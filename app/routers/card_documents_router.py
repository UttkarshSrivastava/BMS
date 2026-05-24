from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi import Form
from sqlalchemy.orm import Session
from datetime import datetime
import os
import uuid

from app.backend.db import get_db
from app.models.card_request_model import CardRequest
from app.models.account import Account


router = APIRouter(prefix="/card", tags=["Card Documents"])


def _ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def _save_upload(upload: UploadFile, folder: str) -> str:
    _ensure_dir(folder)
    # keep original extension
    _, ext = os.path.splitext(upload.filename or "")
    safe_ext = ext if ext else ""
    filename = f"{uuid.uuid4().hex}{safe_ext}"
    full_path = os.path.join(folder, filename)

    with open(full_path, "wb") as f:
        content = upload.file.read()
        f.write(content)

    return filename


@router.post("/upload-documents")
async def upload_documents(
    account_number: str = Form(...),
    request_id: int | None = Form(None),
    # draft fields (may be used to create CardRequest if missing)
    card_type: str | None = Form(None),
    network: str | None = Form(None),
    card_variant: str | None = Form(None),
    credit_limit: str | None = Form(None),
    address: str | None = Form(None),
    city: str | None = Form(None),
    pincode: str | None = Form(None),

    aadhaar_document: UploadFile | None = File(None),
    pan_document: UploadFile | None = File(None),
    income_proof: UploadFile | None = File(None),
    photo: UploadFile | None = File(None),
    db: Session = Depends(get_db)
):
    # Prefer updating the request row created in step 1
    req = None
    if request_id is not None:
        req = db.query(CardRequest).filter(CardRequest.id == request_id).first()

    # Fallback: Find latest card request for this account
    if req is None:
        req = (
            db.query(CardRequest)
            .filter(CardRequest.account_number == account_number)
            .order_by(CardRequest.created_at.desc())
            .first()
        )

    if not req:
        # Create CardRequest on the fly using draft fields sent by the client.
        user = db.query(Account).filter(Account.account_number == account_number).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        req = CardRequest(
            user_id=user.id,
            branch_id=user.branch_id,
            full_name=user.customer_name,
            account_number=user.account_number,
            mobile=user.mobile,
            email=user.email,
            card_type=card_type,
            network=network,
            card_variant=card_variant,
            credit_limit=credit_limit,
            address=address,
            city=city,
            pincode=pincode,
            status="Pending At Employee",
            employee_status="Pending",
            manager_status="Pending",
            admin_status="Pending",
            created_at=datetime.utcnow(),
        )
        db.add(req)
        db.commit()
        db.refresh(req)

    # Store uploads into app/static/images (matches existing static folder)
    uploads_dir = os.path.join("app", "static", "images")

    if aadhaar_document is not None:
        req.aadhaar_document = _save_upload(aadhaar_document, uploads_dir)

    if pan_document is not None:
        req.pan_document = _save_upload(pan_document, uploads_dir)

    if income_proof is not None:
        req.income_proof = _save_upload(income_proof, uploads_dir)

    if photo is not None:
        req.photo = _save_upload(photo, uploads_dir)

    db.commit()
    db.refresh(req)

    return {
        "success": True,
        "message": "Documents uploaded successfully",
        "request_id": req.id,
        "saved": {
            "aadhaar_document": req.aadhaar_document,
            "pan_document": req.pan_document,
            "income_proof": req.income_proof,
            "photo": req.photo,
        },
    }


