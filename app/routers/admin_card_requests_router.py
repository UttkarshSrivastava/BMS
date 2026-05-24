from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.backend.db import get_db
from app.models.card_request_model import CardRequest
from app.models.employee import Employee

from app.auth.auth_handler import verify_token
from fastapi import Header

router = APIRouter(prefix="/admin", tags=["Admin Card Requests"])


def get_current_admin(authorization: str = Header(None), db: Session = Depends(get_db)) -> Employee:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization missing")

    try:
        token = authorization.replace("Bearer ", "").strip()
        payload = verify_token(token)

        employee_id = payload.get("employee_id") or payload.get("employeeId") or payload.get("id") or payload.get("sub")
        if not employee_id:
            raise HTTPException(status_code=401, detail="Employee ID missing in token")

        admin = db.query(Employee).filter(Employee.employee_id == str(employee_id)).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")

        return admin

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/card-requests/pending")
def get_pending_card_requests(
    db: Session = Depends(get_db),
    admin: Employee = Depends(get_current_admin)
):
    try:
        reqs = (
            db.query(CardRequest)
            .filter(CardRequest.employee_status == "Forwarded")
            .filter(CardRequest.status == "pending_admin")
            .order_by(CardRequest.created_at.desc())
            .all()
        )

        return {
            "success": True,
            "requests": [
                {
                    "request_id": r.id,
                    "full_name": r.full_name,
                    "account_number": r.account_number,
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
                    "admin_status": r.admin_status,
                    "aadhaar_document": r.aadhaar_document,
                    "pan_document": r.pan_document,
                    "income_proof": r.income_proof,
                    "photo": r.photo,
                    "created_at": r.created_at,
                }
                for r in reqs
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/card-requests/approve/{request_id}")
def approve_card_request(
    request_id: int,
    db: Session = Depends(get_db),
    admin: Employee = Depends(get_current_admin)
):
    try:
        req = db.query(CardRequest).filter(CardRequest.id == request_id).first()
        if not req:
            raise HTTPException(status_code=404, detail="Card request not found")

        req.admin_status = "Approved"
        req.admin_approved_at = datetime.utcnow()
        req.status = "approved"

        db.commit()
        db.refresh(req)

        return {"success": True, "message": "Card request approved", "request_id": req.id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/card-requests/reject/{request_id}")
def reject_card_request(
    request_id: int,
    db: Session = Depends(get_db),
    admin: Employee = Depends(get_current_admin)
):
    try:
        req = db.query(CardRequest).filter(CardRequest.id == request_id).first()
        if not req:
            raise HTTPException(status_code=404, detail="Card request not found")

        req.admin_status = "Rejected"
        req.status = "rejected"

        db.commit()
        db.refresh(req)

        return {"success": True, "message": "Card request rejected", "request_id": req.id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

