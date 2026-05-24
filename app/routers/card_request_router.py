# app/routers/card_request_router.py

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import datetime

from app.backend.db import get_db

from app.models.card_request_model import CardRequest
from app.models.account import Account

router = APIRouter(
    prefix="/card",
    tags=["Card Requests"]
)

# ======================================================
# APPLY NEW CARD
# ======================================================

@router.post("/apply")

def apply_new_card(
    request_data: dict,
    db: Session = Depends(get_db)
):

    try:

        account_number = request_data.get("account_number")

        if not account_number:

            raise HTTPException(
                status_code=400,
                detail="Account number required"
            )

        # FIND USER

        user = db.query(Account).filter(
            Account.account_number == account_number
        ).first()

        if not user:

            raise HTTPException(
                status_code=404,
                detail="User not found"
            )

        # CREATE REQUEST

        new_request = CardRequest(

            user_id=user.id,
            branch_id=user.branch_id,

            full_name=user.customer_name,
            account_number=user.account_number,
            mobile=user.mobile,
            email=user.email,

            card_type=request_data.get("card_type"),
            network=request_data.get("network"),
            card_variant=request_data.get("card_variant"),
            credit_limit=request_data.get("credit_limit"),

            address=request_data.get("address"),
            city=request_data.get("city"),
            pincode=request_data.get("pincode"),

            # DOCUMENTS (stored as string filenames/metadata)
            aadhaar_document=request_data.get("aadhaar_document"),
            pan_document=request_data.get("pan_document"),
            income_proof=request_data.get("income_proof"),
            photo=request_data.get("photo"),

            status="Pending At Employee",
            employee_status="Pending",
            manager_status="Pending",
            admin_status="Pending",

            created_at=datetime.utcnow()

        )

        db.add(new_request)
        db.commit()
        db.refresh(new_request)

        return {

            "success": True,
            "message": "Card request submitted successfully",
            "request_id": new_request.id

        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# ======================================================
# MY CARD REQUESTS
# ======================================================

@router.get("/my-requests/{account_number}")

def my_card_requests(
    account_number: str,
    db: Session = Depends(get_db)
):

    try:

        requests = db.query(CardRequest).filter(
            CardRequest.account_number == account_number
        ).order_by(
            CardRequest.created_at.desc()
        ).all()

        all_requests = []

        for req in requests:

            all_requests.append({

                "request_id": req.id,
                "card_type": req.card_type,
                "network": req.network,
                "variant": req.card_variant,
                "status": req.status,
                "employee_status": req.employee_status,
                "manager_status": req.manager_status,
                "admin_status": req.admin_status,
                "created_at": req.created_at,
                "aadhaar_document": req.aadhaar_document,
                "pan_document": req.pan_document,
                "income_proof": req.income_proof,
                "photo": req.photo

            })

        return {

            "success": True,
            "data": all_requests

        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

# ======================================================
# VIEW SINGLE REQUEST
# ======================================================

@router.get("/view/{request_id}")

def view_single_request(
    request_id: int,
    db: Session = Depends(get_db)
):

    try:

        request_data = db.query(CardRequest).filter(
            CardRequest.id == request_id
        ).first()

        if not request_data:

            raise HTTPException(
                status_code=404,
                detail="Request not found"
            )

        return {

            "success": True,

            "data": {

                "request_id": request_data.id,

                "full_name": request_data.full_name,
                "account_number": request_data.account_number,
                "mobile": request_data.mobile,
                "email": request_data.email,

                "card_type": request_data.card_type,
                "network": request_data.network,
                "card_variant": request_data.card_variant,
                "credit_limit": request_data.credit_limit,

                "address": request_data.address,
                "city": request_data.city,
                "pincode": request_data.pincode,

                "status": request_data.status,

                "employee_status": request_data.employee_status,
                "manager_status": request_data.manager_status,
                "admin_status": request_data.admin_status,

                "created_at": request_data.created_at,

                "aadhaar_document": request_data.aadhaar_document,
                "pan_document": request_data.pan_document,
                "income_proof": request_data.income_proof,
                "photo": request_data.photo

            }

        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )