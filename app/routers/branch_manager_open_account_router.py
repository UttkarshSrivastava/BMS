from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.models.account_request import AccountRequest

router = APIRouter(prefix="/manager/open-account", tags=["Manager Open Account"])


# =========================================
# 🟢 GET REQUESTS (FROM EMPLOYEE STAGE)
# =========================================
@router.get("/pending/{manager_id}")
def get_manager_requests(manager_id: int, db: Session = Depends(get_db)):

    requests = db.query(AccountRequest).filter(
        AccountRequest.current_stage == "manager"
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
            "employee_status": r.employee_status,
            "manager_status": r.manager_status
        }
        for r in requests
    ]


# =========================================
# 🟡 FORWARD TO ADMIN
# =========================================
@router.put("/forward/{app_id}")
def forward_to_admin(app_id: int, remark: str = Query(None), db: Session = Depends(get_db)):

    req = db.query(AccountRequest).filter(AccountRequest.id == app_id).first()

    if not req:
        return {"success": False, "message": "Not found"}

    req.manager_status = "Forwarded"
    req.manager_remark = remark

    req.current_stage = "admin"
    req.status = "forwarded_admin"

    db.commit()

    return {"success": True, "message": "Forwarded to Admin"}


# =========================================
# 🔴 REJECT BY MANAGER
# =========================================
@router.put("/reject/{app_id}")
def reject_request(app_id: int, remark: str = Query(None), db: Session = Depends(get_db)):

    req = db.query(AccountRequest).filter(AccountRequest.id == app_id).first()

    if not req:
        return {"success": False, "message": "Not found"}

    req.manager_status = "Rejected"
    req.manager_remark = remark

    req.current_stage = "rejected"
    req.status = "rejected"

    db.commit()

    return {"success": True, "message": "Rejected by Manager"}