from repositories.user_repositories import UserRepository
from fastapi import HTTPException
from typing import Optional
from datetime import datetime, timedelta
import jwt
from config.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
        self.blacklisted_token = set()

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def login(self, email: str, password: str):
        # Validations
        if not email or not password:
            raise HTTPException(status_code=400, detail="Email and password are required")

        # Finding by user
        user = self.user_repo.find_by_credentials(email, password)

        # Business rule
        if not user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Generates token
        token = self.create_access_token({"user_id": user["id"]})

        return {"user": user, "token": token}

    def register(self, firstName: str, lastName: str, email: str, password: str, phone: str = None):
        """
        Where will register user
        :param email: string
        :param password: string
        :param fullName: string
        :param phone: string
        :return:

        Also, will make validations of email existent
        """
        # Validation input data
        if not email or not password or not firstName or not lastName:
            raise HTTPException(status_code=400, detail="Email, password and fullname are required")
        # Check if user already exists
        user = self.user_repo.find_by_email(email)
        if user:
            raise HTTPException(status_code=409, detail="Email already exists")
        # Create user
        user_id = self.user_repo.create_user(firstName, lastName,email, password, phone)

        return self.login(email, password)

    def logout(self, token:str):
        self.blacklisted_token.add(token)
        return {"success": True, "message": "Successful logout"}

    def verify_token(self, token: str):
        """
        Objective: verify if token is valid (for endpoints /api/auth/me)
        :param token:
        :return:
        """
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id = payload.get("user_id")
            if not user_id:
                raise HTTPException(status_code=401, detail="Invalid Token")
            user = self.user_repo.find_by_user_id(user_id)
            if not user:
                raise HTTPException(status_code=401, detail="User not found")

            return user
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid Token")

    def is_token_blacklisted(self, token:str) -> bool:
        return token in self.blacklisted_token

    def get_list_users(self):
        users = self.user_repo.find_all_users()
        return {'success':True, 'users': users}

    def get_profile_user(self, user_id):
        user = self.user_repo.find_by_user_id(user_id)
        return {'success': True, 'user': user}

    def update_profile(self, user_id: int, updates: dict):
        user = self.user_repo.update_profile(user_id, updates)
        return {'success': True, 'user': user}
