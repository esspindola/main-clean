from fastapi import APIRouter, Form, Depends, HTTPException, Body
from config.database import get_db_connection

from repositories.user_repositories import UserRepository
from services.auth_service import AuthService
from utils.dependencies import get_current_token, get_current_user
from config.database import get_postgres_db

router = APIRouter(prefix="/api/auth", tags=["auth"])

def _get_auth_service(db=Depends(get_db_connection))->AuthService:
    db_conn = next(db) # extract connection
    auth_repo = UserRepository(db_conn) # postgres is default db
    return AuthService(auth_repo)

@router.post("/login")
def login(email: str = Form(...),
          password: str = Form(...),
          auth_service = Depends(_get_auth_service)
          ):
    result = auth_service.login(email, password)
    return result

@router.post('/register')
def register(firstName: str=Form(...),
             lastName: str=Form(...),
             email: str = Form(...),
             password: str = Form(...),
             phone: str = Form(None),
             auth_service = Depends(_get_auth_service)
             ):
    result = auth_service.register(firstName, lastName, email, password, phone)
    return result

@router.post('/logout')
def logout(token: str = Depends(get_current_token)):
    return token

@router.get('/me')
def get_current_user(user = Depends((get_current_user))):
    return user

@router.get('/users')
def list_users(current_user = Depends(get_current_user), auth_service=Depends(_get_auth_service)):
    if not current_user.get('is_admin'):
        raise HTTPException(status_code= 403,detail="Acess denied")
    return auth_service.get_list_users()

@router.get('/profile/{user_id}')
def get_profile(user_id: int,
                # current_user=Depends(get_current_user),
                auth_service=Depends(_get_auth_service)):
    # Thinking..
    # if user_id != current_user.get('user_id') and not current_user.get('is_admin'):
    #     raise HTTPException(status_code=403, detail="Access denied")
    return auth_service.get_profile_user(user_id)

@router.put('/profile/{user_id}')
def update_profile(user_id: int, updates: dict=Body(...),
                   current_user = Depends(get_current_user), auth_service=Depends(_get_auth_service)):
    if not current_user.get('is_admin'):
        raise HTTPException(status_code=403, detail='Acess denied')
    return auth_service.update_profile(user_id, updates)
