# app/routers/branch_router.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.backend.db import get_db
from app.schemas.branch_schema import BranchCreate
from app.schemas.branch_schema import BranchOut
from app.services.branch_service import (
    create_branch,
    get_all_branches,
    assign_manager
)

router = APIRouter(prefix="/branch", tags=["Branch"])


@router.post("/create")
def create_branch_api(data: BranchCreate, db: Session = Depends(get_db)):
    return create_branch(db, data)


@router.get("/all", response_model=list[BranchOut])
def get_branches(db: Session = Depends(get_db)):
    return get_all_branches(db)


@router.post("/{branch_id}/assign-manager")
def assign_manager_api(branch_id: str, manager_name: str, db: Session = Depends(get_db)):
    result = assign_manager(db, branch_id, manager_name)

    if not result:
        return {"success": False, "message": "Branch not found"}

    return {"success": True, "message": "Manager assigned", "data": result}