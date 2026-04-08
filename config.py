from urllib.parse import quote_plus


password = quote_plus("mypassword")


class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://myuser:mypassword@localhost:5432/mydatabase"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "Yamin12345678"