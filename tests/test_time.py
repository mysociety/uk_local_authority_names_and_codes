"""
Test properties of date and time

"""


from datetime import datetime
from pathlib import Path

import pandas as pd
from typing import Callable


top_level = Path(__file__).parent.parent
current_package = top_level / "data" / "packages" / "uk_la_past_current"
future_package = top_level / "data" / "packages" / "uk_la_future"


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


def get_df(future=False) -> pd.DataFrame:
    if future:
        return pd.read_csv(
            Path(future_package, "uk_local_authorities_future.csv"),
        )
    else:
        return pd.read_csv(
            Path(current_package, "uk_local_authorities_current.csv"),
        )


def datetime_valid(dt_str):
    if dt_str == "":
        return True
    try:
        datetime.fromisoformat(dt_str)
    except Exception:
        return False
    return True


@use_both_dfs
def test_end_date_before_start(df: pd.DataFrame):
    df = df[~df["start-date"].isna() & ~df["end-date"].isna()]
    assert (df["end-date"] < df["start-date"]).any() == False


@use_both_dfs
def test_end_date_needs_replaced_by(df: pd.DataFrame):
    old_ni = ~df["local-authority-code"].str.contains("NIR", regex=False)
    s = ~df["end-date"].isna() & df["replaced-by"].isna() & old_ni
    assert s.any() == False


@use_both_dfs
def test_start_dates_must_be_valid_dates(df: pd.DataFrame):
    valid_dates = df["start-date"].fillna("").apply(datetime_valid)
    assert (valid_dates == False).any() == False


@use_both_dfs
def test_end_dates_must_be_valid_dates(df: pd.DataFrame):
    valid_dates = df["end-date"].fillna("").apply(datetime_valid)
    assert (valid_dates == False).any() == False
