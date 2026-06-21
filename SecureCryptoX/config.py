import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "CHANGE_THIS_IN_PRODUCTION")

    # Session Security
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Change to True after HTTPS is enabled
    SESSION_COOKIE_SAMESITE = 'Lax'

    # ===== User Database Connection =====
    DB_CONN_STR_USER = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=YOUR_RDS_ENDPOINT;"
        "DATABASE=SecureCryptoX;"
        "UID=YOUR_MASTER_USERNAME;"
        "PWD=YOUR_MASTER_PASSWORD;"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )

    # ===== Manager Database Connection =====
    DB_CONN_STR_MANAGER = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=YOUR_RDS_ENDPOINT;"
        "DATABASE=SecureCryptoX;"
        "UID=YOUR_MASTER_USERNAME;"
        "PWD=YOUR_MASTER_PASSWORD;"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )

    # ===== Admin Database Connection =====
    DB_CONN_STR_ADMIN = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=YOUR_RDS_ENDPOINT;"
        "DATABASE=SecureCryptoX;"
        "UID=YOUR_MASTER_USERNAME;"
        "PWD=YOUR_MASTER_PASSWORD;"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
    )

#try

