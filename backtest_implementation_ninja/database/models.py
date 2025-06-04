from sqlalchemy import Column, Integer, String, DateTime, Date
from .database_backtest import Base

class backtest_data(Base):
    __tablename__ = 'backtest_data'
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(50))  # Specify length for VARCHAR
    ver = Column(String(50), nullable=True)  # Specify length for VARCHAR
    interval = Column(String(20))  # Specify length for VARCHAR
    trade_start = Column(Date)
    trade_end = Column(Date)
    datetoday = Column(DateTime)
    decision_boundary = Column(String(255), nullable=True)  # Column for PNG file path or URL
    svm_backtest = Column(String(255), nullable=True)  # Column for CSV file path or URL
    svm_backtest_one = Column(String(255), nullable=True)  # Column for CSV file path or URL
    tradesheet = Column(String(255), nullable=True)  # Column for CSV file path or URL
    statistics = Column(String(255), nullable=True)  # Column for CSV file path or URL