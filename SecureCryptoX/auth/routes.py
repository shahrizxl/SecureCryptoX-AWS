from flask import Blueprint, flash, jsonify
from flask import render_template
from flask import request
from flask import redirect
from flask import session
from flask import url_for

from security.decorators import login_required

from database.connection import get_db, reset_db
from security.audit import log_action

from auth.validators import validate_signup
from auth.validators import validate_login

from auth.services import create_user
from auth.services import user_exists
from auth.services import get_user_by_username
from auth.services import verify_password


from security.session import create_user_session
from limit import limiter

from datetime import datetime
from datetime import timedelta


auth_bp = Blueprint("auth", __name__)

# Tracked per username, not IP
failed_attempts = {}


# =========================================
# LOGIN PAGE
# =========================================

@auth_bp.route("/")
def login_page():

    if "user_id" in session:

        if session.get("role") == "admin":
            return redirect("/admin")

        elif session.get("role") == "manager":
            return redirect("/manager")

        else:
            return redirect("/dashboard")

    return render_template("login.html")


# =========================================
# SIGNUP PAGE
# =========================================

@auth_bp.route("/signup")
def signup_page():
    return render_template("signup.html")


# =========================================
# SUBMIT SIGNUP
# =========================================

@auth_bp.route("/submit_signup", methods=["POST"])
def submit_signup():

    username = request.form.get("username", "").strip()
    email    = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    errors = validate_signup(username, email, password)

    if errors:
        for error in errors:
            flash(error, "error")
        return redirect(url_for("auth.signup_page"))

    if user_exists(username, email):
        flash("Username or email already exists.", "error")
        return redirect(url_for("auth.signup_page"))

    create_user(username, email, password)

    flash("Account created successfully! Please log in.", "success")
    return redirect(url_for("auth.login_page"))


# =========================================
# HELPER — LOG SUSPICIOUS ACTIVITY
# =========================================

def log_suspicious(user_id, attempts):

    try:

        if attempts >= 5:
            risk = "high"
        elif attempts >= 3:
            risk = "medium"
        else:
            risk = "low"

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO SuspiciousActivities
                (user_id, activity_type, risk_level, status)
            VALUES (?, ?, ?, 'unreviewed')
            """,
            (
                user_id,
                f"Failed login attempt (attempt #{attempts})",
                risk
            )
        )

        conn.commit()

    except Exception:
        pass


# =========================================
# LOGIN
# =========================================

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    key      = username.lower()

    # =========================================
    # CHECK LOCKOUT (per username)
    # =========================================

    if key in failed_attempts:

        locked_until = failed_attempts[key]["locked_until"]

        if datetime.now() < locked_until:

            remaining = int(
                (locked_until - datetime.now()).total_seconds()
            )

            flash(str(remaining), "lockout")
            return redirect(url_for("auth.login_page"))

    # =========================================
    # VALIDATION
    # =========================================

    errors = validate_login(username, password)

    if errors:
        for error in errors:
            flash(error, "error")
        return redirect(url_for("auth.login_page"))

    # =========================================
    # GET USER
    # =========================================

    user = get_user_by_username(username)

    # =========================================
    # INVALID USERNAME OR PASSWORD
    # =========================================

    if not user or not verify_password(user.password_hash, password):

        if key not in failed_attempts:
            failed_attempts[key] = {
                "count": 0,
                "locked_until": datetime.now()
            }

        failed_attempts[key]["count"] += 1
        attempts = failed_attempts[key]["count"]

        # =========================================
        # LOG TO SUSPICIOUS ACTIVITIES
        # =========================================

        if user:
            log_suspicious(user.user_id, attempts)

        # =========================================
        # PROGRESSIVE LOCKOUT
        # =========================================

        if attempts >= 7:
            lock_minutes = 15
        elif attempts >= 5:
            lock_minutes = 10
        elif attempts >= 3:
            lock_minutes = 3
        else:
            lock_minutes = 0

        if lock_minutes > 0:
            failed_attempts[key]["locked_until"] = (
                datetime.now() + timedelta(minutes=lock_minutes)
            )
            flash(str(lock_minutes * 60), "lockout")

        else:
            attempts_left = 3 - attempts
            flash(
                f"Invalid username or password. "
                f"{attempts_left} attempt(s) left before lockout.",
                "error"
            )

        return redirect(url_for("auth.login_page"))

    # =========================================
    # ACCOUNT DISABLED
    # =========================================

    if not user.is_active:
        flash("Your account has been disabled. Contact support.", "error")
        return redirect(url_for("auth.login_page"))

    # =========================================
    # RESET THIS USER'S FAILED ATTEMPTS
    # =========================================

    if key in failed_attempts:
        del failed_attempts[key]

    # =========================================
    # CREATE SESSION + AUDIT
    # =========================================

    create_user_session(user)

    reset_db()  

    log_action(user.user_id, "User logged in")

    # =========================================
    # ROLE REDIRECT
    # =========================================

    if user.role == "admin":
        return redirect("/admin")

    elif user.role == "manager":
        return redirect("/manager")

    else:
        return redirect("/dashboard")


# =========================================
# VERIFY PASSWORD (balance reveal)
# =========================================

@auth_bp.route("/verify_password", methods=["POST"])
@login_required
def verify_password_route():

    data     = request.get_json()
    password = data.get("password", "")
    username = session.get("username")
    user     = get_user_by_username(username)

    if not user:
        return jsonify({"valid": False})

    if verify_password(user.password_hash, password):
        return jsonify({"valid": True})

    # =========================================
    # WRONG PASSWORD — LOG SUSPICIOUS ACTIVITY
    # =========================================

    try:

        conn   = get_db()
        cursor = conn.cursor()

        # Count how many times they've failed today
        cursor.execute(
            """
            SELECT COUNT(*) AS fail_count
            FROM SuspiciousActivities
            WHERE user_id = ?
            AND activity_type LIKE 'Wrong password%'
            AND CAST(created_at AS DATE) = CAST(GETDATE() AS DATE)
            """,
            (user.user_id,)
        )

        fail_count = cursor.fetchone().fail_count + 1

        if fail_count >= 5:
            risk = "high"
        elif fail_count >= 3:
            risk = "medium"
        else:
            risk = "low"

        cursor.execute(
            """
            INSERT INTO SuspiciousActivities
                (user_id, activity_type, risk_level, status)
            VALUES (?, ?, ?, 'unreviewed')
            """,
            (
                user.user_id,
                f"Wrong password on dashboard (attempt #{fail_count})",
                risk
            )
        )

        conn.commit()

    except Exception:
        pass

    return jsonify({"valid": False})


# =========================================
# LOGOUT
# =========================================

@auth_bp.route("/logout")
def logout():

    session.clear()

    response = redirect("/")

    response.set_cookie(
        "balanceUnlocked",
        "",
        expires=0
    )

    return response