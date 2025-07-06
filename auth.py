from fastapi import Request, Response
from itsdangerous import URLSafeSerializer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models import User
from settings import settings

class AuthManager:
    def __init__(self, cookie_name: str, secret_key: str):
        self.cookie_name = cookie_name
        self.serializer = URLSafeSerializer(secret_key)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash_password(self, password: str):
        return self.pwd_context.hash(password)

    def verify_password(self, plain: str, hashed: str):
        return self.pwd_context.verify(plain, hashed)

    def create_session_token(self, username: str):
        return self.serializer.dumps(username)

    def get_username_from_session_token(self, token: str):
        try:
            return self.serializer.loads(token)
        except Exception:
            return None

    def get_current_user(self, request: Request, db: Session):
        token = request.cookies.get(self.cookie_name)
        if not token:
            return None
        username = self.get_username_from_session_token(token)
        if not username:
            return None
        return db.query(User).filter(User.username == username).first()

    def login_user(self, response: Response, username: str, remember: bool = False):
        token = self.create_session_token(username)
        max_age = 60 * 60 * 24 * 30 if remember else None
        response.set_cookie(
            key=self.cookie_name,
            value=token,
            httponly=True,
            max_age=max_age,
            expires=max_age,
            samesite="lax",
            secure=False
        )

    def logout_user(self, response: Response):
        response.delete_cookie(self.cookie_name)

auth_manager = AuthManager(
    cookie_name=settings.SESSION_COOKIE, 
    secret_key=settings.AUTH_SECRET_KEY
)
