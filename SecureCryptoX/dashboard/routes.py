from flask import Blueprint
from flask import render_template
from flask import session
from flask import redirect
from flask import make_response

from security.decorators import login_required

from utils.crypto import get_btc_price

from wallet.services import get_wallet
from wallet.services import get_user_transactions
from wallet.services import calculate_portfolio


dashboard_bp = Blueprint(
    "dashboard",
    __name__
)


@dashboard_bp.route("/dashboard")
@login_required
def dashboard():

    # =========================================
    # EXTRA SESSION SAFETY (important)
    # =========================================
    if "user_id" not in session:
        return redirect("/")

    # =========================================
    # DATA LOADING
    # =========================================
    btc_price = get_btc_price()

    wallet = get_wallet(
        session["user_id"]
    )

    transactions = get_user_transactions(
        session["user_id"]
    )

    portfolio = calculate_portfolio(
        session["user_id"]
    )

    # =========================================
    # RESPONSE WITH CACHE DISABLED
    # =========================================
    response = make_response(render_template(
        "dashboard.html",
        username=session.get("username"),
        btc_price=btc_price,
        wallet=wallet,
        transactions=transactions,
        portfolio=portfolio
    ))

    response.headers["Cache-Control"] = (
        "no-store, no-cache, must-revalidate, max-age=0"
    )
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    return response


