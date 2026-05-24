from datetime import datetime, timedelta
import jwt
from sqlalchemy.orm import Session

from app.auth.auth_handler import create_token
from app.models.employee import Employee


def authenticate_branch_employee(db: Session, username: str, password: str):
    # Requirement:
    # - username = branch id
    # - password = emp id (Employee.employee_id)
    username = str(username).strip()
    password = str(password).strip()

    # Department check: this endpoint is only for non-Manager employees.
    emp = (
        db.query(Employee)
        .filter(Employee.branch_id == username)
        .filter(Employee.employee_id == password)
        .first()
    )
    if not emp:
        return {"success": False, "message": "You are not employee in this branch"}

    if (emp.department or "").strip().lower() == "manager":
        return {"success": False, "message": "You are not employee in this branch"}




    token = create_token(
        {
            "employee_id": emp.employee_id,
            "role": "branch_employee",
            "iat": datetime.utcnow().timestamp(),
        }
    )

    return {
        "success": True,
        "role": "branch_employee",
        "access_token": token,
        "name": f"{emp.first_name} {emp.last_name}",
        "branch_id": emp.branch_id,
        "employee": {
            "employee_id": emp.employee_id,
            "first_name": emp.first_name,
            "last_name": emp.last_name,
            "email": emp.email,
            "phone": emp.phone,
            "department": emp.department,
            "branch_id": emp.branch_id,
            "salary": emp.salary,
        },
    }

