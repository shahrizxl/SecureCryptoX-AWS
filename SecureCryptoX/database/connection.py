import pyodbc
from flask import g, session
from config import Config


def get_conn_str():

    role = session.get("role", "user")

    if role == "admin":
        return Config.DB_CONN_STR_ADMIN

    elif role == "manager":
        return Config.DB_CONN_STR_MANAGER

    return Config.DB_CONN_STR_USER


def get_db():

    # =========================================
    # CREATE CONNECTION
    # =========================================
    if 'db' not in g:

        g.db = pyodbc.connect(
            get_conn_str(),
            autocommit=False
        )

    # =========================================
    # ALWAYS SET SESSION CONTEXT
    # IMPORTANT FOR RLS
    # =========================================
    if "user_id" in session:

        cursor = g.db.cursor()

        cursor.execute(
            """
            EXEC sp_set_session_context
                @key = N'user_id',
                @value = ?
            """,
            (session["user_id"],)
        )

        g.db.commit()

    return g.db


def reset_db():

    db = g.pop('db', None)

    if db is not None:
        db.close()


def close_db(error=None):

    db = g.pop('db', None)

    if db is not None:
        db.close()