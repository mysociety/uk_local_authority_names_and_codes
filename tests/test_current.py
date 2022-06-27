"""
Tests that the current version is correctly excluding all references to the future

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


def test_no_future_start_date():
    df = get_df()
    now = pd.Timestamp(datetime.now())
    assert (pd.to_datetime(df["start-date"]) > now).any() == False  # type: ignore


def test_no_future_end_date():
    df = get_df()
    now = pd.Timestamp(datetime.now())
    assert (pd.to_datetime(df["end-date"]) > now).any() == False  # type: ignore
