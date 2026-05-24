from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime

from app.backend.db import get_db
from app.models.card_request_model import CardRequest
from app.models.employee import Employee

from app.auth.auth_handler import verify_token

router = APIRouter(prefix="/branch-manager", tags=["Branch Manager Card Requests"])


def get_current_manager(authorization: str = Header(None), db: Session = Depends(get_db)) -> Employee:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization missing")

    try:
        token = authorization.replace("Bearer ", "").strip()
        payload = verify_token(token)

        employee_id = (
            payload.get("employee_id")
            or payload.get("employeeId")
            or payload.get("id")
            or payload.get("sub")
        )

        if not employee_id:
            raise HTTPException(status_code=401, detail="Employee ID missing in token")

        manager = db.query(Employee).filter(Employee.employee_id == str(employee_id)).first()
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")

        return manager

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/card-requests/dashboard")
def manager_card_requests_dashboard(
    db: Session = Depends(get_db),
    manager: Employee = Depends(get_current_manager),
):
    try:
        branch_id = manager.branch_id

        reqs = (
            db.query(CardRequest)
            .filter(CardRequest.branch_id == branch_id)
            .filter(CardRequest.employee_status == "Forwarded")
            .filter(CardRequest.status == "pending_manager")
            .order_by(CardRequest.created_at.desc())
            .all()
        )

        def doc_or_dash(val: str | None):
            return val if val else "-"

        formatted = []
        for r in reqs:
            formatted.append(
                {
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
                    "admin_status": r.admin_status,

                    "full_name": r.full_name,
                    "account_number": r.account_number,

                    "aadhaar_document": doc_or_dash(r.aadhaar_document),
                    "pan_document": doc_or_dash(r.pan_document),
                    "income_proof": doc_or_dash(r.income_proof),
                    "photo": doc_or_dash(r.photo),

                    "created_at": r.created_at,
                }
            )

        return {
            "success": True,
            "branch_id": branch_id,
            "cards_summary": {
                "total": len(reqs),
                "approved": 0,
                "rejected": 0,
            },
            "requests": formatted,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/card-requests/forward/{request_id}")
def forward_card_request_to_admin(
    request_id: int,
    remark: str = Query(None),
    db: Session = Depends(get_db),
    manager: Employee = Depends(get_current_manager),
):
    try:
        req = (
            db.query(CardRequest)
            .filter(CardRequest.id == request_id)
            .filter(CardRequest.branch_id == manager.branch_id)
            .filter(CardRequest.employee_status == "Forwarded")
            .filter(CardRequest.status == "pending_manager")
            .first()
        )

        if not req:
            raise HTTPException(status_code=404, detail="Card request not found")

        req.manager_status = "Forwarded"
        req.manager_forwarded_at = datetime.utcnow()

        # Move to admin stage.
        req.status = "pending_admin"
        # Keep employee_status as-is.



        db.commit()
        db.refresh(req)

        return {"success": True, "message": "Forwarded to Admin", "request_id": req.id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

