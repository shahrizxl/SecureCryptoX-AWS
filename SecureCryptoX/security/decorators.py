from flask import session, redirect
from functools import wraps


def login_required(f):

    @wraps(f)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return redirect("/")

        return f(*args, **kwargs)

    return wrapper



def role_required(role):

    def decorator(f):

        @wraps(f)
        def wrapper(*args, **kwargs):

            if session.get("role") != role:
                return "Access denied", 403

            return f(*args, **kwargs)

        return wrapper

    return decorator