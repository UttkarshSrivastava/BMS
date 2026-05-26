from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.models.account import Account
from app.models.transaction import Transaction

router = APIRouter(prefix="/account-queries", tags=["Account Queries"])


@router.get("/balance")
def get_balance(
    account_number: str = Query(...),
    db: Session = Depends(get_db)
):
    acc = db.query(Account).filter(
        Account.account_number == account_number
    ).first()

    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")

    return {
        "account_number": acc.account_number,
        "customer_name": acc.customer_name,
        "balance": acc.balance,
        "status": acc.status,
        "branch_id": acc.branch_id,
    }


@router.get("/mini-statement")
def mini_statement(
    account_number: str = Query(...),
    db: Session = Depends(get_db)
):
    acc = db.query(Account).filter(
        Account.account_number == account_number
    ).first()

    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")

    txs = (
        db.query(Transaction)
        .filter(Transaction.account_number == account_number)
        .order_by(Transaction.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "account_number": acc.account_number,
        "customer_name": acc.customer_name,
        "balance": acc.balance,
        "transactions": [
            {
                "transaction_id": t.transaction_id,
                "transaction_type": t.transaction_type,
                "amount": t.amount,
                "balance_after": t.balance_after,
                "created_at": t.created_at,
            }
            for t in txs
        ],
    }


@router.get("/full-statement")
def full_statement(
    account_number: str = Query(...),
    db: Session = Depends(get_db)
):
    acc = db.query(Account).filter(
        Account.account_number == account_number
    ).first()

    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")

    txs = (
        db.query(Transaction)
        .filter(Transaction.account_number == account_number)
        .order_by(Transaction.created_at.desc())
        .all()
    )

    return {
        "account_number": acc.account_number,
        "customer_name": acc.customer_name,
        "balance": acc.balance,
        "total_transactions": len(txs),
        "transactions": [
            {
                "transaction_id": t.transaction_id,
                "transaction_type": t.transaction_type,
                "amount": t.amount,
                "balance_after": t.balance_after,
                "created_at": t.created_at,
            }
            for t in txs
        ],
    }


@router.get("/details")
def account_details(
    account_number: str = Query(...),
    db: Session = Depends(get_db)
):
    acc = db.query(Account).filter(
        Account.account_number == account_number
    ).first()

    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")

    return {
        "account_number": acc.account_number,
        "customer_name": acc.customer_name,
        "email": acc.email,
        "mobile": acc.mobile,
        "aadhaar": acc.aadhaar,
        "pan": acc.pan,
        "address": acc.address,
        "account_type": acc.account_type,
        "balance": acc.balance,
        "status": acc.status,
        "branch_id": acc.branch_id,
        "nominee": acc.nominee,
    }
