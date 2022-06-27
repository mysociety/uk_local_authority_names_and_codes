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
    valid_mask = (
        df["local-authority-type-name"].isin(["County"]) & df["end-date"].isna()
    )
    valid_authorities = df[valid_mask]["local-authority-code"]
    result = df["county-la"].isin(valid_authorities) | df["county-la"].isna()
    assert ~result.any() == False


@use_both_dfs
def test_combined_refs(df):
    # test all refs to combined authorities are to authorities assigned as combs or strategic
    types = ["Combined authority", "Strategic Regional Authority"]
    valid_mask = df["local-authority-type-name"].isin(types) & df["end-date"].isna()
    valid_authorities = df[valid_mask]["local-authority-code"]
    result = df["combined-authority"].isin(valid_authorities) | df["county-la"].isna()
    assert ~result.any() == False


@use_both_dfs
def test_valid_replaced_by(df):
    """
    Test that all replaced by values are in valid_authorities
    """
    valid_authorities = df["local-authority-code"]
    df["replaced-by"] = df["replaced-by"].dropna()
    assert ~(df["replaced-by"].isin(valid_authorities)).any() == False
