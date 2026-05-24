from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

from database.connection import get_db


def create_user(username, email, password):

    hashed_password = generate_password_hash(password)

    conn = get_db()
    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO Users
            (
                username,
                email,
                password_hash,
                role,
                is_active
            )
            VALUES (?, ?, ?, 'user', 1)
            """,
            (username, email, hashed_password)
        )

        cursor.execute(
            """
            SELECT user_id
            FROM Users
            WHERE username=?
            """,
            (username,)
        )

        user = cursor.fetchone()

        cursor.execute(
            """
            INSERT INTO Wallets
            (
                user_id,
                balance_rm,
                balance_btc
            )
            VALUES (?, 0, 0)
            """,
            (user.user_id,)
        )

        conn.commit()

    except Exception:

        conn.rollback()
        raise


def get_user_by_username(username):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT user_id,
               username,
               email,
               password_hash,
               role,
               is_active
        FROM Users
        WHERE username=?
        """,
        (username,)
    )

    return cursor.fetchone()


def verify_password(hashed_password, password):

    return check_password_hash(
        hashed_password,
        password
    )


def user_exists(username, email):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT 1
        FROM Users
        WHERE username=? OR email=?
        """,
        (username, email)
    )

    return cursor.fetchone() is not None

def get_user_transactions(user_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT TOP 20
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