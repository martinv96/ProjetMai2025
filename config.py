import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'ton_secret_key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///C:/Developpeur/ProjetMai2025/messages.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
