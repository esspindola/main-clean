from fastapi import APIRouter, Form, Depends, HTTPException
from config.database import get_db_connection

from repositories.user_repositories import UserRepository
from services.auth_service import AuthService
from utils.dependencies import get_current_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

def _get_auth_service(db=Depends(get_db_connection))->AuthService:
    auth_repo = UserRepository(db) # postgres is default db
    return AuthService(auth_repo)

@router.post("/login")
def login(email: str = Form(...),
          password: str = Form(...),
          auth_service = Depends(_get_auth_service)
          ):
    result = auth_service.login(email, password)
    return result

@router.post('/register')
def register(email: str = Form(...),
             password: str = Form(...),
             fullName: str = Form(...),
             phone: str = Form(None),
             auth_service = Depends(_get_auth_service)
             ):
    result = auth_service.register(email, password, fullName, phone)
    return result

@router.post('/logout')
def logout(token: str = Depends(get_current_token)):
    return token

@router.get('/me')
def get_current_user(user = Depends((get_current_user))):
    return user