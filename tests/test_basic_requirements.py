"""
Test required columns are present and are not duplicated

"""


from datetime import datetime
from pathlib import Path
from typing import Callable

import pandas as pd
import pytest

top_level = Path(__file__).parent.parent
current_package = top_level / "data" / "packages" / "uk_la_past_current"
future_package = top_level / "data" / "packages" / "uk_la_future"


def test_no_duplicate_local_authority_code(both_dfs):
    for df in both_dfs:
        assert df["local-authority-code"].duplicated().any() == False


def test_no_duplicate_official_name_code(both_dfs):
    for df in both_dfs:
        assert df["official-name"].duplicated().any() == False


def test_no_duplicate_gss_code(both_dfs):
    # allow na for future
    for df in both_dfs:
        assert df["gss-code"].dropna().duplicated().any() == False


def test_must_have_offical_name(both_dfs):
    for df in both_dfs:
        assert df["official-name"].isna().any() == False


def test_must_have_region(both_dfs):
    for df in both_dfs:
        df = df[df["current-authority"]]
        assert df["region"].isna().any() == False


def test_must_have_nation(both_dfs):
    for df in both_dfs:
        assert df["nation"].isna().any() == False


def test_must_have_type(both_dfs):
    for df in both_dfs:
        assert df["local-authority-type"].isna().any() == False


def test_no_duplicate_gss_code_no_na(df):
    """
    No NA for gss code in current dataset.
    """
    # exclude anything with an end date because some past stuff doesn't have gss codes
    df = df[df["end-date"].isna()]
    assert df["gss-code"].duplicated().any() == False, "NAs in current dataset"
