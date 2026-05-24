from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from datetime import datetime, timedelta

from app.backend.db import get_db

from app.models.employee import Employee
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.branch import Branch

from app.auth.auth_handler import verify_token


router = APIRouter(
    prefix="/branch-manager",
    tags=["Branch Manager Dashboard"]
)


# =====================================================
# GET CURRENT MANAGER
# =====================================================

def get_current_manager(
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

        print("TOKEN PAYLOAD =>", payload)

        employee_id = (

            payload.get("employee_id")

            or payload.get("employeeId")

            or payload.get("id")

            or payload.get("sub")

        )

        if not employee_id:

            raise HTTPException(
                status_code=401,
                detail="Employee ID missing in token"
            )

        manager = db.query(Employee).filter(
            Employee.employee_id == str(employee_id)
        ).first()

        if not manager:

            raise HTTPException(
                status_code=404,
                detail="Manager not found"
            )

        return manager

    except HTTPException:
        raise

    except Exception as e:

        print("VERIFY TOKEN ERROR =>", e)

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


# =====================================================
# BRANCH MANAGER DASHBOARD API
# =====================================================

@router.get("/dashboard-data")
def branch_manager_dashboard_data(
    db: Session = Depends(get_db),
    manager: Employee = Depends(get_current_manager)
):

    try:

        branch_id = manager.branch_id

        # =================================================
        # TOTAL ACCOUNTS
        # =================================================

        total_accounts = db.query(Account).filter(
            Account.branch_id == branch_id
        ).count()

        # =================================================
        # ACTIVE ACCOUNTS
        # =================================================

        active_accounts = db.query(Account).filter(
            Account.branch_id == branch_id,
            Account.status == "ACTIVE"
        ).count()

        # =================================================
        # TOTAL BRANCH BALANCE
        # =================================================

        branch_balance = db.query(
            func.sum(Account.balance)
        ).filter(
            Account.branch_id == branch_id
        ).scalar() or 0

        # =================================================
        # ALL BRANCH ACCOUNTS
        # =================================================

        branch_accounts = db.query(Account).filter(
            Account.branch_id == branch_id
        ).all()

        account_numbers = [
            acc.account_number
            for acc in branch_accounts
        ]

        # =================================================
        # TOTAL TRANSACTIONS
        # =================================================

        total_transactions = db.query(Transaction).filter(

            or_(

                Transaction.account_number.in_(account_numbers),

                Transaction.sender_account_number.in_(account_numbers),

                Transaction.receiver_account_number.in_(account_numbers)

            )

        ).count()

        # =================================================
        # RECENT TRANSACTIONS
        # =================================================

        recent_txns = db.query(Transaction).filter(

            or_(

                Transaction.account_number.in_(account_numbers),

                Transaction.sender_account_number.in_(account_numbers),

                Transaction.receiver_account_number.in_(account_numbers)

            )

        ).order_by(
            Transaction.created_at.desc()
        ).limit(10).all()

        recent_transactions = []

        for txn in recent_txns:

            account_no = (

                txn.account_number

                or txn.sender_account_number

                or txn.receiver_account_number

            )

            customer_name = "N/A"

            if account_no:

                acc = db.query(Account).filter(
                    Account.account_number == account_no
                ).first()

                if acc:
                    customer_name = acc.customer_name

            recent_transactions.append({

                "transaction_id":
                    txn.transaction_id,

                "account_number":
                    account_no,

                "customer_name":
                    customer_name,

                "transaction_type":
                    txn.transaction_type,

                "amount":
                    float(txn.amount or 0),

                "created_at":
                    txn.created_at.strftime("%d-%m-%Y %H:%M")
                    if txn.created_at else "",

            })

        # =================================================
        # MONTHLY CHART
        # =================================================

        monthly_labels = [
            "Jan", "Feb", "Mar",
            "Apr", "May", "Jun",
            "Jul", "Aug", "Sep",
            "Oct", "Nov", "Dec"
        ]

        monthly_data = [0] * 12

        all_txns = db.query(Transaction).filter(

            or_(

                Transaction.account_number.in_(account_numbers),

                Transaction.sender_account_number.in_(account_numbers),

                Transaction.receiver_account_number.in_(account_numbers)

            )

        ).all()

        for txn in all_txns:

            if txn.created_at:

                month_index = txn.created_at.month - 1

                monthly_data[month_index] += 1

        # =================================================
        # DAILY CHART
        # =================================================

        daily_labels = []

        daily_credit = []

        daily_debit = []

        for i in range(6, -1, -1):

            day = datetime.now() - timedelta(days=i)

            label = day.strftime("%d %b")

            daily_labels.append(label)

            credit_count = db.query(Transaction).filter(

                or_(

                    Transaction.account_number.in_(account_numbers),

                    Transaction.sender_account_number.in_(account_numbers),

                    Transaction.receiver_account_number.in_(account_numbers)

                ),

                Transaction.transaction_type == "CREDIT",

                func.date(Transaction.created_at) == day.date()

            ).count()

            debit_count = db.query(Transaction).filter(

                or_(

                    Transaction.account_number.in_(account_numbers),

                    Transaction.sender_account_number.in_(account_numbers),

                    Transaction.receiver_account_number.in_(account_numbers)

                ),

                Transaction.transaction_type == "DEBIT",

                func.date(Transaction.created_at) == day.date()

            ).count()

            daily_credit.append(credit_count)

            daily_debit.append(debit_count)

        # =================================================
        # BRANCH NAME
        # =================================================

        branch = db.query(Branch).filter(
            Branch.branch_id == branch_id
        ).first()

        branch_name = "Main Branch"

        if branch:

            branch_name = (

                getattr(branch, "branch_name", None)

                or getattr(branch, "name", None)

                or "Main Branch"

            )

        # =================================================
        # RESPONSE
        # =================================================

        return {

            "success": True,

            "manager_name":

                getattr(
                    manager,
                    "employee_name",
                    "Branch Manager"
                ),

            "branch_name":
                branch_name,

            "branch_id":
                branch_id,

            "total_accounts":
                total_accounts,

            "active_accounts":
                active_accounts,

            "total_transactions":
                total_transactions,

            "branch_balance":
                float(branch_balance),

            "recent_transactions":
                recent_transactions,

            "monthly_chart": {

                "labels":
                    monthly_labels,

                "data":
                    monthly_data
            },

            "daily_chart": {

                "labels":
                    daily_labels,

                "credit":
                    daily_credit,

                "debit":
                    daily_debit
            }
        }

    except Exception as e:

        print("DASHBOARD ERROR =>", e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )