from pydantic import BaseModel
from typing import Optional


class AccountCreate(BaseModel):
    customer_name: str
    email: str
    mobile: str
    aadhaar: str
    pan: str
    address: str
    account_type: str
    initial_deposit: float
    branch_id: str
    nominee: Optional[str] = None


class AccountUpdate(BaseModel):
    mobile: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    nominee: Optional[str] = None
    account_type: Optional[str] = None



class AccountOut(BaseModel):
    account_number: str
    customer_name: str
    branch_id: str
    branch_name: Optional[str] = None
    account_type: str
    balance: float
    status: str
    nominee: Optional[str] = None

    class Config:
        from_attributes = True


class AccountSearchOut(BaseModel):
    account_number: str
    customer_name: str
    mobile: str
    branch_id: str
    branch_name: Optional[str] = None
    account_type: str
    balance: float
    status: str

    class Config:
        from_attributes = True

