from sqlalchemy import Column, Integer, String, DateTime, Float
from datetime import datetime
from app.backend.db import Base


class AccountRequest(Base):
    __tablename__ = "account_requests"

    id = Column(Integer, primary_key=True, index=True)

    # branch info
    branch_id = Column(String)
    branch_name = Column(String)

    # customer details
    full_name = Column(String)
    father_name = Column(String)
    mobile = Column(String)
    email = Column(String)
    aadhaar = Column(String)
    pan = Column(String)

    # nominee
    nominee_name = Column(String)
    nominee_relation = Column(String)
    nominee_mobile = Column(String)
    nominee_address = Column(String)

    # deposit
    deposit_amount = Column(Float)
    payment_mode = Column(String)

    # workflow status
    employee_status = Column(String, default="Pending")
    manager_status = Column(String, default="Waiting")
    admin_status = Column(String, default="Waiting")

    status = Column(String, default="pending_employee")
    current_stage = Column(String, default="employee")

    # final output
    generated_account_number = Column(String, nullable=True)
    generated_username = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)