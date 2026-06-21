import pyodbc

_connection = None

def get_db():
    global _connection

    if _connection is None:
        _connection = pyodbc.connect(
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=securecryptox-db.curcyiccgz9c.us-east-1.rds.amazonaws.com;"
            "DATABASE=SecureCryptoX;"
            "UID=admin;"
            "PWD=Shah1234;"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;"
        )

    return _connection


def close_db(exception=None):
    global _connection

    if _connection:
        _connection.close()
        _connection = None


def reset_db():
    close_db()
