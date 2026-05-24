# app/services/employee_service.py
import random
from sqlalchemy.orm import Session
from app.models.employee import Employee


def generate_emp_id():
    return str(random.randint(10000, 99999))


def create_employee(db: Session, data):
    emp = Employee(
        employee_id=generate_emp_id(),
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        phone=data.phone,
        department=data.department,
        branch_id=data.branch_id,
        salary=data.salary
    )

    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


def get_all_employees(db: Session):
    return db.query(Employee).all()