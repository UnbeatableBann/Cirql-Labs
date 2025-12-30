from fastapi.concurrency import run_in_threadpool
import yfinance as yf

from app.models import OHLCV
from app.config import settings
from app.exceptions import ExternalServiceError


def fetch_ohlcv(ticker: str, interval: str = settings.DEFAULT_INTERVAL) -> list[OHLCV]:
    try:
        df = yf.download(
            ticker,
            period="5d",
            interval=interval,
            progress=False,
            threads=False,
        )

        if df is None or df.empty:
            raise ExternalServiceError(
                f"No data returned from Yahoo Finance for ticker '{ticker}'"
            )

        try:
            df.columns = df.columns.droplevel(1)
        except Exception:
            pass

        df = df.reset_index()

        ts_col = "Datetime" if "Datetime" in df.columns else df.columns[0]

        rows: list[OHLCV] = []
        for _, row in df.iterrows():
            rows.append(
                OHLCV(
                    timestamp=str(row[ts_col]),
                    ticker=ticker,
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=int(row["Volume"]),
                )
            )

        return rows

    except ExternalServiceError as e:
        print("Yahoo failure:", e)
        raise
    except Exception as e:
        raise ExternalServiceError(
            f"Yahoo Finance fetch failed for ticker '{ticker}': {e}"
        )


async def fetch_ohlcv_async(ticker: str) -> list[OHLCV]:
    """
    Async wrapper for fetch_ohlcv to be used inside FastAPI endpoints.
    """
    return await run_in_threadpool(fetch_ohlcv, ticker)
