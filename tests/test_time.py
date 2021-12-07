"""
Test properties of date and time

"""


from datetime import datetime
from pathlib import Path

import pandas as pd


def get_df() -> pd.DataFrame:
    return pd.read_csv(Path("data", "uk_local_authorities.csv"))


def datetime_valid(dt_str):
    if dt_str == "":
        return True
    try:
        datetime.fromisoformat(dt_str)
    except Exception:
        return False
    return True


def test_end_date_before_start():
    df = get_df()
    df = df[~df["start-date"].isna() & ~df["end-date"].isna()]
    assert (df["end-date"] < df["start-date"]).any() == False


def test_end_date_needs_replaced_by():
    df = get_df()
    s = ~df["end-date"].isna() & df["replaced-by"].isna()
    assert s.any() == False


def test_start_dates_must_be_valid_dates():
    df = get_df()
    valid_dates = df["start-date"].fillna("").apply(datetime_valid)
    assert (valid_dates == False).any() == False


def test_end_dates_must_be_valid_dates():
    df = get_df()
    valid_dates = df["end-date"].fillna("").apply(datetime_valid)
    assert (valid_dates == False).any() == False
