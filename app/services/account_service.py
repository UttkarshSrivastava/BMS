import random
import string
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.account import Account
from app.models.branch import Branch
from app.models.transaction import Transaction


def _generate_account_number(db: Session, prefix: str = "ACC-", digits: int = 6) -> str:
    while True:
        num = "".join(random.choices(string.digits, k=digits))
        acc_no = f"{prefix}{num}"
        if not db.query(Account).filter(Account.account_number == acc_no).first():
            return acc_no


def _generate_transaction_id(db: Session, prefix: str = "TXN-", digits: int = 10) -> str:
    while True:
        num = "".join(random.choices(string.digits, k=digits))
        tx_id = f"{prefix}{num}"
        if not db.query(Transaction).filter(Transaction.transaction_id == tx_id).first():
            return tx_id


def get_all_branches_for_dropdown(db: Session):
    branches = db.query(Branch).all()
    return [
        {
            "id": b.id,
            "branch_id": b.branch_id,
            "branch_name": b.branch_name,
        }
        for b in branches
    ]


def open_account(db: Session, data):
    # validate branch
    branch = db.query(Branch).filter(Branch.branch_id == data.branch_id).first()
    if not branch:
        return {"success": False, "message": "Invalid branch_id"}

    acc_no = _generate_account_number(db)

    acc = Account(
        account_number=acc_no,
        customer_name=data.customer_name,
        email=data.email,
        mobile=data.mobile,
        aadhaar=data.aadhaar,
        pan=data.pan,
        address=data.address,
        account_type=data.account_type,
        initial_deposit=float(data.initial_deposit or 0.0),
        balance=float(data.initial_deposit or 0.0),
        status="ACTIVE",
        branch_id=data.branch_id,
        nominee=getattr(data, "nominee", None),
    )

    db.add(acc)
    db.commit()
    db.refresh(acc)

    if acc.initial_deposit and acc.initial_deposit > 0:
        tx_id = _generate_transaction_id(db)
        tx = Transaction(
            transaction_id=tx_id,
            transaction_type="CREDIT",
            account_number=acc.account_number,
            amount=float(acc.initial_deposit),
            balance_after=float(acc.balance),
        )
        db.add(tx)
        db.commit()

    return {
        "success": True,
        "message": "Account opened successfully",
        "account_number": acc.account_number,
    }


def _account_out(db: Session, acc: Account):
    branch = db.query(Branch).filter(Branch.branch_id == acc.branch_id).first()
    return {
        "account_number": acc.account_number,
        "customer_name": acc.customer_name,
        "branch_id": acc.branch_id,
        "branch_name": branch.branch_name if branch else None,
        "account_type": acc.account_type,
        "balance": acc.balance,
        "status": acc.status,
        "nominee": acc.nominee,
    }


def list_accounts(db: Session):
    accounts = db.query(Account).all()
    return [_account_out(db, a) for a in accounts]


def search_accounts(db: Session, account_number: str | None, mobile: str | None, customer_name: str | None):
    q = db.query(Account)

    if account_number:
        q = q.filter(Account.account_number == account_number)
    if mobile:
        q = q.filter(Account.mobile == mobile)
    if customer_name:
        q = q.filter(Account.customer_name.ilike(f"%{customer_name}%"))

    accounts = q.all()
    return [_account_out(db, a) for a in accounts]


def update_account(db: Session, account_number: str, data):
    acc = db.query(Account).filter(Account.account_number == account_number).first()
    if not acc:
        return {"success": False, "message": "Account not found"}

    # apply updates
    if data.mobile is not None:
        acc.mobile = data.mobile
    if data.email is not None:
        acc.email = data.email
    if data.address is not None:
        acc.address = data.address
    if data.nominee is not None:
        acc.nominee = data.nominee
    if data.account_type is not None:
        acc.account_type = data.account_type

    db.commit()
    db.refresh(acc)
    return {"success": True, "message": "Account updated successfully", "data": _account_out(db, acc)}


def _ensure_not_blocked(acc: Account):
    if acc.status == "CLOSED":
        return False, "Account is CLOSED"
    if acc.status == "FROZEN":
        return False, "Account is FROZEN"
    return True, ""


def deposit(db: Session, account_number: str, amount: float):
    acc = db.query(Account).filter(Account.account_number == account_number).first()
    if not acc:
        return {"success": False, "message": "Account not found"}

    ok, msg = _ensure_not_blocked(acc)
    if not ok:
        return {"success": False, "message": msg}

    amt = float(amount)
    if amt <= 0:
        return {"success": False, "message": "Deposit amount must be > 0"}

    acc.balance = float(acc.balance) + amt

    tx_id = _generate_transaction_id(db)
    tx = Transaction(
        transaction_id=tx_id,
        transaction_type="CREDIT",
        account_number=acc.account_number,
        amount=amt,
        balance_after=float(acc.balance),
    )
    db.add(tx)

    db.commit()
    db.refresh(acc)

    return {"success": True, "message": "Deposit successful", "data": _account_out(db, acc)}


