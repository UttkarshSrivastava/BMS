# app/models/branch.py

from sqlalchemy import Column, Integer, String
from app.backend.db import Base

class Branch(Base):
    __tablename__ = "branches"

    id = Column(Integer, primary_key=True, index=True)
    branch_id = Column(String, unique=True, index=True)
    branch_name = Column(String)
    city = Column(String)
    state = Column(String)
    address = Column(String)
    contact = Column(String)
    manager_name = Column(String, nullable=True)