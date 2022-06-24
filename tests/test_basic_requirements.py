"""
Test required columns are present and are not duplicated

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
def test_no_duplicate_local_authority_code(df):
    assert df["local-authority-code"].duplicated().any() == False


@use_both_dfs
def test_no_duplicate_official_name_code(df):
    assert df["official-name"].duplicated().any() == False


@use_both_dfs
def test_no_duplicate_gss_code(df):
    # allow na for future
    assert df["gss-code"].dropna().duplicated().any() == False


def test_no_duplicate_gss_code_no_na():
    """
    No NA for gss code in current dataset.
    """
    df = get_df()

    # exclude anything with an end date because some past stuff doesn't have gss codes
    df = df[df["end-date"].isna()]
    assert df["gss-code"].duplicated().any() == False


@use_both_dfs
def test_must_have_offical_name(df):
    assert df["official-name"].isna().any() == False


@use_both_dfs
def test_must_have_region(df):
    df = df[df["current-authority"]]
    assert df["region"].isna().any() == False


@use_both_dfs
def test_must_have_nation(df):
    assert df["nation"].isna().any() == False


@use_both_dfs
def test_must_have_type(df):
    assert df["local-authority-type"].isna().any() == False
