from database.connection import get_db


def log_action(user_id, action):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO AuditLog
        (
            user_id,
            action
        )
        VALUES (?, ?)
        """,
        (user_id, action)
    )

    conn.commit()