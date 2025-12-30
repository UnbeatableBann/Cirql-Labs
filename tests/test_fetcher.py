import pandas as pd
from unittest.mock import patch
from app.fetcher import fetch_ohlcv
from app.models import OHLCV


@patch("yfinance.download")
def test_fetch_ohlcv_success(mock_download):
    data = {
        ("Open", "TSLA"): [100.0],
        ("High", "TSLA"): [110.0],
        ("Low", "TSLA"): [95.0],
        ("Close", "TSLA"): [105.0],
        ("Volume", "TSLA"): [1000],
    }

    df = pd.DataFrame(
        data,
        index=pd.to_datetime(["2025-01-01 10:00:00"])
    )

    mock_download.return_value = df

    rows = fetch_ohlcv("TSLA")

    assert isinstance(rows, list)
    assert len(rows) == 1
    assert isinstance(rows[0], OHLCV)
    assert rows[0].ticker == "TSLA"
    assert rows[0].open == 100.0
