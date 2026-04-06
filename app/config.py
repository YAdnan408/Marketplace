# src/config.py


import os  # new

from dotenv import load_dotenv  # new
load_dotenv()  # new


class BaseConfig:
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # new
    SECRET_KEY = os.environ.get("SECRET_KEY", "default_secret_key")  # new


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_TEST_URL")


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

config_map = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

def get_config():
    env = os.environ.get("FLASK_ENV", "development")  # default: development
    return config_map.get(env, DevelopmentConfig)