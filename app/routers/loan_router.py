from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.backend.db import get_db

from app.models.loan_request import LoanRequest

router = APIRouter(
    prefix="/loan",
    tags=["Loan"]
)


@router.post("/apply")
def apply_loan(
    data: dict,
    db: Session = Depends(get_db)
):

    new_loan = LoanRequest(

        account_number =
        data.get("account_number"),

        customer_name =
        data.get("customer_name"),

        branch_id =
        data.get("branch_id"),

        loan_type =
        data.get("loan_type"),

        loan_amount =
        float(data.get("loan_amount")),

        duration_months =
        int(data.get("duration_months")),

        interest_rate =
        float(data.get("interest_rate")),

        monthly_emi =
        float(data.get("monthly_emi")),

        employee_status =
        "Pending",

        manager_status =
        "Waiting",

        admin_status =
        "Waiting",

        overall_status =
        "Pending"

    )

    db.add(new_loan)

    db.commit()

    db.refresh(new_loan)

    return {
        "message":"Loan Applied Successfully"
    }


@router.get("/status/{account_number}")
def loan_status(
    account_number: str,
    db: Session = Depends(get_db)
):

    loans = db.query(
        LoanRequest
    ).filter(
        LoanRequest.account_number
        == account_number
    ).all()

    return loans