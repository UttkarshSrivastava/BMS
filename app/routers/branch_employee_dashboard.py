# app/routers/branch_employee_dashboard.py

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from datetime import datetime, timedelta
from collections import defaultdict
from zoneinfo import ZoneInfo

from app.backend.db import get_db

from app.models.employee import Employee
from app.models.branch import Branch
from app.models.account import Account
from app.models.transaction import Transaction

from app.auth.auth_handler import verify_token

router = APIRouter(
    prefix="/employee-dashboard",
    tags=["Branch Employee Dashboard"]
)

# =====================================================
# AUTH: CURRENT EMPLOYEE
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
            "Bearer ", ""
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
                detail="Employee ID missing in token"
            )

        employee = db.query(Employee).filter(
            Employee.employee_id == str(employee_id)
        ).first()

        if not employee:
            raise HTTPException(
                status_code=404,
                detail="Employee not found"
            )

        return employee

    except Exception as e:

        print("AUTH ERROR =>", str(e))

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


# =====================================================
# DASHBOARD API
# =====================================================

@router.get("/dashboard")
def branch_employee_dashboard(
    db: Session = Depends(get_db),
    employee: Employee = Depends(get_current_employee)
):

    try:

        print("===== DASHBOARD START =====")

        branch_id = employee.branch_id

        # =========================================
        # BRANCH
        # =========================================
        branch = db.query(Branch).filter(
            Branch.id == branch_id
        ).first()

        # =========================================
        # ACCOUNTS
        # =========================================
        accounts = db.query(Account).filter(
            Account.branch_id == branch_id
        ).all()

        account_numbers = [
            acc.account_number
            for acc in accounts
        ]

        # TOTAL ACCOUNTS
        total_accounts = len(accounts)

        # ONLY ACTIVE ACCOUNTS
        active_accounts = len([

            acc for acc in accounts

            if str(
                getattr(acc, "status", "")
            ).lower() == "active"

        ])

        # BRANCH BALANCE
        branch_balance = db.query(
            func.sum(Account.balance)
        ).filter(
            Account.branch_id == branch_id
        ).scalar() or 0

        # =========================================
        # TRANSACTIONS
        # =========================================
        transactions = []

        if account_numbers:

            transactions = db.query(Transaction).filter(

                or_(

                    # NORMAL CREDIT / DEBIT
                    Transaction.account_number.in_(account_numbers),

                    # TRANSFER SENDER
                    Transaction.sender_account_number.in_(account_numbers),

                    # TRANSFER RECEIVER
                    Transaction.receiver_account_number.in_(account_numbers)

                )

            ).order_by(
                Transaction.created_at.desc()
            ).all()

        # =========================================
        # TOTAL TRANSACTION COUNT
        # =========================================
        total_transaction_count = len(transactions)

        # =========================================
        # RECENT TRANSACTIONS
        # =========================================
        recent_transactions = []

        for txn in transactions[:10]:

            txn_time = getattr(txn, "created_at", None)

            formatted_time = "N/A"

            if txn_time:

                try:

                    formatted_time = txn_time.astimezone(
                        ZoneInfo("Asia/Kolkata")
                    ).strftime("%Y-%m-%d %H:%M:%S")

                except:

                    formatted_time = str(txn_time)

            txn_account = (
                txn.account_number
                or txn.sender_account_number
                or txn.receiver_account_number
                or "N/A"
            )

            recent_transactions.append({

                "transaction_id": getattr(
                    txn,
                    "transaction_id",
                    "N/A"
                ),

                "account_number": txn_account,

                "type": getattr(
                    txn,
                    "transaction_type",
                    "Unknown"
                ),

                "amount": float(
                    getattr(txn, "amount", 0)
                ),

                "date": formatted_time,

                "status": "Success"
            })

        # =========================================
        # DAILY CREDIT / DEBIT GRAPH
        # =========================================
        today = datetime.now(
            ZoneInfo("Asia/Kolkata")
        )

        last_7_days = [
            today - timedelta(days=i)
            for i in range(6, -1, -1)
        ]

        credit_data = defaultdict(int)

        debit_data = defaultdict(int)

        for txn in transactions:

            if txn.created_at:

                try:

                    txn_date = txn.created_at.astimezone(
                        ZoneInfo("Asia/Kolkata")
                    ).date()

                except:

                    txn_date = txn.created_at.date()

                txn_type = str(
                    txn.transaction_type
                ).upper()

                # CREDIT COUNT
                if txn_type == "CREDIT":

                    credit_data[txn_date] += 1

                # DEBIT COUNT
                elif txn_type == "DEBIT":

                    debit_data[txn_date] += 1

        labels = []

        credit_values = []

        debit_values = []

        for day in last_7_days:

            date_key = day.date()

            labels.append(str(date_key))

            credit_values.append(
                credit_data.get(date_key, 0)
            )

            debit_values.append(
                debit_data.get(date_key, 0)
            )

        # =========================================
        # FINAL RESPONSE
        # =========================================
        return {

            "employee_name":
                f"{employee.first_name} {employee.last_name}",

            "employee_id":
                employee.employee_id,

            "branch_id":
                employee.branch_id,

            "branch_name":
                getattr(branch, "branch_name", "No Branch"),

            "branch_balance":
                float(branch_balance),

            "active_accounts":
                active_accounts,

            "total_accounts":
                total_accounts,

            "transaction_count":
                total_transaction_count,

            "recent_transactions":
                recent_transactions,

            "chart": {

                "labels": labels,

                "credit": credit_values,

                "debit": debit_values
            }
        }

    except Exception as e:

        print("DASHBOARD ERROR =>", str(e))

        return {
            "error": str(e)
        }