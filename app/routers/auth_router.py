from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.auth.auth_handler import verify_token
from app.models.employee import Employee

router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.get("/me")
def me(authorization: str = Header(default=None), db: Session = Depends(get_db)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    token = parts[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Expected payload keys (best-effort): employee_id or sub
    employee_id = payload.get("employee_id") or payload.get("sub")
    role_from_token = payload.get("role")

    # Admin token shortcut (admin is hardcoded and may not exist in Employee table)
    if role_from_token == "admin" or employee_id == "admin":
        return {
            "role": "admin",
            "employee_id": "admin",
            "name": "Admin",
            "branch_id": None,
        }

    if not employee_id:
        raise HTTPException(status_code=401, detail="Token has no employee_id")

    emp = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")

    mapped_role = "manager" if emp.department == "Manager" else "employee"

    return {
        "role": mapped_role,
        "employee_id": emp.employee_id,
        "name": f"{emp.first_name} {emp.last_name}",
        "first_name": emp.first_name,
        "last_name": emp.last_name,
        "email": emp.email,
        "phone": emp.phone,
        "department": emp.department,
        "branch_id": emp.branch_id,
        "salary": emp.salary,
    }

