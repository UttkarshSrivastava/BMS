from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class TransactionOut(BaseModel):
    transaction_id: str
    transaction_type: str
    account_number: Optional[str] = None
    sender_account_number: Optional[str] = None
    receiver_account_number: Optional[str] = None
    amount: float
    balance_after: float
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

