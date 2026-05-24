# app/models/employee.py
from sqlalchemy import Column, Integer, String
from app.backend.db import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    employee_id = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    phone = Column(String)
    department = Column(String)
    branch_id = Column(String)
    salary = Column(Integer)