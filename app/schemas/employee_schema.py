from pydantic import BaseModel

class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    department: str
    salary: int
    branch_id: str


class EmployeeTransfer(BaseModel):
    employee_id: str
    new_branch_id: str


class EmployeeOut(BaseModel):
    id: int
    employee_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    department: str
    salary: int
    branch_id: str
    branch_name: str

    class Config:
        from_attributes = True