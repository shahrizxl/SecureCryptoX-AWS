from database.connection import get_db
from utils.crypto import get_btc_price

from security.audit import log_action


def deposit_money(user_id, amount):

    if amount <= 0:
        return False

    conn = get_db()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            UPDATE Wallets
            SET balance_rm = balance_rm + ?
            WHERE user_id=?
            """,
            (amount, user_id)
        )

        cursor.execute(
            """
            INSERT INTO Transactions
            (
                user_id,
                transaction_type,
                amount_rm
            )
            VALUES (?, 'deposit', ?)
            """,
            (user_id, amount)
        )

        log_action(
            user_id,
            f"Deposited RM {amount}"
        )

        conn.commit()

        return True

    except Exception:

        conn.rollback()
        return False


def withdraw_money(user_id, amount):

    if amount <= 0:
        return False

    conn = get_db()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT balance_rm
            FROM Wallets
            WHERE user_id=?
            """,
            (user_id,)
        )

        wallet = cursor.fetchone()

        if not wallet:
            return False

        if wallet.balance_rm < amount:
            return False

        cursor.execute(
            """
            UPDATE Wallets
            SET balance_rm = balance_rm - ?
            WHERE user_id=?
            """,
            (amount, user_id)
        )

        cursor.execute(
            """
            INSERT INTO Transactions
            (
                user_id,
                transaction_type,
                amount_rm
            )
            VALUES (?, 'withdraw', ?)
            """,
            (user_id, amount)
        )

        if amount >= 5000:

            cursor.execute(
                """
                INSERT INTO SuspiciousActivities
                (
                    user_id,
                    activity_type,
                    risk_level
                )
                VALUES
                (
                    ?,
                    'Large Withdrawal',
                    'High'
                )
                """,
                (user_id,)
            )

        log_action(
            user_id,
            f"Withdrew RM {amount}"
        )

        conn.commit()

        return True

    except Exception:

        conn.rollback()
        return False


def buy_btc(user_id, amount_rm, btc_price):

    if amount_rm <= 0:
        return False


    btc_amount = amount_rm / btc_price

    conn = get_db()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT balance_rm
            FROM Wallets
            WHERE user_id=?
            """,
            (user_id,)
        )

        wallet = cursor.fetchone()

        if not wallet:
            return False

        if wallet.balance_rm < amount_rm:
            return False

        cursor.execute(
            """
            UPDATE Wallets
            SET balance_rm = balance_rm - ?,
                balance_btc = balance_btc + ?
            WHERE user_id=?
            """,
            (amount_rm, btc_amount, user_id)
        )

        cursor.execute(
            """
            INSERT INTO Transactions
            (
                user_id,
                transaction_type,
                amount_rm,
                amount_btc
            )
            VALUES (?, 'buy', ?, ?)
            """,
            (user_id, amount_rm, btc_amount)
        )

        log_action(
            user_id,
            f"Bought BTC worth RM {amount_rm}"
        )

        conn.commit()

        return True

    except Exception as e:

        print("ERROR:", e)

        conn.rollback()
        return False


def sell_btc(user_id, btc_amount, btc_price):

    if btc_amount <= 0:
        return False

    rm_amount = btc_amount * btc_price

    conn = get_db()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT balance_btc
            FROM Wallets
            WHERE user_id=?
            """,
            (user_id,)
        )

        wallet = cursor.fetchone()

        if not wallet:
            return False

        if wallet.balance_btc < btc_amount:
            return False

        cursor.execute(
            """
            UPDATE Wallets
            SET balance_btc = balance_btc - ?,
                balance_rm = balance_rm + ?
            WHERE user_id=?
            """,
            (btc_amount, rm_amount, user_id)
        )

        cursor.execute(
            """
            INSERT INTO Transactions
            (
                user_id,
                transaction_type,
                amount_rm,
                amount_btc
            )
            VALUES (?, 'sell', ?, ?)
            """,
            (user_id, rm_amount, btc_amount)
        )

        log_action(
            user_id,
            f"Sold {btc_amount} BTC"
        )

        conn.commit()

        return True

    except Exception:

        conn.rollback()
        return False


def transfer_btc(sender_id, receiver_id, btc_amount):

    if btc_amount <= 0:
        return False

    if sender_id == receiver_id:
        return False

    conn = get_db()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            SELECT balance_btc
            FROM Wallets
            WHERE user_id=?
            """,
            (sender_id,)
        )

        sender_wallet = cursor.fetchone()

        if not sender_wallet:
            return False

        if sender_wallet.balance_btc < btc_amount:
            return False

        cursor.execute(
            """
            SELECT user_id
            FROM Users
            WHERE user_id=?
            """,
            (receiver_id,)
        )

        receiver = cursor.fetchone()

        if not receiver:
            return False

        cursor.execute(
            """
            UPDATE Wallets
            SET balance_btc = balance_btc - ?
            WHERE user_id=?
            """,
            (btc_amount, sender_id)
        )

        cursor.execute(
            """
            UPDATE Wallets
            SET balance_btc = balance_btc + ?
            WHERE user_id=?
            """,
            (btc_amount, receiver_id)
        )

        cursor.execute(
            """
            INSERT INTO Transactions
            (
                user_id,
                receiver_id,
                transaction_type,
                amount_btc
            )
            VALUES (?, ?, 'transfer', ?)
            """,
            (sender_id, receiver_id, btc_amount)
        )

        if btc_amount >= 1:

            cursor.execute(
                """
                INSERT INTO SuspiciousActivities
                (
                    user_id,
                    activity_type,
                    risk_level
                )
                VALUES
                (
                    ?,
                    'Large BTC Transfer',
                    'Medium'
                )
                """,
                (sender_id,)
            )

        log_action(
            sender_id,
            f"Transferred {btc_amount} BTC to user {receiver_id}"
        )

        conn.commit()

        return True

    except Exception:

        conn.rollback()
        return False


def get_wallet(user_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT balance_rm,
               balance_btc
        FROM Wallets
        WHERE user_id=?
        """,
        (user_id,)
    )

    return cursor.fetchone()

def get_user_transactions(user_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT TOP 30
               transaction_type,
               amount_rm,
               amount_btc,
               receiver_id,
               created_at
        FROM Transactions
        WHERE user_id=?
        ORDER BY created_at DESC
        """,
        (user_id,)
    )

    return cursor.fetchall()

def calculate_portfolio(user_id):

    wallet = get_wallet(user_id)
    
    # 1. ADD THIS GUARD CLAUSE
    if not wallet:
        return {
            "btc_value": 0,
            "total_portfolio": 0,
            "profit": 0
        }

    btc_price = get_btc_price()
    btc_value = wallet.balance_btc * btc_price

    total_portfolio = (
        wallet.balance_rm +
        btc_value
    )

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT ISNULL(SUM(amount_rm), 0)
        AS invested
        FROM Transactions
        WHERE user_id=?
        AND transaction_type='buy'
        """,
        (user_id,)
    )

    # Note: Because you used an aggregate function (SUM) with ISNULL, 
    # fetchone() will safely return a row with '0' even if there are no transactions.
    invested = cursor.fetchone().invested

    profit = btc_value - invested

    return {
        "btc_value": btc_value,
        "total_portfolio": total_portfolio,
        "profit": profit
    }