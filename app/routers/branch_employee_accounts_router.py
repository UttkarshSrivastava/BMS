from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import or_

from datetime import datetime
from zoneinfo import ZoneInfo

import random

from app.backend.db import get_db

from app.models.account import Account
from app.models.transaction import Transaction
from app.models.employee import Employee

from app.auth.auth_handler import verify_token


router = APIRouter(
    prefix="/branch-employee/accounts",
    tags=["Branch Employee Accounts"]
)


# =====================================================
# GET CURRENT EMPLOYEE
# =====================================================

def get_current_employee(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization missing"
        )

    try:

        token = authorization.replace(
            "Bearer ",
            ""
        ).strip()

        payload = verify_token(token)

        employee_id = (
            payload.get("employee_id")
            or payload.get("id")
            or payload.get("sub")
        )

        if not employee_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        employee = (
            db.query(Employee)
            .filter(
                Employee.employee_id == str(employee_id)
            )
            .first()
        )

        if not employee:
            raise HTTPException(
                status_code=404,
                detail="Employee not found"
            )

        return employee

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


# =====================================================
# GENERATE ACCOUNT NUMBER
# =====================================================

def generate_account_number(db):

    while True:

        acc_no = f"ACC-{random.randint(100000,999999)}"

        exists = (
            db.query(Account)
            .filter(
                Account.account_number == acc_no
            )
            .first()
        )

        if not exists:
            return acc_no


# =====================================================
# GENERATE TRANSACTION ID
# =====================================================

def generate_txn_id(db):

    while True:

        txn_id = f"TXN-{random.randint(100000,999999)}"

        exists = (
            db.query(Transaction)
            .filter(
                Transaction.transaction_id == txn_id
            )
            .first()
        )

        if not exists:
            return txn_id


# =====================================================
# SERIALIZER
# =====================================================

def serialize_account(a):

    return {

        "account_number": a.account_number,
        "customer_name": a.customer_name,
        "email": a.email,
        "mobile": a.mobile,
        "aadhaar": a.aadhaar,
        "pan": a.pan,
        "address": a.address,
        "account_type": a.account_type,
        "balance": a.balance,
        "nominee": a.nominee,
        "branch_id": a.branch_id,
        "status": a.status
    }


# =====================================================
# CREATE ACCOUNT
# =====================================================

@router.post("/create")
def create_account(
    payload: dict,
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee)
):

    existing = (
        db.query(Account)
        .filter(
            or_(
                Account.mobile == payload.get("mobile"),
                Account.aadhaar == payload.get("aadhaar"),
                Account.pan == payload.get("pan")
            )
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=400,
            detail="Customer already exists"
        )

    initial_deposit = float(
        payload.get("initial_deposit", 0)
    )

    if initial_deposit < 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid deposit amount"
        )

    account = Account(

        account_number=
            generate_account_number(db),

        customer_name=
            payload.get("customer_name"),

        email=
            payload.get("email"),

        mobile=
            payload.get("mobile"),

        aadhaar=
            payload.get("aadhaar"),

        pan=
            payload.get("pan"),

        address=
            payload.get("address"),

        account_type=
            payload.get("account_type"),

        initial_deposit=
            initial_deposit,

        balance=
            initial_deposit,

        nominee=
            payload.get("nominee"),

        branch_id=
            employee.branch_id,

        status="ACTIVE"
    )

    try:

        db.add(account)

        db.commit()

        db.refresh(account)

        return {

            "success": True,

            "message":
                "Account created successfully",

            "account_number":
                account.account_number,

            "branch_id":
                account.branch_id
        }

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to create account"
        )


# =====================================================
# GET ALL ACCOUNTS
# =====================================================

@router.get("/employee/all")
def get_accounts(
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee)
):

    accounts = (
        db.query(Account)
        .filter(
            Account.branch_id == employee.branch_id
        )
        .all()
    )

    return {

        "success": True,

        "employee_branch":
            employee.branch_id,

        "accounts":
            [serialize_account(a) for a in accounts]
    }


# =====================================================
# SEARCH ACCOUNTS
# =====================================================

@router.get("/employee/search")
def search_accounts(
    account_number: str = "",
    mobile: str = "",
    customer_name: str = "",
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee)
):

    query = (
        db.query(Account)
        .filter(
            Account.branch_id == employee.branch_id
        )
    )

    if account_number:

        query = query.filter(
            Account.account_number == account_number
        )

    if mobile:

        query = query.filter(
            Account.mobile == mobile
        )

    if customer_name:

        query = query.filter(
            Account.customer_name.ilike(
                f"%{customer_name}%"
            )
        )

    accounts = query.all()

    return {

        "success": True,

        "accounts":
            [serialize_account(a) for a in accounts]
    }


# =====================================================
# UPDATE ACCOUNT
# =====================================================

@router.put("/{account_number}")
def update_account(
    account_number: str,
    payload: dict,
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee)
):

    account = (
        db.query(Account)
        .filter(
            Account.account_number == account_number,
            Account.branch_id == employee.branch_id
        )
        .first()
    )

    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    account.mobile = payload.get("mobile")
    account.email = payload.get("email")
    account.address = payload.get("address")
    account.nominee = payload.get("nominee")
    account.account_type = payload.get("account_type")

    try:

        db.commit()

        return {

            "success": True,

            "message":
                "Account updated successfully"
        }

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to update account"
        )


# =====================================================
# DEPOSIT
# =====================================================

@router.post("/deposit")
def deposit(
    payload: dict,
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee)
):

    account = (
        db.query(Account)
        .filter(
            Account.account_number ==
                payload.get("account_number"),

            Account.branch_id ==
                employee.branch_id
        )
        .first()
    )

    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    if account.status != "ACTIVE":
        raise HTTPException(
            status_code=400,
            detail="Account is not active"
        )

    amount = float(
        payload.get("amount", 0)
    )

    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid amount"
        )

    account.balance += amount

    txn = Transaction(

        transaction_id=
            generate_txn_id(db),

        transaction_type="CREDIT",

        account_number=
            account.account_number,

        amount=amount,

        balance_after=
            account.balance,

        created_at=
            datetime.now(
                ZoneInfo("Asia/Kolkata")
            )
    )

    try:

        db.add(txn)

        db.commit()

        return {

            "success": True,

            "message":
                "Amount deposited successfully"
        }

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Deposit failed"
        )


# =====================================================
# WITHDRAW
# =====================================================

@router.post("/withdraw")
def withdraw(
    payload: dict,
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee)
):

    account = (
        db.query(Account)
        .filter(
            Account.account_number ==
                payload.get("account_number"),

            Account.branch_id ==
                employee.branch_id
        )
        .first()
    )

    if not account:
        raise HTTPException(
            status_code=404,
            detail="Account not found"
        )

    if account.status != "ACTIVE":
        raise HTTPException(
            status_code=400,
            detail="Account is not active"
        )

    amount = float(
        payload.get("amount", 0)
    )

    if amount <= 0:
        raise HTTPException(
            status_code=400,
            detail="Invalid amount"
        )

    if account.balance < amount:
        raise HTTPException(
            status_code=400,
            detail="Insufficient balance"
        )

    account.balance -= amount

    txn = Transaction(

        transaction_id=
            generate_txn_id(db),

        transaction_type="DEBIT",

        account_number=
            account.account_number,

        amount=amount,

        balance_after=
            account.balance,

        created_at=
            datetime.now(
                ZoneInfo("Asia/Kolkata")
            )
    )

    try:

        db.add(txn)

        db.commit()

        return {

            "success": True,

            "message":
                "Amount withdrawn successfully"
        }

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Withdraw failed"
        )