from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from zoneinfo import ZoneInfo

from app.backend.db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    transaction_id = Column(String, unique=True, index=True)
    transaction_type = Column(String, index=True)

    account_number = Column(String, index=True, nullable=True)

    sender_account_number = Column(String, index=True, nullable=True)
    receiver_account_number = Column(String, index=True, nullable=True)

    amount = Column(Float)

    balance_after = Column(Float, default=0.0)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(ZoneInfo("Asia/Kolkata")),
        index=True
    )