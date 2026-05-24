from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.backend.db import get_db
from app.models.card_request_model import CardRequest
from app.models.employee import Employee

from app.auth.auth_handler import verify_token
from fastapi import Header


router = APIRouter(prefix="/employee/card-requests", tags=["Employee Card Requests"])


def get_current_employee(authorization: str = Header(None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    token = authorization.replace("Bearer ", "").strip()
    payload = verify_token(token)

    employee_id = payload.get("employee_id") or payload.get("sub")
    if not employee_id:
        raise HTTPException(status_code=401, detail="Token has no employee_id")

    employee = db.query(Employee).filter(Employee.employee_id == str(employee_id)).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee


@router.get("/dashboard")
def employee_card_requests_dashboard(
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee)
):
    # Employee should see only requests for his/her branch
    reqs = (
        db.query(CardRequest)
        .filter(CardRequest.branch_id == employee.branch_id)
        .order_by(CardRequest.created_at.desc())
        .all()
    )

    def doc_or_dash(val):
        return val if val else "-"

    formatted = []
    for r in reqs:
        formatted.append({
            "request_id": r.id,
            "card_type": r.card_type,
            "network": r.network,
            "card_variant": r.card_variant,
            "credit_limit": r.credit_limit,
            "address": r.address,
            "city": r.city,
            "pincode": r.pincode,

            "status": r.status,
            "employee_status": r.employee_status,
            "manager_status": r.manager_status,

            "aadhaar_document": doc_or_dash(r.aadhaar_document),
            "pan_document": doc_or_dash(r.pan_document),
            "income_proof": doc_or_dash(r.income_proof),
            "photo": doc_or_dash(r.photo),

            "created_at": r.created_at,
        })

    # Counting based on option C: count `status` (approved/rejected)
    approved_count = sum(1 for r in reqs if (r.status or "").lower() == "approved")
    rejected_count = sum(1 for r in reqs if (r.status or "").lower() == "rejected")

    return {
        "success": True,
        "branch_id": employee.branch_id,
        "cards_summary": {
            "total": len(reqs),
            "approved": approved_count,
            "rejected": rejected_count
        },
        "requests": formatted
    }


@router.put("/forward/{request_id}")
def employee_forward_to_manager(
    request_id: int,
    remark: str = Query(None),
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee)
):
    req = (
        db.query(CardRequest)
        .filter(
            CardRequest.id == request_id,
            CardRequest.branch_id == employee.branch_id
        )
        .first()
    )
    if not req:
        raise HTTPException(status_code=404, detail="Card request not found")

    # Strings confirmed by user:
    # employee_status = Forwarded
    # status = pending_manager
    req.employee_forwarded_at = datetime.utcnow()
    req.employee_status = "Forwarded"
    req.status = "pending_manager"
    req.manager_status = "Pending"


    # user said manager status change no (already handled by not setting it)
    db.commit()
    db.refresh(req)

    return {
        "success": True,
        "message": "Forwarded by Employee",
        "request_id": req.id
    }
