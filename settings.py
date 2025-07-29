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
    # App Env variables
    ENV_PATH = ENV_PATH
    APP_VERSION = APP_VERSION        
    APP_NAME = getenv("APP_NAME", "Mediahub Dashboard")
    APP_PORT = getenv("APP_PORT", "3000")
    APP_DEBUG = getenv("APP_DEBUG", "False").lower() == "true"
    LOG_LEVEL = getenv("LOG_LEVEL", "INFO").upper()
    
    # Directory and Database
    UPLOAD_DIR = getenv("UPLOAD_DIR", "uploaded_files")
    DATABASE_URL = getenv("DATABASE_URL", "sqlite:///./mediahub.db")        
    
    # Secret keys
    SESSION_COOKIE = getenv("SESSION_COOKIE", "user_session")
    JWT_SECRET_KEY = getenv("JWT_SECRET_KEY", "jwt-dev-secret")
    AUTH_SECRET_KEY = getenv("AUTH_SECRET_KEY", "auth-dev-secret")
    
    # AzureAI Inferenece API
    AZUREAI_ENDPOINT_URL = getenv("AZUREAI_ENDPOINT_URL", "")
    AZUREAI_ENDPOINT_KEY = getenv("AZUREAI_ENDPOINT_KEY", "")
    AZUREAI_API_VERSION = getenv("AZUREAI_API_VERSION", "")
    AZUREAI_DEPLOYMENT = getenv("AZUREAI_DEPLOYMENT", "")
    AZUREAI_EMBEDDING_DEPLOYMENT = getenv("AZUREAI_EMBEDDING_DEPLOYMENT", "")

settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
