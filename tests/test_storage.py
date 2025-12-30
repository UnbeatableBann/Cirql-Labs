import pytest
from app.storage import init_db, insert_rows, get_all
from app.models import OHLCV


@pytest.mark.asyncio
async def test_insert_and_get_rows():
    await init_db()

    rows = [
        OHLCV(
            timestamp="2025-01-01T10:00:00",
            ticker="TSLA",
            open=100,
            high=110,
            low=90,
            close=105,
            volume=1000,
        )
    ]

    await insert_rows(rows)
    result = await get_all()

    assert len(result) >= 1
    assert result[0].ticker == "TSLA"
