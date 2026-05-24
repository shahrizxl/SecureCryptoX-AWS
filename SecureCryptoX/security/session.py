from flask import session
from database.connection import get_db


def create_user_session(user):

    session.permanent = True

    session["user_id"] = user.user_id
    session["username"] = user.username
    session["role"] = user.role

    # =========================================
    # SQL SERVER SESSION CONTEXT
    # =========================================

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        EXEC sp_set_session_context
            @key=N'user_id',
            @value=?
    """, user.user_id)

    conn.commit()


def clear_user_session():
    session.clear()


def is_logged_in():
    return "user_id" in session


def current_user_role():
    return session.get("role")


def current_username():
    return session.get("username")