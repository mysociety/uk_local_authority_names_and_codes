from datetime import datetime
from pathlib import Path
from typing import Callable

import pandas as pd
import pytest

top_level = Path(__file__).parent.parent
current_package = top_level / "data" / "packages" / "uk_la_past_current"
future_package = top_level / "data" / "packages" / "uk_la_future"


def get_la_df(future=False) -> pd.DataFrame:
    if future:
        return pd.read_csv(
            Path(future_package, "uk_local_authorities_future.csv"),
        )
    else:
        return pd.read_csv(
            Path(current_package, "uk_local_authorities_current.csv"),
        )


@pytest.fixture(name="df")
def current_df():
    return get_la_df()


@pytest.fixture()
def future_df():
    return get_la_df()


@pytest.fixture()
def both_dfs():
    return [get_la_df(), get_la_df(future=True)]
