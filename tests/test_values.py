"""
Tests of if values are correct and make sense
"""

from datetime import datetime
from pathlib import Path

import pandas as pd


def get_df() -> pd.DataFrame:
    return pd.read_csv(Path("data", "uk_local_authorities.csv"))


def test_valid_authority_type():

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

    df = get_df()
    assert (~df["local-authority-type-name"].isin(allowed_types)).any() == False


def test_valid_region():

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

    df = get_df()
    df = df[df["current-authority"]]
    assert (~df["region"].isin(allowed_types)).any() == False


def test_valid_codes():
    def valid_code(s):
        return s == s.upper()[:4]

    df = get_df()
    assert ~(df["local-authority-code"].apply(valid_code)).any() == False


def test_counties():
    # test all refs to counties are to authorities assigned as countries
    df = get_df()
    valid_mask = df["local-authority-type-name"].isin(
        ["County"]) & df["end-date"].isna()
    valid_authorities = (df[valid_mask]["local-authority-code"])
    result = df["county-la"].isin(valid_authorities) | df["county-la"].isna()
    assert ~result.any() == False


def test_combined_refs():
    # test all refs to combined authorities are to authorities assigned as combs or strategic
    df = get_df()
    types = ["Combined authority", "Strategic Regional Authority"]
    valid_mask = df["local-authority-type-name"].isin(
        types) & df["end-date"].isna()
    valid_authorities = (df[valid_mask]["local-authority-code"])
    result = df["combined-authority"].isin(
        valid_authorities) | df["county-la"].isna()
    assert ~result.any() == False
