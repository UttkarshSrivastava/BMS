from fastapi import APIRouter, Depends
from fastapi import Query
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.services.account_service import (
    get_all_branches_for_dropdown,
    open_account,
    list_accounts,
    search_accounts,
    update_account,
    deposit,
    withdraw,
    transfer,
    freeze_account,
    close_account,
    reopen_account,
    get_transactions,
)


from app.schemas.account_schema import AccountCreate, AccountUpdate

router = APIRouter(prefix="/accounts", tags=["Accounts"])


@router.get("/branches")
def branches_dropdown(db: Session = Depends(get_db)):
    return get_all_branches_for_dropdown(db)


@router.post("/create")
def create_account_api(data: AccountCreate, db: Session = Depends(get_db)):
    return open_account(db, data)


@router.get("/all")
def all_accounts(db: Session = Depends(get_db)):
    return list_accounts(db)


@router.get("/search")
def search_accounts_api(
    account_number: str | None = Query(default=None),
    mobile: str | None = Query(default=None),
    customer_name: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return search_accounts(db, account_number, mobile, customer_name)


@router.put("/{account_number}")
def edit_account_api(account_number: str, data: AccountUpdate, db: Session = Depends(get_db)):
    return update_account(db, account_number, data)


@router.post("/deposit")
def deposit_api(payload: dict, db: Session = Depends(get_db)):
    return deposit(db, payload.get("account_number"), payload.get("amount"))


@router.post("/withdraw")
def withdraw_api(payload: dict, db: Session = Depends(get_db)):
    return withdraw(db, payload.get("account_number"), payload.get("amount"))


@router.post("/transfer")
def transfer_api(payload: dict, db: Session = Depends(get_db)):
    return transfer(
        db,
        payload.get("sender_account_number"),
        payload.get("receiver_account_number"),
        payload.get("amount"),
    )


@router.post("/{account_number}/freeze")
def freeze_api(account_number: str, db: Session = Depends(get_db)):
    return freeze_account(db, account_number)


@router.post("/{account_number}/close")
def close_api(account_number: str, db: Session = Depends(get_db)):
    return close_account(db, account_number)


@router.post("/{account_number}/reopen")
def reopen_api(account_number: str, db: Session = Depends(get_db)):
    return reopen_account(db, account_number)


@router.get("/transactions/{account_number}")
def transactions_api(
    account_number: str,
    tx_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    return {"history": get_transactions(db, account_number, tx_type=tx_type)}


@router.get("/statements/{account_number}")
def statements_api(account_number: str, db: Session = Depends(get_db)):
    txs = get_transactions(db, account_number)
    return {"mini_statement": txs[:10], "full_statement": txs}

