from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
import random

from app.backend.db import get_db
from app.models.account_request import AccountRequest
from app.models.account import Account

router = APIRouter(prefix="/admin/open-account", tags=["Admin Open Account"])


# =========================================
# 🟢 GET PENDING REQUESTS (FROM MANAGER)
# =========================================
@router.get("/pending/{admin_id}")
def get_admin_requests(admin_id: int, db: Session = Depends(get_db)):

    requests = db.query(AccountRequest).filter(
        AccountRequest.current_stage == "admin"
    ).all()

    return [
        {
            "id": r.id,
            "full_name": r.full_name,
            "mobile": r.mobile,
            "email": r.email,
            "aadhaar": r.aadhaar,
            "pan": r.pan,
            "branch_id": r.branch_id,
            "branch_name": r.branch_name,
            "deposit_amount": r.deposit_amount,
            "employee_status": r.employee_status,
            "manager_status": r.manager_status,
            "admin_status": r.admin_status
        }
        for r in requests
    ]


# =========================================
# 🟢 APPROVE & CREATE ACCOUNT (FINAL STEP)
# =========================================
@router.put("/approve/{app_id}")
def approve_application(app_id: int, db: Session = Depends(get_db)):

    try:

        req = db.query(AccountRequest).filter(
            AccountRequest.id == app_id
        ).first()

        if not req:
            return {
                "success": False,
                "message": "Request not found"
            }

        # ACCOUNT NUMBER
        account_number = "ACC-" + str(random.randint(100000, 999999))

        # USERNAME
        username = req.branch_id

        # CREATE ACCOUNT
        new_account = Account(

            account_number=account_number,

            customer_name=req.full_name,

            email=req.email,

            mobile=req.mobile,

            aadhaar=req.aadhaar,

            pan=req.pan,

            address=req.nominee_address,

            account_type="Savings",

            initial_deposit=req.deposit_amount,

            balance=req.deposit_amount,

            status="ACTIVE",

            branch_id=req.branch_id,

            nominee=req.nominee_name
        )

        db.add(new_account)

        # UPDATE REQUEST
        req.admin_status = "Approved"

        req.status = "approved"

        req.current_stage = "completed"

        req.generated_account_number = account_number

        req.generated_username = username

        db.commit()

        return {
            "success": True,
            "message": "Account Created",
            "account_number": account_number
        }

    except Exception as e:

        db.rollback()

        return {
            "success": False,
            "error": str(e)
        }