def withdraw(db: Session, account_number: str, amount: float):
    acc = db.query(Account).filter(Account.account_number == account_number).first()
    if not acc:
        return {"success": False, "message": "Account not found"}

    ok, msg = _ensure_not_blocked(acc)
    if not ok:
        return {"success": False, "message": msg}

    amt = float(amount)
    if amt <= 0:
        return {"success": False, "message": "Withdraw amount must be > 0"}

    if float(acc.balance) < amt:
        return {"success": False, "message": "Insufficient balance"}

    acc.balance = float(acc.balance) - amt

    tx_id = _generate_transaction_id(db)
    tx = Transaction(
        transaction_id=tx_id,
        transaction_type="DEBIT",
        account_number=acc.account_number,
        amount=amt,
        balance_after=float(acc.balance),
    )
    db.add(tx)

    db.commit()
    db.refresh(acc)

    return {"success": True, "message": "Withdraw successful", "data": _account_out(db, acc)}


def transfer(db: Session, sender_account_number: str, receiver_account_number: str, amount: float):
    if sender_account_number == receiver_account_number:
        return {"success": False, "message": "Sender and receiver cannot be same"}

    sender = db.query(Account).filter(Account.account_number == sender_account_number).first()
    receiver = db.query(Account).filter(Account.account_number == receiver_account_number).first()

    if not sender or not receiver:
        return {"success": False, "message": "Sender/receiver account not found"}

    ok, msg = _ensure_not_blocked(sender)
    if not ok:
        return {"success": False, "message": f"Sender: {msg}"}

    ok, msg = _ensure_not_blocked(receiver)
    if not ok:
        return {"success": False, "message": f"Receiver: {msg}"}

    amt = float(amount)
    if amt <= 0:
        return {"success": False, "message": "Transfer amount must be > 0"}

    if float(sender.balance) < amt:
        return {"success": False, "message": "Insufficient balance"}

    # Atomic update
    sender.balance = float(sender.balance) - amt
    receiver.balance = float(receiver.balance) + amt

    tx_id_sender = _generate_transaction_id(db)
    tx_sender = Transaction(
        transaction_id=tx_id_sender,
        transaction_type="TRANSFER",
        sender_account_number=sender.account_number,
        receiver_account_number=receiver.account_number,
        account_number=sender.account_number,
        amount=amt,
        balance_after=float(sender.balance),
    )

    tx_id_receiver = _generate_transaction_id(db)
    tx_receiver = Transaction(
        transaction_id=tx_id_receiver,
        transaction_type="TRANSFER",
        sender_account_number=sender.account_number,
        receiver_account_number=receiver.account_number,
        account_number=receiver.account_number,
        amount=amt,
        balance_after=float(receiver.balance),
    )

    db.add(tx_sender)
    db.add(tx_receiver)

    db.commit()
    db.refresh(sender)
    db.refresh(receiver)

    return {
        "success": True,
        "message": "Transfer successful",
        "data": {
            "sender": _account_out(db, sender),
            "receiver": _account_out(db, receiver),
        },
    }


def freeze_account(db: Session, account_number: str):
    acc = db.query(Account).filter(Account.account_number == account_number).first()
    if not acc:
        return {"success": False, "message": "Account not found"}
    if acc.status == "CLOSED":
        return {"success": False, "message": "Cannot freeze CLOSED account"}

    acc.status = "FROZEN"
    db.commit()
    db.refresh(acc)
    return {"success": True, "message": "Account frozen", "data": _account_out(db, acc)}


def close_account(db: Session, account_number: str):
    acc = db.query(Account).filter(Account.account_number == account_number).first()
    if not acc:
        return {"success": False, "message": "Account not found"}

    acc.status = "CLOSED"
    db.commit()
    db.refresh(acc)
    return {"success": True, "message": "Account closed", "data": _account_out(db, acc)}


def reopen_account(db: Session, account_number: str):
    acc = db.query(Account).filter(Account.account_number == account_number).first()
    if not acc:
        return {"success": False, "message": "Account not found"}

    # CLOSED -> ACTIVE is allowed (per your confirmation)
    # FROZEN -> ACTIVE is allowed as well.
    if acc.status == "ACTIVE":
        return {"success": False, "message": "Account is already ACTIVE"}

    if acc.status not in ("FROZEN", "CLOSED"):
        return {"success": False, "message": f"Account cannot be reopened from status {acc.status}"}

    acc.status = "ACTIVE"
    db.commit()
    db.refresh(acc)
    return {"success": True, "message": "Account reopened (ACTIVE)", "data": _account_out(db, acc)}


def get_transactions(db: Session, account_number: str, tx_type: str | None = None):
    q = db.query(Transaction).filter(Transaction.account_number == account_number)
    if tx_type:
        q = q.filter(Transaction.transaction_type == tx_type)
    txs = q.order_by(Transaction.created_at.desc()).all()

    return [
        {
            "transaction_id": t.transaction_id,
            "transaction_type": t.transaction_type,
            "account_number": t.account_number,
            "sender_account_number": t.sender_account_number,
            "receiver_account_number": t.receiver_account_number,
            "amount": t.amount,
            "balance_after": t.balance_after,
            "created_at": t.created_at,
        }
        for t in txs
    ]

