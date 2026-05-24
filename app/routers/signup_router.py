from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.backend.db import SessionLocal
from app.models.signup_model import SignupUser


router = APIRouter()


# DATABASE CONNECTION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# SIGNUP API
@router.post("/signup")
async def signup_user(
    request: Request,
    name: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
    contact: str = Form(...),
    db: Session = Depends(get_db)
):

    # CREATE NEW USER
    new_user = SignupUser(
        name=name,
        password=password,
        email=email,
        contact=contact
    )

    # SAVE TO DATABASE
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # REDIRECT AFTER SIGNUP
    return RedirectResponse(url="/", status_code=303)