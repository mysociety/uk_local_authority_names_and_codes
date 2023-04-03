"""
Test properties of date and time

"""


from datetime import datetime
from pathlib import Path

import pandas as pd
from typing import Callable


def datetime_valid(dt_str: str):
    if dt_str == "":
        return True
    try:
        datetime.fromisoformat(dt_str)
    except Exception:
        return False
    return True


def test_end_date_before_start(both_dfs: list[pd.DataFrame]):
    for df in both_dfs:
        df = df[~df["start-date"].isna() & ~df["end-date"].isna()]
        assert (df["end-date"] < df["start-date"]).any() == False


def test_end_date_needs_replaced_by(both_dfs: list[pd.DataFrame]):
    for df in both_dfs:
        old_ni = ~df["local-authority-code"].str.contains("NIR", regex=False)
        s = ~df["end-date"].isna() & df["replaced-by"].isna() & old_ni
        assert s.any() == False


def test_start_dates_must_be_valid_dates(both_dfs: list[pd.DataFrame]):
    for df in both_dfs:
        valid_dates = df["start-date"].fillna("").apply(datetime_valid)
        assert (valid_dates == False).any() == False


def test_end_dates_must_be_valid_dates(both_dfs: list[pd.DataFrame]):
    for df in both_dfs:
        valid_dates = df["end-date"].fillna("").apply(datetime_valid)
        assert (valid_dates == False).any() == False
