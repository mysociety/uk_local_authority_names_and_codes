"""
Test required columns are present and are not duplicated

"""


from datetime import datetime
from pathlib import Path

import pandas as pd


def get_df() -> pd.DataFrame:
    return pd.read_csv(Path("data", "uk_local_authorities.csv"))


def test_no_duplicate_local_authority_code():
    df = get_df()
    assert df["local-authority-code"].duplicated().any() == False


def test_no_duplicate_official_name_code():
    df = get_df()
    assert df["official-name"].duplicated().any() == False


def test_no_duplicate_gss_code():
    df = get_df()
    assert df["gss-code"].duplicated().any() == False


def test_must_have_offical_name():
    df = get_df()
    assert df["official-name"].isna().any() == False


def test_must_have_region():
    df = get_df()
    assert df["region"].isna().any() == False


def test_must_have_nation():
    df = get_df()
    assert df["nation"].isna().any() == False


def test_must_have_type():
    df = get_df()
    assert df["region"].isna().any() == False
