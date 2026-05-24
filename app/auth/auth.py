from pydantic import BaseModel
from datetime import datetime

from app.auth.auth_handler import create_token


# -------------------
# LOGIN MODEL
# -------------------
class LoginRequest(BaseModel):
    username: str
    password: str
    role: str


# -------------------
# AUTH LOGIC
# -------------------
def authenticate_user(data: LoginRequest):
    # ADMIN LOGIN
    if data.role == "admin":
        if data.username == "admin" and data.password == "1234":
            token = create_token(
                {
                    "sub": "admin",
                    "employee_id": "admin",
                    "role": "admin",
                    "iat": datetime.utcnow().timestamp(),
                }
            )
            return {
                "success": True,
                "role": "admin",
                "access_token": token,
                "message": "Login successful",
            }
        return {
            "success": False,
            "message": "Invalid admin credentials",
        }

    return {
        "success": False,
        "message": "Role not supported",
    }

