import csv
import io
from datetime import datetime

from flask import Blueprint
from flask import render_template
from flask import redirect
from flask import request
from flask import session
from flask import Response

from security.decorators import login_required
from security.decorators import role_required

from database.connection import get_db
from security.audit import log_action


admin_bp = Blueprint(
    "admin",
    __name__
)


# =========================================
# ADMIN DASHBOARD
# =========================================

@admin_bp.route("/admin")
@login_required
@role_required("admin")
def admin_panel():

    conn = get_db()
    cursor = conn.cursor()

    selected_user = request.args.get("user_id")

    # =========================================
    # DATE RANGE FILTER
    # =========================================

    date_range = request.args.get("date_range", "all")

    if date_range == "today":
        date_sql     = "WHERE CAST(t.created_at AS DATE) = CAST(GETDATE() AS DATE)"
        date_sql_and = "AND CAST(t.created_at AS DATE) = CAST(GETDATE() AS DATE)"

    elif date_range == "week":
        date_sql     = "WHERE t.created_at >= DATEADD(DAY, -7, GETDATE())"
        date_sql_and = "AND t.created_at >= DATEADD(DAY, -7, GETDATE())"

    elif date_range == "month":
        date_sql     = "WHERE t.created_at >= DATEADD(DAY, -30, GETDATE())"
        date_sql_and = "AND t.created_at >= DATEADD(DAY, -30, GETDATE())"

    else:
        date_sql     = ""
        date_sql_and = ""

    # =========================================
    # USERS
    # =========================================

    cursor.execute(
        """
        SELECT *
        FROM Users
        ORDER BY user_id
        """
    )

    users = cursor.fetchall()

    # =========================================
    # TRANSACTIONS (filterable by user + date)
    # =========================================

    if selected_user:

        cursor.execute(
            f"""
            SELECT TOP 20
                t.transaction_id,
                t.user_id,
                u.username,
                t.transaction_type,
                t.amount_rm,
                t.amount_btc,
                t.created_at
            FROM Transactions t
            INNER JOIN Users u
                ON t.user_id = u.user_id
            WHERE t.user_id = ?
            {date_sql_and}
            ORDER BY t.created_at DESC
            """,
            (selected_user,)
        )

    else:

        cursor.execute(
            f"""
            SELECT TOP 20
                t.transaction_id,
                t.user_id,
                u.username,
                t.transaction_type,
                t.amount_rm,
                t.amount_btc,
                t.created_at
            FROM Transactions t
            INNER JOIN Users u
                ON t.user_id = u.user_id
            {date_sql_and.replace("AND", "WHERE", 1) if date_sql_and else ""}
            ORDER BY t.created_at DESC
            """
        )

    transactions = cursor.fetchall()

    # =========================================
    # AUDIT LOGS (filterable by user)
    # =========================================

    if selected_user:

        cursor.execute(
            """
            SELECT TOP 20
                a.audit_id,
                a.user_id,
                u.username,
                a.action,
                a.created_at
            FROM AuditLog a
            INNER JOIN Users u
                ON a.user_id = u.user_id
            WHERE a.user_id = ?
            ORDER BY a.created_at DESC
            """,
            (selected_user,)
        )

    else:

        cursor.execute(
            """
            SELECT TOP 20
                a.audit_id,
                a.user_id,
                u.username,
                a.action,
                a.created_at
            FROM AuditLog a
            INNER JOIN Users u
                ON a.user_id = u.user_id
            ORDER BY a.created_at DESC
            """
        )

    logs = cursor.fetchall()

    # =========================================
    # SUSPICIOUS ACTIVITIES
    # Escalated pinned to top, then rest
    # =========================================

    cursor.execute(
        """
        SELECT TOP 30
            s.activity_id,
            s.user_id,
            u.username,
            s.activity_type,
            s.risk_level,
            s.status,
            s.created_at
        FROM SuspiciousActivities s
        INNER JOIN Users u
            ON s.user_id = u.user_id
        ORDER BY
            CASE WHEN s.status = 'escalated' THEN 0 ELSE 1 END,
            s.created_at DESC
        """
    )

    suspicious = cursor.fetchall()

    # =========================================
    # STAT COUNTS
    # =========================================

    cursor.execute(
        "SELECT COUNT(*) AS total_users FROM Users"
    )
    total_users = cursor.fetchone().total_users

    cursor.execute(
        "SELECT COUNT(*) AS total_transactions FROM Transactions"
    )
    total_transactions = cursor.fetchone().total_transactions

    cursor.execute(
        """
        SELECT COUNT(*) AS escalated_count
        FROM SuspiciousActivities
        WHERE status = 'escalated'
        """
    )
    escalated_count = cursor.fetchone().escalated_count

    cursor.execute(
        "SELECT COUNT(*) AS suspicious_count FROM SuspiciousActivities"
    )
    suspicious_count = cursor.fetchone().suspicious_count

    return render_template(
        "admin.html",
        users=users,
        transactions=transactions,
        logs=logs,
        suspicious=suspicious,
        suspicious_count=suspicious_count,
        escalated_count=escalated_count,
        total_users=total_users,
        total_transactions=total_transactions,
        selected_user=selected_user,
        date_range=date_range
    )


