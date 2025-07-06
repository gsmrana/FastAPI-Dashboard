import os
import logging
from os import getenv, path
from dotenv import load_dotenv

APP_VERSION = "1.0.0"
DEFAULT_ENV = ".env"

ENV_PATH = os.getenv("MEDIAHUB_ENV_PATH", DEFAULT_ENV)
ENV_PATH = ENV_PATH if path.exists(ENV_PATH) else DEFAULT_ENV
if not load_dotenv(ENV_PATH):
    logging.warning(f'Failed to load dotenv from path: "{ENV_PATH}"')

class Settings:    
    ENV_PATH = ENV_PATH
    APP_VERSION = APP_VERSION        
    APP_NAME = getenv("APP_NAME", "Mediahub Dashboard")
    APP_PORT = getenv("APP_PORT", "3000")
    APP_DEBUG = getenv("APP_DEBUG", "False").lower() == "true"
    LOG_LEVEL = getenv("LOG_LEVEL", "INFO").upper()
    UPLOAD_DIR = getenv("UPLOAD_DIR", "uploaded_files")
    DATABASE_URL = getenv("DATABASE_URL", "sqlite:///./mediahub.db")        
    SESSION_COOKIE = getenv("SESSION_COOKIE", "user_session")
    AUTH_SECRET_KEY = getenv("AUTH_SECRET_KEY", "fallback-dev-secret")

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
