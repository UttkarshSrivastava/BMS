from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from app.backend.db import Base


class LoanRequest(Base):

    __tablename__ = "loan_requests"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =========================
    # CUSTOMER DETAILS
    # =========================

    account_number = Column(String)

    customer_name = Column(String)

    branch_id = Column(String)

    # =========================
    # LOAN DETAILS
    # =========================

    loan_type = Column(String)

    loan_amount = Column(Float)

    duration_months = Column(Integer)

    interest_rate = Column(Float)

    monthly_emi = Column(Float)

    # =========================
    # STATUS FLOW
    # =========================

    employee_status = Column(String)

    manager_status = Column(String)

    admin_status = Column(String)

    overall_status = Column(String)

    # =========================
    # EMI TRACKING
    # =========================

    total_paid_emi = Column(
        Integer,
        default=0
    )

    remaining_emi = Column(Integer)

    remaining_amount = Column(Float)

    # =========================
    # APPROVAL DETAILS
    # =========================

    approved_date = Column(DateTime)

    rejection_reason = Column(String)

    # =========================
    # CREATED DATE
    # =========================

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )