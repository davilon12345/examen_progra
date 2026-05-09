import os

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:Davilon_123@localhost:5432/Store2"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'superstore_secret_key'