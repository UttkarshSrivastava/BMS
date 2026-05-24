from sqlalchemy import Column, Integer, String, Float
from app.backend.db import Base


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)

    # Example: ACC-483920
    account_number = Column(String, unique=True, index=True)

    customer_name = Column(String)
    email = Column(String)
    mobile = Column(String)
    aadhaar = Column(String)
    pan = Column(String)
    address = Column(String)

    account_type = Column(String)
    initial_deposit = Column(Float, default=0.0)
    balance = Column(Float, default=0.0)

    # ACTIVE / FROZEN / CLOSED
    status = Column(String, default="ACTIVE", index=True)

    # Must reference existing branches.branch_id (string)
    branch_id = Column(String, index=True)

    nominee = Column(String, nullable=True)

