import asyncio
import httpx

BASE_URL = "http://localhost:8000"
FETCH_URL = f"{BASE_URL}/api/fetch"
LAST_URL = f"{BASE_URL}/api/last"

TICKERS = ["TSLA", "AAPL"] * 3  # 3× load


async def send_fetch(client, ticker):
    r = await client.post(FETCH_URL, params={"ticker": ticker})
    return f"fetch:{ticker}", r.status_code


async def send_last(client):
    r = await client.get(LAST_URL)
    return "last", r.status_code


async def main():
    async with httpx.AsyncClient(timeout=60) as client:
        tasks = []

        # Concurrent fetch requests
        for ticker in TICKERS:
            tasks.append(send_fetch(client, ticker))

        # Concurrent last reads (simulate dashboard reads)
        for _ in range(3):
            tasks.append(send_last(client))

        results = await asyncio.gather(*tasks)

    for label, status in results:
        print(label, status)


if __name__ == "__main__":
    asyncio.run(main())