# =========================================
# DISABLE USER
# =========================================

@admin_bp.route("/disable_user/<int:user_id>")
@login_required
@role_required("admin")
def disable_user(user_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE Users SET is_active=0 WHERE user_id=?",
        (user_id,)
    )
    conn.commit()

    log_action(
        session["user_id"],
        f"Disabled user account {user_id}"
    )

    return redirect("/admin")


# =========================================
# ENABLE USER
# =========================================

@admin_bp.route("/enable_user/<int:user_id>")
@login_required
@role_required("admin")
def enable_user(user_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE Users SET is_active=1 WHERE user_id=?",
        (user_id,)
    )
    conn.commit()

    log_action(
        session["user_id"],
        f"Enabled user account {user_id}"
    )

    return redirect("/admin")


# =========================================
# UPDATE ROLE
# =========================================

@admin_bp.route("/update_role", methods=["POST"])
@login_required
@role_required("admin")
def update_role():

    user_id = request.form.get("user_id")
    role    = request.form.get("role")

    if role not in ["user", "manager"]:
        return redirect("/admin")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE Users SET role=? WHERE user_id=?",
        (role, user_id)
    )
    conn.commit()

    log_action(
        session["user_id"],
        f"Updated user {user_id} role to {role}"
    )

    return redirect("/admin")


# =========================================
# RESOLVE ESCALATED ACTIVITY
# Admin-only — only works on escalated items
# =========================================

@admin_bp.route("/resolve_activity/<int:activity_id>")
@login_required
@role_required("admin")
def resolve_activity(activity_id):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE SuspiciousActivities
        SET status = 'resolved'
        WHERE activity_id = ?
        AND status = 'escalated'
        """,
        (activity_id,)
    )
    conn.commit()

    log_action(
        session["user_id"],
        f"Resolved escalated activity {activity_id}"
    )

    return redirect("/admin")


# =========================================
# EXPORT TRANSACTIONS AS CSV
# =========================================

@admin_bp.route("/export_transactions")
@login_required
@role_required("admin")
def export_transactions():

    conn = get_db()
    cursor = conn.cursor()

    date_range    = request.args.get("date_range", "all")
    selected_user = request.args.get("user_id")

    if date_range == "today":
        date_sql = "WHERE CAST(t.created_at AS DATE) = CAST(GETDATE() AS DATE)"
        date_sql_and = "AND CAST(t.created_at AS DATE) = CAST(GETDATE() AS DATE)"
    elif date_range == "week":
        date_sql = "WHERE t.created_at >= DATEADD(DAY, -7, GETDATE())"
        date_sql_and = "AND t.created_at >= DATEADD(DAY, -7, GETDATE())"
    elif date_range == "month":
        date_sql = "WHERE t.created_at >= DATEADD(DAY, -30, GETDATE())"
        date_sql_and = "AND t.created_at >= DATEADD(DAY, -30, GETDATE())"
    else:
        date_sql     = ""
        date_sql_and = ""

    if selected_user:

        cursor.execute(
            f"""
            SELECT
                t.transaction_id,
                t.user_id,
                u.username,
                t.transaction_type,
                t.amount_rm,
                t.amount_btc,
                t.created_at
            FROM Transactions t
            INNER JOIN Users u
                ON t.user_id = u.user_id
            WHERE t.user_id = ?
            {date_sql_and}
            ORDER BY t.created_at DESC
            """,
            (selected_user,)
        )

    else:

        cursor.execute(
            f"""
            SELECT
                t.transaction_id,
                t.user_id,
                u.username,
                t.transaction_type,
                t.amount_rm,
                t.amount_btc,
                t.created_at
            FROM Transactions t
            INNER JOIN Users u
                ON t.user_id = u.user_id
            {date_sql_and.replace("AND", "WHERE", 1) if date_sql_and else ""}
            ORDER BY t.created_at DESC
            """
        )

    rows = cursor.fetchall()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Transaction ID",
        "User ID",
        "Username",
        "Type",
        "Amount (RM)",
        "Amount (BTC)",
        "Date"
    ])

    for row in rows:
        writer.writerow([
            row.transaction_id,
            row.user_id,
            row.username,
            row.transaction_type,
            row.amount_rm,
            row.amount_btc,
            row.created_at
        ])

    output.seek(0)

    log_action(
        session["user_id"],
        f"Exported transactions CSV (range: {date_range})"
    )

    filename = f"transactions_{date_range}_{datetime.now().strftime('%Y%m%d')}.csv"

    return Response(
        output,
        mimetype="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )