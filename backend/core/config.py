# backend/core/config.py

import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """
    Pydantic model to hold all application settings, loaded from environment variables.
    """
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD")
    DB_NAME: str = os.getenv("DB_NAME")
    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    
    # --- NEW ---
    # Load the secret key for signing JWTs
    SECRET_KEY: str = os.getenv("SECRET_KEY")

# Create a single instance of the settings to be used throughout the app
settings = Settings()