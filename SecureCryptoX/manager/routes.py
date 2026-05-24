from datetime import datetime

from flask import Blueprint
from flask import render_template
from flask import redirect
from flask import request
from flask import session

from security.decorators import login_required
from security.decorators import role_required

from database.connection import get_db
from security.audit import log_action


manager_bp = Blueprint(
    "manager",
    __name__
)


# =========================================
# MANAGER DASHBOARD
# =========================================

@manager_bp.route("/manager")
@login_required
@role_required("manager")
def manager_dashboard():

    conn = get_db()
    cursor = conn.cursor()

    # =========================================
    # DAILY STATS (today vs yesterday)
    # =========================================

    cursor.execute(
        """
        SELECT
            SUM(CASE WHEN CAST(created_at AS DATE) = CAST(GETDATE() AS DATE)
                THEN amount_rm ELSE 0 END) AS today_volume,
            SUM(CASE WHEN CAST(created_at AS DATE) = CAST(DATEADD(DAY,-1,GETDATE()) AS DATE)
                THEN amount_rm ELSE 0 END) AS yesterday_volume,
            COUNT(CASE WHEN CAST(created_at AS DATE) = CAST(GETDATE() AS DATE)
                THEN 1 END) AS today_count,
            COUNT(CASE WHEN CAST(created_at AS DATE) = CAST(DATEADD(DAY,-1,GETDATE()) AS DATE)
                THEN 1 END) AS yesterday_count
        FROM Transactions
        """
    )

    daily = cursor.fetchone()

    today_volume     = daily.today_volume     or 0
    yesterday_volume = daily.yesterday_volume or 0
    today_count      = daily.today_count      or 0
    yesterday_count  = daily.yesterday_count  or 0

    if yesterday_volume and yesterday_volume > 0:
        volume_change = round(
            ((today_volume - yesterday_volume) / yesterday_volume) * 100, 1
        )
    else:
        volume_change = None

    # =========================================
    # TOTAL VOLUME + BTC (all time)
    # =========================================

    cursor.execute(
        "SELECT SUM(amount_rm) AS total_volume FROM Transactions"
    )
    volume = cursor.fetchone()

    cursor.execute(
        "SELECT SUM(amount_btc) AS total_btc FROM Transactions"
    )
    btc = cursor.fetchone()

    # =========================================
    # UNREVIEWED SUSPICIOUS COUNT
    # =========================================

    cursor.execute(
        """
        SELECT COUNT(*) AS unreviewed
        FROM SuspiciousActivities
        WHERE status = 'unreviewed'
        """
    )

    unreviewed_count = cursor.fetchone().unreviewed

    # =========================================
    # SUSPICIOUS ACTIVITIES
    # =========================================

    cursor.execute(
        """
        SELECT TOP 20
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
        ORDER BY s.created_at DESC
        """
    )

    suspicious = cursor.fetchall()

    return render_template(
        "manager.html",
        username=session.get("username"),
        volume=volume.total_volume or 0,
        btc=btc.total_btc or 0,
        suspicious=suspicious,
        today_volume=today_volume,
        yesterday_volume=yesterday_volume,
        volume_change=volume_change,
        today_count=today_count,
        yesterday_count=yesterday_count,
        unreviewed_count=unreviewed_count
    )


# =========================================
# REVIEW SUSPICIOUS ACTIVITY
# =========================================

@manager_bp.route("/review_activity/<int:activity_id>/<action>")
@login_required
@role_required("manager")
def review_activity(activity_id, action):

    if action not in ["reviewed", "escalated", "dismissed"]:
        return redirect("/manager")

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE SuspiciousActivities
        SET status = ?
        WHERE activity_id = ?
        """,
        (action, activity_id)
    )

    conn.commit()

    log_action(
        session["user_id"],
        f"Marked suspicious activity {activity_id} as {action}"
    )

    return redirect("/manager")