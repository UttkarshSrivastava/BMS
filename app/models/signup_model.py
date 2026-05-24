from sqlalchemy import Column, Integer, String
from app.backend.db import Base


class SignupUser(Base):
    __tablename__ = "signup_users"

    # PRIMARY KEY
    id = Column(Integer, primary_key=True, index=True)

    # USERNAME
    name = Column(String, nullable=False)

    # PASSWORD
    password = Column(String, nullable=False)

    # EMAIL
    email = Column(String, unique=True, nullable=False)

    # CONTACT NUMBER
    contact = Column(String, nullable=False)