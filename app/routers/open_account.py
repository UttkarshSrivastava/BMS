from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.backend.db import get_db
from app.models.account_request import AccountRequest
import random

router = APIRouter(prefix="/api/open-account", tags=["Open Account"])


# 🟢 CREATE APPLICATION
@router.post("")
def create_application(data: dict, db: Session = Depends(get_db)):

    new_req = AccountRequest(
      branch_id = data.get("branch_id"),
     

        full_name=data.get("full_name"),
        father_name=data.get("father_name"),
        mobile=data.get("mobile"),
        email=data.get("email"),
        aadhaar=data.get("aadhaar"),
        pan=data.get("pan"),

        nominee_name=data.get("nominee_name"),
        nominee_relation=data.get("nominee_relation"),
        nominee_mobile=data.get("nominee_mobile"),
        nominee_address=data.get("nominee_address"),

        deposit_amount=float(data.get("deposit_amount") or 0),
        payment_mode=data.get("payment_mode"),

        employee_status="Pending",
        manager_status="Waiting",
        admin_status="Waiting",

        status="pending_employee",
        current_stage="employee"
    )

    db.add(new_req)
    db.commit()
    db.refresh(new_req)

    return {
        "message": "Application submitted",
        "application_id": new_req.id
    }


# 🟡 GET STATUS (FOR FRONTEND POLLING)
@router.get("/status/{app_id}")
def get_status(app_id: int, db: Session = Depends(get_db)):

    req = db.query(AccountRequest).filter(
        AccountRequest.id == app_id
    ).first()

    if not req:
        return {"message": "Not found"}

    return {
        "employee_status": req.employee_status,
        "manager_status": req.manager_status,
        "admin_status": req.admin_status,
        "generated_username": req.generated_username,
        "generated_account_number": req.generated_account_number
    }


# 🔵 EMPLOYEE FORWARD
@router.put("/employee/forward/{app_id}")
def employee_forward(app_id: int, remark: str, db: Session = Depends(get_db)):

    req = db.query(AccountRequest).filter(AccountRequest.id == app_id).first()

    req.employee_status = "Forwarded"
    req.status = "forwarded_manager"
    req.current_stage = "manager"

    db.commit()

    return {"message": "Forwarded to Manager"}


# 🟠 MANAGER FORWARD
@router.put("/manager/forward/{app_id}")
def manager_forward(app_id: int, remark: str, db: Session = Depends(get_db)):

    req = db.query(AccountRequest).filter(AccountRequest.id == app_id).first()

    req.manager_status = "Forwarded"
    req.status = "forwarded_admin"
    req.current_stage = "admin"

    db.commit()

    return {"message": "Forwarded to Admin"}


# 🟢 ADMIN APPROVE (FINAL → accounts table insert logic yahan add hoga)
@router.put("/admin/approve/{app_id}")
def admin_approve(app_id: int, db: Session = Depends(get_db)):

    req = db.query(AccountRequest).filter(AccountRequest.id == app_id).first()

    acc_no = str(random.randint(10000000, 99999999))

    req.admin_status = "Approved"
    req.status = "approved"
    req.current_stage = "completed"

    req.generated_account_number = acc_no
    req.generated_username = req.branch_id + acc_no

    db.commit()

    return {
        "message": "Account Approved",
        "account_number": acc_no,
        "username": req.generated_username
    }