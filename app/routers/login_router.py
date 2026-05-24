# loginrouter.py

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.backend.db import get_db

# IMPORT MODELS
from app.models.customer import Customer
from app.models.signup_model import SignupUsers
from app.models.admin import Admin
from app.models.branch_manager import BranchManager
from app.models.branch_employee import BranchEmployee

router = APIRouter()


# =========================================
# REQUEST MODEL
# =========================================

class LoginRequest(BaseModel):
    role: str
    username: str
    password: str


# =========================================
# LOGIN API
# =========================================

@router.post("/api/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):

    role = data.role
    username = data.username
    password = data.password

    print("ROLE RECEIVED =>", role)

    # =====================================================
    # CUSTOMER LOGIN
    # =====================================================

    if role == "user":

        customer = db.query(Customer).filter(
            Customer.branch_id == username,
            Customer.account_number == password
        ).first()

        if not customer:
            raise HTTPException(
                status_code=401,
                detail="Invalid customer credentials"
            )

        return {
            "success": True,
            "role": "user",
            "customer": {
                "customer_name": customer.customer_name,
                "account_number": customer.account_number,
                "branch_id": customer.branch_id
            }
        }

    # =====================================================
    # SIGNUP USER LOGIN
    # =====================================================

        # ---------------- SIGNUP USER LOGIN ----------------
    if data.role == "signup_user":

        from app.backend.db import get_db
        from app.models.signup_model import SignupUsers

        db = next(get_db())

        try:

            signup_user = (
                db.query(SignupUsers)
                .filter(SignupUsers.name == data.username)
                .filter(SignupUsers.password == data.password)
                .first()
            )

            if not signup_user:
                return {
                    "success": False,
                    "message": "Invalid signup user credentials"
                }

            return {
                "success": True,
                "role": "signup_user",
                "user": {
                    "id": signup_user.id,
                    "name": signup_user.name,
                    "email": signup_user.email
                }
            }

        finally:
            db.close()

    # =====================================================
    # ADMIN LOGIN
    # =====================================================

    elif role == "admin":

        admin = db.query(Admin).filter(
            Admin.admin_id == username,
            Admin.password == password
        ).first()

        if not admin:
            raise HTTPException(
                status_code=401,
                detail="Invalid admin credentials"
            )

        return {
            "success": True,
            "role": "admin"
        }

    # =====================================================
    # BRANCH MANAGER LOGIN
    # =====================================================

    elif role == "branch_manager":

        manager = db.query(BranchManager).filter(
            BranchManager.manager_id == username,
            BranchManager.password == password
        ).first()

        if not manager:
            raise HTTPException(
                status_code=401,
                detail="Invalid manager credentials"
            )

        return {
            "success": True,
            "role": "branch_manager",
            "name": manager.name,
            "branch_id": manager.branch_id
        }

    # =====================================================
    # BRANCH EMPLOYEE LOGIN
    # =====================================================

    elif role == "branch_employee":

        employee = db.query(BranchEmployee).filter(
            BranchEmployee.employee_id == username,
            BranchEmployee.password == password
        ).first()

        if not employee:
            raise HTTPException(
                status_code=401,
                detail="Invalid employee credentials"
            )

        return {
            "success": True,
            "role": "branch_employee",
            "name": employee.name,
            "branch_id": employee.branch_id
        }

    # =====================================================
    # INVALID ROLE
    # =====================================================

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid role selected"
        )