from pydantic import BaseModel
from typing import Optional

class BranchCreate(BaseModel):
    branch_name: str
    city: str
    state: str
    address: str
    contact: str


class BranchOut(BaseModel):
    id: int
    branch_id: str
    branch_name: str
    city: str
    state: str
    contact: str
    manager_name: Optional[str] = None   # ✅ FIX HERE

    class Config:
        from_attributes = True