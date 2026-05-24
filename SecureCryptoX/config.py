import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "CHANGE_THIS_IN_PRODUCTION")
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_SAMESITE = 'Lax'

    DB_CONN_STR_USER = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"
    "DATABASE=SecureCryptoX;"
    "UID=crypto_user;PWD=User123!;"
    )
    DB_CONN_STR_MANAGER = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=SecureCryptoX;"
        "UID=crypto_manager;PWD=Manager123!;"
    )
    DB_CONN_STR_ADMIN = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=localhost;"
        "DATABASE=SecureCryptoX;"
        "UID=crypto_admin;PWD=Admin123!;"
    )