import os
import dotenv


dotenv.load_dotenv()
wcl_key = os.environ['WCL_KEY']


class Config:
    DEBUG = False
    TESTING = False
    SEND_FILE_MAX_AGE_DEFAULT = 0
    SECRET_KEY = os.environ['SECRET_KEY']
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Prod(Config):
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']


class Dev(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'


class Test(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
