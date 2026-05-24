from flask import Blueprint
from flask import request
from flask import redirect
from flask import session

from security.decorators import login_required

from wallet.services import deposit_money
from wallet.services import withdraw_money
from wallet.services import buy_btc
from wallet.services import sell_btc
from wallet.services import transfer_btc
from utils.crypto import get_btc_price


wallet_bp = Blueprint(
    "wallet",
    __name__
)


@wallet_bp.route("/deposit", methods=["POST"])
@login_required
def deposit():

    amount = float(
        request.form.get("amount")
    )

    deposit_money(
        session["user_id"],
        amount
    )

    return redirect("/dashboard")

from flask import jsonify

@wallet_bp.route("/lookup_receiver", methods=["POST"])
@login_required
def lookup_receiver():
    from database.connection import get_db
    data     = request.get_json()
    username = data.get("username", "").strip()

    if not username:
        return jsonify({"found": False, "message": "Enter a username."})

    # Can't send to yourself
    if username.lower() == session.get("username", "").lower():
        return jsonify({"found": False, "message": "You can't transfer to yourself."})

    conn   = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user_id, username FROM Users WHERE username = ? AND is_active = 1",
        (username,)
    )
    user = cursor.fetchone()

    if user:
        return jsonify({"found": True, "user_id": user.user_id, "username": user.username})

    return jsonify({"found": False, "message": "User not found in the system."})


@wallet_bp.route("/withdraw", methods=["POST"])
@login_required
def withdraw():

    amount = float(
        request.form.get("amount")
    )

    withdraw_money(
        session["user_id"],
        amount
    )

    return redirect("/dashboard")


@wallet_bp.route("/buy_btc", methods=["POST"])
@login_required
def buy():

    btc_price = float(
        request.form.get("btc_price")
    )

    amount_rm = request.form.get(
        "amount_rm"
    )

    btc_quantity = request.form.get(
        "btc_quantity"
    )

    if amount_rm:

        amount_rm = float(amount_rm)

    elif btc_quantity:

        btc_quantity = float(
            btc_quantity
        )

        amount_rm = (
            btc_quantity *
            btc_price
        )

    else:

        return redirect("/dashboard")

    buy_btc(
        session["user_id"],
        amount_rm,
        btc_price
    )

    return redirect("/dashboard")


@wallet_bp.route("/sell_btc", methods=["POST"])
@login_required
def sell():

    btc_price = float(
        request.form.get("btc_price")
    )

    btc_quantity = request.form.get(
        "btc_quantity"
    )

    amount_rm = request.form.get(
        "amount_rm"
    )

    if btc_quantity:

        btc_quantity = float(
            btc_quantity
        )

    elif amount_rm:

        amount_rm = float(
            amount_rm
        )

        btc_quantity = (
            amount_rm / btc_price
        )

    else:

        return redirect("/dashboard")

    sell_btc(
        session["user_id"],
        btc_quantity,
        btc_price
    )

    return redirect("/dashboard")


@wallet_bp.route("/transfer_btc", methods=["POST"])
@login_required
def transfer():

    btc_price         = float(request.form.get("btc_price"))
    receiver_username = request.form.get("receiver_username")
    btc_quantity      = request.form.get("btc_quantity")
    amount_rm         = request.form.get("amount_rm")

    if btc_quantity:
        btc_quantity = float(btc_quantity)
    elif amount_rm:
        btc_quantity = float(amount_rm) / btc_price
    else:
        return redirect("/dashboard")

    # Look up receiver_id from username
    from database.connection import get_db
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT user_id FROM Users WHERE username = ? AND is_active = 1",
        (receiver_username,)
    )
    receiver = cursor.fetchone()

    if not receiver:
        return redirect("/dashboard")

    transfer_btc(
        session["user_id"],
        receiver.user_id,
        btc_quantity
    )

    return redirect("/dashboard")