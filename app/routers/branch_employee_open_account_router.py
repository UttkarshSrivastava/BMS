from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.models.account_request import AccountRequest

router = APIRouter(prefix="/employee/open-account", tags=["Employee Open Account"])


# =========================================
# 🟢 GET PENDING REQUESTS (BRANCH WISE)
# =========================================
@router.get("/pending/{employee_id}")
def get_pending_requests(employee_id: int, db: Session = Depends(get_db)):

    # ⚠️ IMPORTANT:
    # abhi employee_id use nahi ho raha properly
    # best practice: employee se branch_id fetch karo

    requests = db.query(AccountRequest).filter(
        AccountRequest.current_stage == "employee"
    ).all()

    return [
        {
            "id": r.id,
            "full_name": r.full_name,
            "mobile": r.mobile,
            "email": r.email,
            "aadhaar": r.aadhaar,
            "pan": r.pan,
            "branch_name": r.branch_name,
            "deposit_amount": r.deposit_amount,
            "payment_mode": r.payment_mode,
            "nominee_name": r.nominee_name,
            "employee_status": r.employee_status,
            "created_at": r.id  # (agar date column nahi hai to id fallback)
        }
        for r in requests
    ]


# =========================================
# 🟡 APPROVE REQUEST (SEND TO MANAGER)
# =========================================
@router.put("/approve/{app_id}")
def approve_request(app_id: int, db: Session = Depends(get_db)):

    req = db.query(AccountRequest).filter(AccountRequest.id == app_id).first()

    if not req:
        return {"success": False, "message": "Application not found"}

    req.employee_status = "Approved"
    req.current_stage = "manager"
    req.status = "forwarded_manager"

    db.commit()

    return {
        "success": True,
        "message": "Request approved and sent to Manager"
    }


# =========================================
# 🔴 REJECT REQUEST
# =========================================
@router.put("/reject/{app_id}")
def reject_request(app_id: int, db: Session = Depends(get_db)):

    req = db.query(AccountRequest).filter(AccountRequest.id == app_id).first()

    if not req:
        return {"success": False, "message": "Application not found"}

    req.employee_status = "Rejected"
    req.current_stage = "rejected"
    req.status = "rejected"

    db.commit()

    return {
        "success": True,
        "message": "Request rejected successfully"
    }