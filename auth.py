from fastapi import Request, HTTPException, Response
from itsdangerous import URLSafeSerializer
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from models import User
from config import Config

serializer = URLSafeSerializer(Config.AUTH_SECRET_KEY)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)

def create_session_token(username: str):
    return serializer.dumps(username)

def get_username_from_session_token(token: str):
    try:
        return serializer.loads(token)
    except Exception:
        return None

def get_current_user(request: Request, db: Session):
    token = request.cookies.get(Config.SESSION_COOKIE)
    if not token:
        return None
    username = get_username_from_session_token(token)
    if not username:
        return None
    return db.query(User).filter(User.username == username).first()

def login_user(response: Response, username: str, remember: bool = False):
    token = create_session_token(username)
    max_age = 60 * 60 * 24 * 30 if remember else None
    response.set_cookie(
        key=Config.SESSION_COOKIE,
        value=token,
        httponly=True,
        max_age=max_age,
        expires=max_age,
        samesite="lax",
        secure=False
    )

def logout_user(response: Response):
    response.delete_cookie(Config.SESSION_COOKIE)
