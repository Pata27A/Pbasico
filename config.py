import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or '123456'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'postgresql+psycopg2://postgres:123456@localhost/pb_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
