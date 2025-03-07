import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY =  "mysecretkey"
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:root@localhost:5432/elearning")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY =  "myjwtsecret"
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_COOKIE_SECURE = False  
    JWT_ACCESS_COOKIE_NAME = "access_token"
    JWT_REFRESH_COOKIE_NAME = "refresh_token"
    JWT_COOKIE_CSRF_PROTECT = False 
