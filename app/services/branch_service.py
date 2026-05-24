import random
from sqlalchemy.orm import Session
from app.models.branch import Branch


def generate_branch_id():
    return str(random.randint(100000, 999999))


def create_branch(db: Session, data):

    while True:
        bid = generate_branch_id()
        exists = db.query(Branch).filter(Branch.branch_id == bid).first()
        if not exists:
            break

    branch = Branch(
        branch_id=bid,
        branch_name=data.branch_name,
        city=data.city,
        state=data.state,
        address=data.address,
        contact=data.contact,
        manager_name=""   # ✅ FIX: empty string instead of None
    )

    db.add(branch)
    db.commit()
    db.refresh(branch)
    return branch


def get_all_branches(db: Session):
    branches = db.query(Branch).all()

    # ✅ SAFE OUTPUT CLEANING
    result = []
    for b in branches:
        result.append({
            "id": b.id,
            "branch_id": b.branch_id,
            "branch_name": b.branch_name,
            "city": b.city,
            "state": b.state,
            "contact": b.contact,
            "manager_name": b.manager_name or ""
        })

    return result


def assign_manager(db: Session, branch_id: str, manager_name: str):
    branch = db.query(Branch).filter(Branch.branch_id == branch_id).first()
    if not branch:
        return None

    branch.manager_name = manager_name
    db.commit()
    db.refresh(branch)

    return {
        "branch_id": branch.branch_id,
        "manager_name": branch.manager_name
    }