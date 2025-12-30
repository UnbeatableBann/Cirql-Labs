from fastapi import APIRouter, HTTPException, Query
from app.fetcher import fetch_ohlcv_async
from app.storage import insert_rows, get_last, get_all
from app.logger import loggers

router = APIRouter()

@router.post("/fetch")
async def fetch_data(ticker: str = Query(..., min_length=1, examples=["TSLA"])):
    """
    Fetch OHLCV data for a ticker and store it locally.
    """
    try:
        loggers.fastapi.info(f"Fetching OHLCV data for ticker: {ticker.upper()}")
        rows = await fetch_ohlcv_async(ticker.upper())
        await insert_rows(rows)
        loggers.fastapi.info(f"Successfully fetched and stored {len(rows)} rows for {ticker.upper()}")
        return {
            "status": "success",
            "ticker": ticker.upper(),
            "rows_fetched": len(rows)
        }
    except ValueError as e:
        loggers.fastapi.error(f"Invalid ticker or data error for {ticker.upper()}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        loggers.fastapi.error(f"Unexpected error fetching data for {ticker.upper()}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/last")
async def get_latest():
    """
    Return the latest stored OHLCV record.
    """
    try:
        row = await get_last()
        if not row:
            return {}

        return {
            "timestamp": row.timestamp,
            "ticker": row.ticker,
            "open": row.open,
            "high": row.high,
            "low": row.low,
            "close": row.close,
            "volume": row.volume
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history")
async def get_history():
    """
    Return all stored OHLCV records.
    """
    try:
        rows = await get_all()
        return [
            {
                "timestamp": r.timestamp,
                "ticker": r.ticker,
                "open": r.open,
                "high": r.high,
                "low": r.low,
                "close": r.close,
                "volume": r.volume
            }
            for r in rows
        ]

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))