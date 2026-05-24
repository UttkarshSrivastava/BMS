from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from app.auth.auth import authenticate_user, LoginRequest
from app.services.login_service import authenticate_branch_employee
from app.services.branch_manager_service import authenticate_branch_manager

# ---------------- DB INIT ----------------
from app.backend.db import Base, engine
from app.models.branch import Branch
from app.models.employee import Employee
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.signup_model import SignupUser
from app.models.account_request import AccountRequest 
from app.models.loan_request import LoanRequest
from app.models.card_request_model import CardRequest

Base.metadata.create_all(bind=engine)

# ---------------- APP ----------------
app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- STATIC + TEMPLATES ----------------
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# ---------------- PAGES ----------------
@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )

@app.get("/signup")
def page(request: Request):
    return templates.TemplateResponse(
        "signup.html",
        {"request": request}
    )

@app.get("/branch-open-account-request/dashboard")
def open_account_request(request: Request):
    return templates.TemplateResponse(
        "employeeaccountrequest.html",
        {"request": request}
    )

@app.get("/aftersignup.html")
def aftersignup_page(request: Request):
    return templates.TemplateResponse(
        "aftersignup.html",
        {"request": request}
    )

@app.get("/employee-loans -request/page")
def loan_request_employee(request: Request):
    return templates.TemplateResponse(
        "employeeloanrequest.html",
        {"request": request}
    )

# ---------------- BRANCH MANAGER PAGES ----------------
@app.get("/branch-manager/dashboard")
def branch_manager_dashboard(request: Request, name: str | None = None):
    return templates.TemplateResponse(
        "branch_manager_dashboard.html",
        {
            "request": request,
            "name": name
        }
    )

@app.get("/branch-manager-account/dashboard")
def branch_manager_account_dashboard(request: Request, name: str | None = None):
    return templates.TemplateResponse(
        "branch_manager_open_account.html",
        {
            "request": request,
            "name": name
        }
    )

@app.get("/branch-manager-card-requests")
def branch_manager_card_requests_page(request: Request, name: str | None = None):
    return templates.TemplateResponse(
        "branch_manager_card_requests.html",
        {
            "request": request,
            "name": name
        }
    )


@app.get("/admin-open-account/dashboard")
def admin_open_account_dashboard(request: Request, name: str | None = None):
    return templates.TemplateResponse(
        "admin_open_account.html",
        {
            "request": request,
            "name": name
        }
    )

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )

@app.get("/admin")
def admin_page(request: Request):
    return templates.TemplateResponse(
        "admin.html",
        {"request": request}
    )

@app.get("/user")
def user_page(request: Request):
    return templates.TemplateResponse(
        "user.html",
        {"request": request}
    )

@app.get("/branch/manage")
def branch_manage(request: Request):
    return templates.TemplateResponse(
        "branchmanage.html",
        {"request": request}
    )

# ---------------- EMPLOYEE PAGES ----------------
@app.get("/employees/manage")
def manage_employees(request: Request):
    return templates.TemplateResponse(
        "vb.html",
        {"request": request}
    )

@app.get("/employees/dashboard")
def employee_dashboard(request: Request):
    return templates.TemplateResponse(
        "showemploye.html",
        {"request": request}
    )

@app.get("/employees/branch-dashboard")
def branch_employee_dashboard(request: Request):
    return templates.TemplateResponse(
        "bankemployee.html",
        {"request": request}
    )

@app.get("/employees/add")
def add_employee_page(request: Request):
    return templates.TemplateResponse(
        "NE.html",
        {"request": request}
    )

@app.get("/employees/transfer")
def transfer_employee_page(request: Request):
    return templates.TemplateResponse(
        "transfer_employee.html",
        {"request": request}
    )

@app.get("/Account/operation")
def Account_operation_page(request: Request):
    return templates.TemplateResponse(
        "manage_accounts.html",
        {"request": request}
    )

@app.get("/employee-manager/operation")
def Employee_Manager_page(request: Request):
    return templates.TemplateResponse(
        "branch_manager_employees.html",
        {"request": request}
    )

@app.get("/account-manager/operation")
def account_Manager_page(request: Request):
    return templates.TemplateResponse(
        "managersaccounts.html",
        {"request": request}
    )

@app.get("/branch-employee/accounts")
def branch_employee_accounts_page(request: Request):
    return templates.TemplateResponse(
        "branchaccounts.html",
        {"request": request}
    )

@app.get("/apply-loan/user")
def apply_loan_accounts_user(request: Request):
    return templates.TemplateResponse(
        "apply-loan.html",
        {"request": request}
    )

@app.get("/apply-card/user")
def apply_card_user(request: Request):
    return templates.TemplateResponse(
        "apply card.html",
        {"request": request}
    )

@app.get("/loan-status/user")
def loan_status_user(request: Request):
    return templates.TemplateResponse(
        "loan-status.html",
        {"request": request}
    )
    
@app.get("/card-documents")
def card_documents_user(request: Request):
    return templates.TemplateResponse(
        "card-documents.html",
        {"request": request}
    )

@app.get("/branch-employee-card-requests")
def card_request_employee(request: Request):
    return templates.TemplateResponse(
        "branch_employee_card_requests.html",
        {"request": request}
    )

# ---------------- LOGIN API ----------------

