from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import datetime, timedelta

from app.backend.db import get_db
from app.models.branch import Branch
from app.models.account import Account
from app.models.employee import Employee
from app.models.transaction import Transaction

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])


@router.get("/dashboard")
def admin_dashboard(db: Session = Depends(get_db)):

    # ================= BASIC COUNTS =================
    total_branches = db.query(func.count(Branch.id)).scalar()
    total_accounts = db.query(func.count(Account.id)).scalar()
    total_employees = db.query(func.count(Employee.id)).scalar()

    # ================= BALANCE =================
    total_bank_balance = db.query(func.sum(Account.balance)).scalar() or 0

    # ================= STATUS COUNTS =================
    total_active_accounts = db.query(func.count(Account.id)).filter(
        Account.status == "active"
    ).scalar()

    total_freeze_accounts = db.query(func.count(Account.id)).filter(
        Account.status == "freeze"
    ).scalar()

    total_loans = 0  # update if you have loan table

    # ================= RECENT TRANSACTIONS =================
    recent_txns = db.query(Transaction)\
        .order_by(Transaction.created_at.desc())\
        .limit(10)\
        .all()

    recent_loan_applications = [
        {
            "application_id": t.transaction_id,
            "customer_name": t.account_number or t.sender_account_number,
            "loan_type": t.transaction_type,
            "amount": t.amount,
            "branch": "Main",
            "status": "Completed"
        }
        for t in recent_txns
    ]

    # ================= DAILY =================
    today = datetime.now().date()
    daily_labels = []
    daily_values = []

    for i in range(6, -1, -1):
        day = today - timedelta(days=i)

        count = db.query(func.count(Transaction.id)).filter(
            func.date(Transaction.created_at) == day
        ).scalar()

        daily_labels.append(day.strftime("%a"))
        daily_values.append(count or 0)

    # ================= MONTHLY =================
    year = datetime.now().year
    monthly_labels = []
    monthly_values = []

    for m in range(1, 13):
        count = db.query(func.count(Transaction.id)).filter(
            extract("year", Transaction.created_at) == year,
            extract("month", Transaction.created_at) == m
        ).scalar()

        monthly_labels.append(str(m))
        monthly_values.append(count or 0)

    # ================= RESPONSE =================
    return {
        "total_branches": total_branches,
        "total_accounts": total_accounts,
        "total_employees": total_employees,
        "total_bank_balance": total_bank_balance,
        "total_active_accounts": total_active_accounts,
        "total_freeze_accounts": total_freeze_accounts,
        "total_loans": total_loans,

        "recent_loan_applications": recent_loan_applications,

        "daily_transaction_labels": daily_labels,
        "daily_transactions": daily_values,

        "monthly_transaction_labels": monthly_labels,
        "monthly_transactions": monthly_values,

        "chart_labels": monthly_labels[:6],
        "application_chart": monthly_values[:6],
        "approved_chart": monthly_values[:6],
    }