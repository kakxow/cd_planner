import os
import dotenv


dotenv.load_dotenv()


class Config:
    DEBUG = False
    TESTING = False
    SEND_FILE_MAX_AGE_DEFAULT = 0
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class Prod(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


class Dev(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'


class Test(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
