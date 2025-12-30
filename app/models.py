from sqlalchemy import Column, String, Float, Integer
from sqlalchemy.orm import declarative_base


Base = declarative_base()

class OHLCV(Base):
    __tablename__ = "ohlcv"

    timestamp = Column(String, primary_key=True)
    ticker = Column(String, primary_key=True)

    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Integer, nullable=False)
