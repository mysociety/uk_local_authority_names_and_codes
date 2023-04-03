"""
Tests that the current version is correctly excluding all references to the future

"""


from datetime import datetime
from pathlib import Path

import pandas as pd
import pytest


def test_no_future_start_date(df):
    now = pd.Timestamp(datetime.now())
    assert (pd.to_datetime(df["start-date"]) > now).any() == False  # type: ignore


def test_no_future_end_date(df):
    now = pd.Timestamp(datetime.now())
    assert (pd.to_datetime(df["end-date"]) > now).any() == False  # type: ignore


def test_must_have_type(df):
    assert df["local-authority-type"].isna().any() == False
