from flask import Flask
from flask import request
from flask import session

from flask_wtf.csrf import CSRFProtect

from limit import limiter

from datetime import timedelta

from config import Config

from security.headers import apply_security_headers

from database.connection import close_db

from auth.routes import auth_bp
from dashboard.routes import dashboard_bp
from admin.routes import admin_bp
from manager.routes import manager_bp
from wallet.routes import wallet_bp


# =========================================
# CREATE FLASK APPLICATION
# =========================================

app = Flask(__name__)

limiter.init_app(app)

app.config.from_object(Config)


# =========================================
# CSRF PROTECTION
# =========================================

csrf = CSRFProtect(app)
app.config["WTF_CSRF_ENABLED"] = True


# =========================================
# RATE LIMIT KEY
# =========================================

def rate_limit_key():

    if "user_id" in session:

        return str(
            session["user_id"]
        )

    return request.remote_addr

# =========================================
# SESSION CONFIGURATION
# =========================================

app.permanent_session_lifetime = timedelta(
    minutes=30
)


# =========================================
# REGISTER BLUEPRINTS
# =========================================

app.register_blueprint(auth_bp)

app.register_blueprint(dashboard_bp)

app.register_blueprint(admin_bp)

app.register_blueprint(manager_bp)

app.register_blueprint(wallet_bp)


# =========================================
# SECURITY HEADERS
# =========================================

apply_security_headers(app)


# =========================================
# CLOSE DATABASE CONNECTION
# =========================================

app.teardown_appcontext(close_db)


# =========================================
# ERROR HANDLERS
# =========================================

@app.errorhandler(403)
def forbidden(error):

    return "403 Access Denied", 403


@app.errorhandler(404)
def page_not_found(error):

    return "404 Page Not Found", 404


@app.errorhandler(429)
def ratelimit_handler(error):

    return """
    <h1>
        Too Many Requests
    </h1>

    <p>
        Please wait before trying again.
    </p>
    """, 429


@app.errorhandler(500)
def internal_server_error(error):

    return "500 Internal Server Error", 500


# =========================================
# RUN APPLICATION
# =========================================
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
