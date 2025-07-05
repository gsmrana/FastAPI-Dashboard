import os
import logging
from os import getenv, path
from dotenv import load_dotenv

APP_VERSION = "1.0.0"
DEFAULT_ENV = ".env"
env_loaded = False

class Config:    
    @classmethod
    def load_env(cls):
        env_path = os.getenv("MEDIAHUB_ENV_PATH", DEFAULT_ENV)
        env_path = env_path if path.exists(env_path) else DEFAULT_ENV        
        if not load_dotenv(env_path):
            logging.error(f'Error: Failed to load dotenv from path: "{env_path}"')        
        
        cls.ENV_PATH = env_path
        cls.APP_VERSION = APP_VERSION        
        cls.APP_NAME = getenv("APP_NAME", "Mediahub Dashboard")
        cls.APP_PORT = getenv("APP_PORT", "3000")
        cls.APP_DEBUG = getenv("APP_DEBUG", "False").lower() == "true"
        cls.LOG_LEVEL = getenv("LOG_LEVEL", "INFO").upper()
        cls.UPLOAD_DIR = getenv("UPLOAD_DIR", "uploaded_files")
        cls.DATABASE_URL = getenv("DATABASE_URL", "sqlite:///./mediahub.db")        
        cls.SESSION_COOKIE = getenv("SESSION_COOKIE", "user_session")
        cls.AUTH_SECRET_KEY = getenv("AUTH_SECRET_KEY", "supersecretkey")
        
if not env_loaded:
    Config.load_env()
    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
    env_loaded = True
  