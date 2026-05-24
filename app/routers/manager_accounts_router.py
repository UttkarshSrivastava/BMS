from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.auth.auth_handler import verify_token
from app.models.employee import Employee
from app.models.account import Account

router = APIRouter(prefix="/accounts/manager", tags=["Manager Accounts"])


# ---------------- AUTH ----------------
def get_current_manager(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise Exception()
    except:
        raise HTTPException(status_code=401, detail="Invalid Authorization header format")

    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    emp_id = payload.get("employee_id") or payload.get("sub")

    manager = db.query(Employee).filter(Employee.employee_id == emp_id).first()

    if not manager:
        raise HTTPException(status_code=404, detail="Manager not found")

    if (manager.department or "").lower() != "manager":
        raise HTTPException(status_code=403, detail="Only branch manager allowed")

    return manager


# ---------------- HELPERS ----------------
def account_to_dict(a: Account):
    return {
        "account_number": a.account_number,
        "customer_name": a.customer_name,
        "mobile": a.mobile,
        "email": a.email,
        "address": a.address,
        "nominee": a.nominee,
        "account_type": a.account_type,
        "balance": float(a.balance or 0),
        "status": a.status,
        "branch_id": a.branch_id,
    }


# ---------------- GET ALL (BRANCH ONLY) ----------------
@router.get("/all")
def get_branch_accounts(
    manager: Employee = Depends(get_current_manager),
    db: Session = Depends(get_db)
):

    return {
        "success": True,
        "accounts": [
            {
                "account_number": a.account_number,
                "customer_name": a.customer_name,
                "mobile": a.mobile,
                "email": a.email,
                "balance": float(a.balance or 0),
                "status": a.status,
                "branch_id": a.branch_id
            }
            for a in db.query(Account).filter(
                Account.branch_id == manager.branch_id
            ).all()
        ]
    }

# ---------------- SEARCH (BRANCH ONLY) ----------------
@router.get("/search")
def search_accounts(
    account_number: str | None = None,
    mobile: str | None = None,
    customer_name: str | None = None,
    manager: Employee = Depends(get_current_manager),
    db: Session = Depends(get_db)
):

    q = db.query(Account).filter(
        Account.branch_id == manager.branch_id   # 🔥 MOST IMPORTANT FIX
    )

    if account_number:
        q = q.filter(Account.account_number == account_number)

    if mobile:
        q = q.filter(Account.mobile == mobile)

    if customer_name:
        q = q.filter(Account.customer_name.ilike(f"%{customer_name}%"))

    results = q.all()

    return {
        "success": True,
        "accounts": [account_to_dict(a) for a in results]
    }