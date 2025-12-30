# 📊 OHLCV Data Fetching API (FastAPI)

## Project Overview

This project is a FastAPI-based backend service that fetches OHLCV (Open, High, Low, Close, Volume) stock market data from Yahoo Finance and stores it locally using SQLite.

The system is designed to demonstrate:

* Correct async API design
* Safe handling of blocking external I/O
* Idempotent database writes
* Concurrency awareness
* Robust error handling
* Testability and production readiness

---

## Key Features

* Fetch OHLCV data using `yfinance`
* Async FastAPI endpoints
* Blocking external calls isolated via threadpool
* SQLite persistence using async SQLAlchemy
* Database-level duplicate prevention
* Custom exception hierarchy
* Centralized error handling
* Dockerized deployment
* Concurrent load testing support
* Automated test coverage

---

## Tech Stack

* **Language**: Python 3.11
* **Framework**: FastAPI
* **Database**: SQLite (aiosqlite)
* **ORM**: SQLAlchemy (async)
* **External API**: Yahoo Finance (`yfinance`)
* **Testing**: pytest, pytest-asyncio
* **HTTP Client (tests/load)**: httpx
* **Containerization**: Docker

---

## API Endpoints

### Fetch and Store OHLCV Data

**POST** `/api/fetch?ticker=TSLA`

Fetches OHLCV data for the given ticker and stores it locally.

---

### Get Latest Record

**GET** `/api/last`

Returns the most recent OHLCV record.

---

### Get Historical Records

**GET** `/api/history`

Returns all stored OHLCV records.

---

### Health Check

**GET** `/`

Verifies application and database connectivity.

---

## Architecture Summary

![Architecture Diagram](arch_image/architecture.png)

---

## Async & Concurrency Design

`yfinance` is a blocking library. Calling it directly inside async endpoints would block the event loop.

**Solution implemented:**

```python
await run_in_threadpool(fetch_ohlcv, ticker)
```

This ensures:

* Event loop remains responsive
* Multiple requests can be handled concurrently
* Blocking I/O does not degrade API responsiveness

---

## Duplicate Handling (Idempotency)

Duplicates are handled at the database layer.

### Database Constraint

```python
UniqueConstraint("timestamp", "ticker")
```

### Insert Strategy

```python
insert(...).on_conflict_do_nothing()
```

### Result

* Duplicate rows are ignored
* No IntegrityError
* Safe under concurrent fetches
* API is idempotent by design

---

## Error Handling Strategy

Custom exception hierarchy:

* `AppError`
* `DatabaseError`
* `DuplicateDataError`
* `ExternalServiceError`

External API failures return:

**HTTP 502 – Bad Gateway**

This correctly signals an external dependency failure.

---

## Concurrency & Load Testing

A concurrent load test script simulates real-world usage:

* Multiple `/api/fetch` requests
* Mixed read (`/api/last`) and write traffic
* Concurrent tickers

Observed behavior:

* Some requests succeed (`200`)
* Some fail (`502`) due to Yahoo Finance rate limiting
* Database remains consistent
* API remains responsive

---

## Testing

### Test Coverage

* API routes
* Fetcher logic
* Database storage
* Health checks

### Run Tests

```bash
pytest -v
```

All external calls are mocked.
Tests do not rely on network access.

---

## Docker Support

### Build

```bash
docker build -t ohlcv-api .
```

### Run

```bash
docker run -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  ohlcv-api
```

---

## Configuration

```python
FRONTEND_CONNECTION = "https://myfrontend.com"
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
DB_PATH = "data/db.sqlite3"
DEFAULT_INTERVAL = "1m"
```

---

# Extension Questions

## 1. How would this scale to handle 10 tickers concurrently?

The current architecture already supports concurrent requests due to FastAPI’s async design and threadpool isolation for blocking calls.

To scale cleanly:

* Introduce a concurrency limit (semaphore) around Yahoo Finance calls
* Allow request acceptance while throttling outbound fetches

This prevents external API collapse while maintaining responsiveness.

---

## 2. How would you avoid API rate limits?

Yahoo Finance is an unofficial API and rate limits cannot be fully avoided.

Mitigations include:

* Caching recent results (in-memory or Redis)
* Deduplicating in-flight requests
* Enforcing fetch cooldowns per ticker
* Using a paid market data provider in production

Failures are surfaced as HTTP 502.

---

## 3. What’s the first architectural change you’d make for production?

Decouple data fetching from the request lifecycle.

Specifically:

* Move fetch operations to a background worker or queue
* Make `/api/fetch` enqueue jobs instead of fetching synchronously

This improves reliability, latency, and scalability.

---

## 4. What’s a trading-related pitfall of using this setup as-is?

This setup should not be used for live trading decisions.

Pitfalls:

* Yahoo Finance data is delayed and unofficial
* Candles may be incomplete or revised
* No guarantees on timeliness or accuracy
* Concurrent fetches can return inconsistent snapshots

This system is suitable for analysis and research, not execution.

---

## Limitations

* Yahoo Finance is an unofficial data source
* Rate limiting and malformed responses occur under load
* SQLite is single-writer
* No caching layer
* No background job queue

---

## Conclusion

This project demonstrates:

* Correct async system design
* Safe integration with blocking dependencies
* Concurrency-safe persistence
* Real-world error handling
* Practical scalability considerations

The implementation is intentionally simple, technically sound, and production-aware for the assignment scope.
