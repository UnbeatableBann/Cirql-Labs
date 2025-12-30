from sqlite3 import IntegrityError

from sqlalchemy import select, text
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import settings
from app.exceptions import DatabaseError, DuplicateDataError
from app.models import OHLCV, Base

DATABASE_URL = f"sqlite+aiosqlite:///{settings.DB_PATH}"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ─────────────────────────────
# Health check
# ─────────────────────────────
async def check_db_connection() -> bool:
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False


# ─────────────────────────────
# DB init
# ─────────────────────────────
async def init_db() -> None:
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except SQLAlchemyError as e:
        raise DatabaseError(f"Database initialization failed: {e}")


# ─────────────────────────────
# Insert data
# ─────────────────────────────
async def insert_rows(rows: list[OHLCV]) -> None:
    try:
        async with AsyncSessionLocal() as session:
            async with session.begin():
                for row in rows:
                    stmt = (
                        insert(OHLCV)
                        .values(
                            timestamp=row.timestamp,
                            ticker=row.ticker,
                            open=row.open,
                            high=row.high,
                            low=row.low,
                            close=row.close,
                            volume=row.volume,
                        )
                        .on_conflict_do_nothing(
                            index_elements=["timestamp", "ticker"]
                        )
                    )
                    await session.execute(stmt)
    except IntegrityError as e:
        raise DuplicateDataError(f"Duplicate OHLCV data: {e}")
    except SQLAlchemyError as e:
        raise DatabaseError(f"Database insert failed: {e}")


# ─────────────────────────────
# Queries
# ─────────────────────────────
async def get_last() -> OHLCV | None:
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(OHLCV)
                .order_by(OHLCV.timestamp.desc())
                .limit(1)
            )
            return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        raise DatabaseError(f"Failed to fetch latest record: {e}")



async def get_all() -> list[OHLCV]:
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(select(OHLCV))
            return result.scalars().all()
    except SQLAlchemyError as e:
        raise DatabaseError(f"Failed to fetch records: {e}")

