from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy.orm import Session

from app.backend.db import get_db

from app.models.account import Account
from app.models.transaction import Transaction



router = APIRouter(prefix="/customer", tags=["Customer"])


@router.get("/me")
def customer_me(
    account_number: str = Query(..., description="Customer account number (ACC-...)") ,
    db: Session = Depends(get_db),
):
    acc = db.query(Account).filter(Account.account_number == account_number).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")

    # Recent transactions: latest 10 for this account
    txs = (
        db.query(Transaction)
        .filter(Transaction.account_number == acc.account_number)
        .order_by(Transaction.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "customer_name": acc.customer_name,
        "account_number": acc.account_number,
        "branch_id": acc.branch_id,
        "balance": acc.balance,
        "email": acc.email,
        "mobile": acc.mobile,
        "aadhaar": acc.aadhaar,
        "pan": acc.pan,
        "address": acc.address,
        "account_type": acc.account_type,
        "account_status": acc.status,
        "recent_transactions": [
            {
                "transaction_id": t.transaction_id,
                "transaction_type": t.transaction_type,
                "amount": t.amount,
                "created_at": t.created_at,
            }
            for t in txs
        ],
    }
@router.get("/profile")

def get_user_profile(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):

    try:

        if not authorization:
            raise HTTPException(
                status_code=401,
                detail="Token missing"
            )

        token = authorization.split(" ")[1]

        user = db.query(SignupUsers).filter(
            SignupUsers.token == token
        ).first()

        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return {

            "full_name": user.full_name,
            "account_number": user.account_number,
            "mobile": user.mobile,
            "email": user.email,
            "address": user.address,
            "city": user.city,
            "pincode": user.pincode

        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

