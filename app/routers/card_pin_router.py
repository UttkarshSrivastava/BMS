from fastapi import APIRouter, Depends, HTTPException, Header, Query
from sqlalchemy.orm import Session
from datetime import datetime
import secrets

from app.backend.db import get_db
from app.models.card_request_model import CardRequest
from app.models.account import Account
from app.models.employee import Employee

from app.auth.auth_handler import verify_token

router = APIRouter(prefix="/card", tags=["Card PIN & Issuance"])


def get_current_customer(authorization: str = Header(None), db: Session = Depends(get_db)) -> dict:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization missing")
    token = authorization.replace("Bearer ", "").strip()
    payload = verify_token(token)

    # customer login in this repo doesn't return a token in /api/login,
    # but some flows store access_token anyway; we'll support both.
    account_number = (
        payload.get("account_number")
        or payload.get("acc")
        or payload.get("sub")
    )

    if not account_number:
        # fallback: allow using token as employee_id mapping? not safe; block.
        raise HTTPException(status_code=401, detail="Token has no account_number")

    acc = db.query(Account).filter(Account.account_number == account_number).first()
    if not acc:
        raise HTTPException(status_code=404, detail="Account not found")

    return {
        "account_number": acc.account_number,
        "branch_id": acc.branch_id,
        "customer_name": acc.customer_name,
        "id": acc.id if hasattr(acc, "id") else None,
    }


def _generate_16_digit_number(existing: set[str]) -> str:
    # Generate until unique within DB (best effort)
    for _ in range(1000):
        n = ''.join(str(secrets.randbelow(10)) for _ in range(16))
        if n not in existing:
            return n
    raise HTTPException(status_code=500, detail="Could not generate unique card number")


def _generate_4_digit_pin() -> str:
    return str(secrets.randbelow(10000)).zfill(4)


@router.post("/issue-pin")
def issue_pin_for_approved_card(
    db: Session = Depends(get_db),
    customer: dict = Depends(get_current_customer),
):
    # Find latest approved request
    req = (
        db.query(CardRequest)
        .filter(CardRequest.account_number == customer["account_number"])
        .filter(CardRequest.status == "approved")
        .order_by(CardRequest.created_at.desc())
        .first()
    )

    if not req:
        raise HTTPException(status_code=404, detail="No approved card request found")

    # If pin already issued, return it
    if getattr(req, "pin", None):
        return {
            "success": True,
            "message": "PIN already generated",
            "request_id": req.id,
            "card_number": getattr(req, "card_number", None),
            "pin": req.pin,
        }

    # Best effort: generate if columns exist
    # Note: this router expects CardRequest model to contain card_number and pin columns.
    if not hasattr(CardRequest, "card_number") or not hasattr(CardRequest, "pin"):
        raise HTTPException(
            status_code=500,
            detail="PIN issuance not configured: CardRequest model missing card_number/pin"
        )

    existing = set()
    try:
        existing_rows = db.query(CardRequest.card_number).all()
        existing = {row[0] for row in existing_rows if row[0]}
    except Exception:
        existing = set()

    req.card_number = _generate_16_digit_number(existing)
    req.pin = _generate_4_digit_pin()
    req.pin_generated_at = datetime.utcnow()
    db.commit()
    db.refresh(req)

    return {
        "success": True,
        "message": "PIN generated successfully",
        "request_id": req.id,
        "card_number": req.card_number,
        "pin": req.pin,
    }


@router.get("/my-card-pin")
def my_card_pin(
    db: Session = Depends(get_db),
    customer: dict = Depends(get_current_customer),
):
    req = (
        db.query(CardRequest)
        .filter(CardRequest.account_number == customer["account_number"])
        .filter(CardRequest.status == "approved")
        .order_by(CardRequest.created_at.desc())
        .first()
    )

    if not req:
        return {"success": True, "available": False}

    pin = getattr(req, "pin", None)
    card_number = getattr(req, "card_number", None)

    if not pin:
        return {"success": True, "available": False}

    return {
        "success": True,
        "available": True,
        "request_id": req.id,
        "card_number": card_number,
        "pin": pin,
        "pin_generated_at": req.pin_generated_at,
    }

