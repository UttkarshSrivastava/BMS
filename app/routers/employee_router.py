from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid

from app.backend.db import get_db
from app.models.employee import Employee

router = APIRouter(
    prefix="/employee",
    tags=["Employee"]
)


# =========================================================
# GET ALL EMPLOYEES
# =========================================================
@router.get("/get-employees")
def list_employees(db: Session = Depends(get_db)):

    employees = db.query(Employee).all()

    return [
        {
            "id": e.id,
            "employee_id": e.employee_id,
            "first_name": e.first_name,
            "last_name": e.last_name,
            "email": e.email,
            "phone": e.phone,
            "department": e.department,
            "branch_id": e.branch_id,
            "salary": e.salary,
        }
        for e in employees
    ]


# =========================================================
# CREATE EMPLOYEE
# =========================================================
@router.post("/create")
def create_employee(data: dict, db: Session = Depends(get_db)):

    try:

        emp = Employee(
            employee_id="EMP-" + str(uuid.uuid4())[:8],
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            email=data.get("email"),
            phone=data.get("phone"),
            department=data.get("department"),
            branch_id=data.get("branch_id"),
            salary=data.get("salary")
        )

        db.add(emp)
        db.commit()
        db.refresh(emp)

        return {
            "success": True,
            "message": "Employee created successfully"
        }

    except Exception as e:

        db.rollback()

        return {
            "success": False,
            "message": str(e)
        }


# =========================================================
# TRANSFER EMPLOYEE
# =========================================================
@router.post("/transfer-employee")
def transfer_employee(data: dict, db: Session = Depends(get_db)):

    try:

        emp_id = int(data.get("employee_id"))

        emp = db.query(Employee).filter(
            Employee.id == emp_id
        ).first()

        if not emp:
            return {
                "success": False,
                "message": "Employee not found"
            }

        emp.branch_id = str(data.get("new_branch_id"))

        db.commit()

        return {
            "success": True,
            "message": "Employee transferred successfully"
        }

    except Exception as e:

        db.rollback()

        return {
            "success": False,
            "message": str(e)
        }