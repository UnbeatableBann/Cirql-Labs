from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app
from app.models import OHLCV

# Disable TrustedHostMiddleware for tests
app.user_middleware = [
    m for m in app.user_middleware
    if m.cls.__name__ != "TrustedHostMiddleware"
]
app.middleware_stack = app.build_middleware_stack()

client = TestClient(app)


client = TestClient(app)


@patch("app.api.fetch_ohlcv_async", new_callable=AsyncMock)
@patch("app.api.insert_rows", new_callable=AsyncMock)
def test_fetch_endpoint(mock_insert, mock_fetch):
    mock_fetch.return_value = [
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

    response = client.post("/api/fetch?ticker=TSLA")

    assert response.status_code == 200
    assert response.json()["ticker"] == "TSLA"
    assert response.json()["rows_fetched"] == 1

@patch("app.main.check_db_connection", return_value=True)
def test_health_check(mock_check_db_connection):
    response = client.get("/")
    assert response.status_code == 200
    assert "status" in response.json()
