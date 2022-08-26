"""
Tests of if values are correct and make sense
"""

from datetime import datetime
from pathlib import Path

import pandas as pd
from typing import Callable

top_level = Path(__file__).parent.parent
current_package = top_level / "data" / "packages" / "uk_la_past_current"
future_package = top_level / "data" / "packages" / "uk_la_future"


def get_df(future=False) -> pd.DataFrame:
    if future:
        return pd.read_csv(
            Path(future_package, "uk_local_authorities_future.csv"),
        )
    else:
        return pd.read_csv(
            Path(current_package, "uk_local_authorities_current.csv"),
        )


def use_both_dfs(function: Callable):
    """
    Decorator to use both current and future dfs
    """

    def wrapper(*args, **kwargs):
        df = get_df()
        function(df, *args, **kwargs)
        df = get_df(future=True)
        function(df, *args, **kwargs)

    return wrapper


@use_both_dfs
def test_valid_authority_type(df):

    allowed_types = [
        "NI district",
        "Scottish unitary authority",
        "Non-metropolitan district",
        "Welsh unitary authority",
        "Unitary authority",
        "London borough",
        "Metropolitan district",
        "County",
        "Strategic Regional Authority",
        "Combined authority",
        "City corporation",
    ]

    assert (~df["local-authority-type-name"].isin(allowed_types)).any() == False


@use_both_dfs
def test_valid_region(df):

    allowed_types = [
        "Northern Ireland",
        "Scotland",
        "South East",
        "Wales",
        "North West",
        "East Midlands",
        "East of England",
        "South West",
        "London",
        "West Midlands",
        "Yorkshire and The Humber",
        "North East",
    ]
    df = df[df["current-authority"]]
    assert (~df["region"].isin(allowed_types)).any() == False


@use_both_dfs
def test_valid_codes(df):
    def valid_code(s):
        return s == s.upper()[:4]

    assert ~(df["local-authority-code"].apply(valid_code)).any() == False


@use_both_dfs
def test_counties(df):
    # test all refs to counties are to authorities assigned as countries
    id_type_lookup = df[
        ["local-authority-code", "official-name", "local-authority-type-name"]
    ]
    id_type_lookup.columns = ["county-la", "county-name", "county-type"]

    ndf = df.merge(id_type_lookup)
    ndf["county-type"] = ndf["county-type"].fillna("")
    ndf = ndf[~ndf["county-type"].isin(["County", ""])]
    assert len(ndf) == 0


@use_both_dfs
def test_combined_refs(df):
    # test all refs to combined authorities are to authorities assigned as combs or strategic
    id_type_lookup = df[
        ["local-authority-code", "official-name", "local-authority-type-name"]
    ]
    id_type_lookup.columns = ["combined-authority", "county-name", "county-type"]

    ndf = df.merge(id_type_lookup)
    ndf["county-type"] = ndf["county-type"].fillna("")
    ndf = ndf[
        ~ndf["county-type"].isin(
            ["Combined authority", "Strategic Regional Authority", ""]
        )
    ]
    assert len(ndf) == 0


@use_both_dfs
def test_county_lookup_matches_reference(df):
    gss_lookup = pd.read_csv(current_package / "lookup_gss_to_registry.csv")
    lookup = gss_lookup.set_index("gss-code")["local-authority-code"].to_dict()
    gss_lookup = pd.read_csv(current_package / "lookup_gss_to_registry.csv")
    lookup = gss_lookup.set_index("gss-code")["local-authority-code"].to_dict()
    tier_lookup = pd.read_csv(
        Path(
            "data",
            "validation",
            "Local_Authority_District_to_County_(April_2021)_Lookup_in_England.csv",
        )
    )[["LAD21CD", "CTY21CD"]]
    tier_lookup.columns = ["lad", "county"]
    tier_lookup["local-authority-code"] = tier_lookup.lad.map(lookup)
    tier_lookup["validated-county-id"] = tier_lookup.county.map(lookup)
    tier_lookup[~tier_lookup["validated-county-id"].isna()]
    tier_lookup = tier_lookup[["local-authority-code", "validated-county-id"]]
    d = df.merge(tier_lookup, on="local-authority-code")[
        ["local-authority-code", "official-name", "county-la", "validated-county-id"]
    ]
    d = d[d["county-la"] != d["validated-county-id"]]
    d = d[~d["validated-county-id"].isna()]
    assert len(d) == 0


@use_both_dfs
def test_nmd_all_have_counties(df):
    df = df[(df["local-authority-type"] == "NMD") & df["county-la"].isna()]
    assert len(df) == 0


@use_both_dfs
def test_valid_replaced_by(df):
    """
    Test that all replaced by values are in valid_authorities
    """
    valid_authorities = df["local-authority-code"]
    df["replaced-by"] = df["replaced-by"].dropna()
    assert ~(df["replaced-by"].isin(valid_authorities)).any() == False
