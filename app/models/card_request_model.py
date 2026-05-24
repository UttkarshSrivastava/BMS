# app/models/card_request_model.py

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func

from app.backend.db import Base


class CardRequest(Base):

    __tablename__ = "card_requests"

    id = Column(Integer, primary_key=True, index=True)

    # USER DETAILS

    user_id = Column(Integer, ForeignKey("signup_users.id"))
    branch_id = Column(Integer)

    full_name = Column(String, nullable=False)
    account_number = Column(String, nullable=False)
    mobile = Column(String, nullable=False)
    email = Column(String, nullable=False)

    # CARD DETAILS

    card_type = Column(String, nullable=False)
    network = Column(String, nullable=False)
    card_variant = Column(String, nullable=False)
    credit_limit = Column(String, nullable=True)

    # DELIVERY DETAILS

    address = Column(Text, nullable=False)
    city = Column(String, nullable=False)
    pincode = Column(String, nullable=False)

    # DOCUMENTS

    aadhaar_document = Column(String, nullable=True)
    pan_document = Column(String, nullable=True)
    income_proof = Column(String, nullable=True)
    photo = Column(String, nullable=True)

    # STATUS FLOW

    status = Column(
        String,
        default="Pending At Employee"
    )

    employee_status = Column(
        String,
        default="Pending"
    )

    manager_status = Column(
        String,
        default="Pending"
    )

    admin_status = Column(
        String,
        default="Pending"
    )

    # TRACKING

    employee_forwarded_at = Column(DateTime, nullable=True)
    manager_forwarded_at = Column(DateTime, nullable=True)
    admin_approved_at = Column(DateTime, nullable=True)

    # CREATED TIME

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )



