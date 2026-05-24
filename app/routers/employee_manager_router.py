from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.auth.auth_handler import verify_token

from app.models.employee import Employee

router = APIRouter(
    prefix="/employee-manager",
    tags=["Branch Manager Employee Module"]
)


# ==========================================
# AUTH HELPER
# ==========================================

def get_current_manager(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db)
):

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header"
        )

    try:

        scheme, token = authorization.split()

        if scheme.lower() != "bearer":
            raise Exception()

    except:
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header"
        )

    payload = verify_token(token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    employee_id = (
        payload.get("employee_id")
        or payload.get("sub")
    )

    if not employee_id:
        raise HTTPException(
            status_code=401,
            detail="Token missing employee id"
        )

    manager = (
        db.query(Employee)
        .filter(Employee.employee_id == employee_id)
        .first()
    )

    if not manager:
        raise HTTPException(
            status_code=404,
            detail="Manager not found"
        )

    # only branch manager allowed
    if (
        (manager.department or "")
        .strip()
        .lower()
        != "manager"
    ):
        raise HTTPException(
            status_code=403,
            detail="Only branch manager allowed"
        )

    return manager


# ==========================================
# GET ALL EMPLOYEES OF MANAGER BRANCH
# ==========================================

@router.get("/employees")
def get_branch_employees(
    manager: Employee = Depends(get_current_manager),
    db: Session = Depends(get_db)
):

    employees = (
        db.query(Employee)
        .filter(Employee.branch_id == manager.branch_id)
        .order_by(Employee.employee_id.asc())
        .all()
    )

    return {
        "success": True,
        "branch_id": manager.branch_id,
        "total": len(employees),

        "employees": [

            {
                "employee_id": emp.employee_id,
                "first_name": emp.first_name,
                "last_name": emp.last_name,
                "email": emp.email,
                "phone": emp.phone,
                "department": emp.department,
                "salary": emp.salary,
                "branch_id": emp.branch_id,
            }

            for emp in employees
        ]
    }


# ==========================================
# GET SINGLE EMPLOYEE
# ==========================================

@router.get("/employees/{employee_id}")
def get_single_employee(
    employee_id: str,
    manager: Employee = Depends(get_current_manager),
    db: Session = Depends(get_db)
):

    emp = (
        db.query(Employee)
        .filter(
            Employee.employee_id == employee_id,
            Employee.branch_id == manager.branch_id
        )
        .first()
    )

    if not emp:
        raise HTTPException(
            status_code=404,
            detail="Employee not found in your branch"
        )

    return {
        "success": True,

        "employee": {
            "employee_id": emp.employee_id,
            "first_name": emp.first_name,
            "last_name": emp.last_name,
            "email": emp.email,
            "phone": emp.phone,
            "department": emp.department,
            "salary": emp.salary,
            "branch_id": emp.branch_id,
        }
    }


# ==========================================
# DELETE EMPLOYEE
# ==========================================

@router.delete("/employees/{employee_id}")
def delete_employee(
    employee_id: str,
    manager: Employee = Depends(get_current_manager),
    db: Session = Depends(get_db)
):

    emp = (
        db.query(Employee)
        .filter(
            Employee.employee_id == employee_id,
            Employee.branch_id == manager.branch_id
        )
        .first()
    )

    if not emp:
        raise HTTPException(
            status_code=404,
            detail="Employee not found"
        )

    db.delete(emp)

    db.commit()

    return {
        "success": True,
        "message": "Employee deleted successfully"
    }