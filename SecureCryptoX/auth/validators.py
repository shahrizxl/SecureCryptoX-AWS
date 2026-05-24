import re


# =========================================
# SIGNUP VALIDATION
# =========================================
def validate_signup(username, email, password):

    errors = []

    # -----------------------------------------
    # REQUIRED FIELD CHECKS
    # -----------------------------------------
    if not username.strip():
        errors.append("Username is required")

    if not email.strip():
        errors.append("Email is required")

    if not password:
        errors.append("Password is required")

    # Stop further checks if empty
    if errors:
        return errors

    # -----------------------------------------
    # USERNAME RULE (basic improvement)
    # -----------------------------------------
    if len(username.strip()) < 3:
        errors.append("Username must be at least 3 characters")

    # -----------------------------------------
    # EMAIL FORMAT CHECK
    # -----------------------------------------
    email_pattern = r'^[^@]+@[^@]+\.[^@]+$'

    if not re.match(email_pattern, email):
        errors.append("Invalid email format")

    # -----------------------------------------
    # PASSWORD LENGTH CHECK
    # -----------------------------------------
    if len(password) < 8:
        errors.append("Password must be at least 8 characters")

    # -----------------------------------------
    # PASSWORD STRENGTH RULES
    # -----------------------------------------

    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least 1 uppercase letter")

    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least 1 lowercase letter")

    if not re.search(r"[0-9]", password):
        errors.append("Password must contain at least 1 number")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("Password must contain at least 1 special character")

    return errors


# =========================================
# LOGIN VALIDATION
# =========================================
def validate_login(username, password):

    errors = []

    if not username:
        errors.append("Username is required")

    if not password:
        errors.append("Password is required")

    return errors