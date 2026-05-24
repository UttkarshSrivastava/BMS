from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.backend.db import get_db
from app.models.loan_request import LoanRequest
from app.models.employee import Employee
from app.auth.auth_handler import verify_token


router = APIRouter(
    prefix="/employee-loans-request-page",
    tags=["Employee Loan"]
)

# =========================
# AUTH
# =========================
def get_current_employee(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing token")

    token = authorization.replace("Bearer ", "").strip()

    payload = verify_token(token)

    employee_id = payload.get("employee_id") or payload.get("sub")

    employee = db.query(Employee).filter(
        Employee.employee_id == str(employee_id)
    ).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee


# =========================
# SCHEMA
# =========================
class StatusUpdate(BaseModel):
    status: str


# =========================
# GET LOANS
# =========================
@router.get("/loan-requests")
def get_loans(
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee)
):

    loans = db.query(LoanRequest).filter(
        LoanRequest.branch_id == employee.branch_id
    ).all()

    return {
        "success": True,
        "loans": [
            {
                "id": l.id,
                "user_name": l.user_name,
                "amount": l.amount,
                "duration": l.duration,
                "emi": l.emi or 0,
                "status": l.status
            }
            for l in loans
        ]
    }


# =========================
# UPDATE STATUS
# =========================
@router.put("/loan-status/{loan_id}")
def update_status(
    loan_id: int,
    data: StatusUpdate,
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee)
):

    loan = db.query(LoanRequest).filter(
        LoanRequest.id == loan_id,
        LoanRequest.branch_id == employee.branch_id
    ).first()

    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    loan.status = data.status
    db.commit()

    return {"success": True, "message": "Updated"}


# =========================
# FORWARD
# =========================
@router.put("/forward/{loan_id}")
def forward(
    loan_id: int,
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee)
):

    loan = db.query(LoanRequest).filter(
        LoanRequest.id == loan_id,
        LoanRequest.branch_id == employee.branch_id
    ).first()

    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    loan.status = "FORWARDED_TO_MANAGER"
    db.commit()

    return {"success": True, "message": "Forwarded"}