@app.post("/api/login")
def api_login(data: LoginRequest):

    # ---------------- ADMIN LOGIN ----------------
    if data.role == "admin":
        return authenticate_user(data)

    # ---------------- CUSTOMER LOGIN ----------------
    if data.role == "user":

        from app.backend.db import get_db

        db = next(get_db())

        try:
            branch_id = data.username.strip()
            account_number = data.password.strip()

            acc = (
                db.query(Account)
                .filter(Account.branch_id == branch_id)
                .filter(Account.account_number == account_number)
                .first()
            )

            if not acc:
                return {
                    "success": False,
                    "message": "Invalid customer credentials"
                }

            if acc.status in ("FROZEN", "CLOSED"):
                return {
                    "success": False,
                    "message": f"Account status is {acc.status}"
                }

            return {
                "success": True,
                "role": "user",
                "customer": {
                    "account_number": acc.account_number,
                    "customer_name": acc.customer_name,
                    "branch_id": acc.branch_id,
                    "balance": acc.balance,
                },
                "access_token": None,
            }

        finally:
            db.close()

    # ---------------- SIGNUP USER LOGIN ----------------
    if data.role == "signup_user":

        from app.backend.db import get_db

        db = next(get_db())

        try:

            user = (
                db.query(SignupUser)
                .filter(SignupUser.name == data.username)
                .filter(SignupUser.password == data.password)
                .first()
            )

            if not user:
                return {
                    "success": False,
                    "message": "Invalid signup user credentials"
                }

            return {
                "success": True,
                "role": "signup_user",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email
                }
            }

        finally:
            db.close()

    # ---------------- BRANCH EMPLOYEE LOGIN ----------------
    if data.role == "branch_employee":

        from app.backend.db import get_db

        db = next(get_db())

        try:
            return authenticate_branch_employee(
                db,
                data.username,
                data.password
            )

        finally:
            db.close()

    # ---------------- BRANCH MANAGER LOGIN ----------------
    if data.role == "branch_manager":

        from app.backend.db import get_db

        db = next(get_db())

        try:
            return authenticate_branch_manager(
                db,
                data.username,
                data.password
            )

        finally:
            db.close()

    # ---------------- LEGACY MANAGER SUPPORT ----------------
    if data.role in ("manager", "branch_manager"):

        from app.backend.db import get_db

        db = next(get_db())

        try:
            return authenticate_branch_manager(
                db,
                data.username,
                data.password
            )

        finally:
            db.close()

    return {
        "success": False,
        "message": "Role not supported"
    }

# ---------------- ROUTERS ----------------
from app.routers.branch_router import router as branch_router
from app.routers.employee_router import router as employee_router
from app.routers.auth_router import router as auth_router
from app.routers.account_router import router as account_router
from app.routers.customer_router import router as customer_router
from app.routers.signup_router import router as signup_router

from app.routers.manager_dashboard_router import router as branch_manager_dashboard_router
from app.routers.employee_manager_router import router as employee_manager_router
from app.routers.manager_accounts_router import router as manager_accounts_router
from app.routers.branch_employee_dashboard import router as branch_employee_dashboard_router
from app.routers.branch_employee_accounts_router import router as branch_employee_accounts_router
from app.routers.admin_dashboard_router import router as admin_dashboard_router
from app.routers.open_account import router as open_account_router
from app.routers.branch_employee_open_account_router import router as employee_open_account_router
from app.routers.branch_manager_open_account_router import router as manager_open_account_router
from app.routers.admin_open_account_router import router as admin_router
from app.routers.loan_router import router as loan_router
from app.routers.employee_loan_router import router as employee_loan_router
from app.routers.card_request_router import router as card_request_router

# ==========================================
# INCLUDE ROUTERS
# ==========================================
app.include_router(branch_router)
app.include_router(employee_router)
app.include_router(auth_router)
app.include_router(account_router)
app.include_router(customer_router)
app.include_router(branch_manager_dashboard_router)
app.include_router(employee_manager_router)
app.include_router(manager_accounts_router)
app.include_router(branch_employee_dashboard_router)
app.include_router(branch_employee_accounts_router)
app.include_router(admin_dashboard_router)
app.include_router(signup_router)
app.include_router(open_account_router)
app.include_router(employee_open_account_router)
app.include_router(manager_open_account_router)
app.include_router(admin_router)
app.include_router(loan_router)
app.include_router(employee_loan_router)
app.include_router(card_request_router)
from app.routers.card_documents_router import router as card_documents_router
app.include_router(card_documents_router)
from app.routers.branch_employee_card_requests_router import router as branch_employee_card_requests_router
app.include_router(branch_employee_card_requests_router)



from app.routers.branch_manager_card_requests_router import router as branch_manager_card_requests_router
app.include_router(branch_manager_card_requests_router)

from app.routers.admin_card_requests_router import router as admin_card_requests_router
app.include_router(admin_card_requests_router)


@app.get("/admin/card-requests")
def admin_card_requests_page(request: Request):
    return templates.TemplateResponse(
        "admin_card_requests.html",
        {"request": request}
    )


# ---------------- ACCOUNT QUERIES ROUTER ----------------

try:
    from app.routers.account_queries_router import router as account_queries_router

    app.include_router(account_queries_router)

except Exception:
    pass