CREATE_USER_QUERY = """
INSERT INTO Users
(
    username,
    email,
    password_hash,
    role,
    is_active
)
VALUES (?, ?, ?, 'user', 1)
"""

GET_USER_BY_USERNAME_QUERY = """
SELECT user_id,
       username,
       email,
       password_hash,
       role,
       is_active
FROM Users
WHERE username=?
"""

CHECK_USER_EXISTS_QUERY = """
SELECT 1
FROM Users
WHERE username=? OR email=?
"""

INSERT_AUDIT_LOG_QUERY = """
INSERT INTO AuditLog
(
    user_id,
    action
)
VALUES (?, ?)
"""

GET_ALL_USERS_QUERY = """
SELECT *
FROM Users
"""

DELETE_USER_QUERY = """
DELETE FROM Users
WHERE user_id=?
"""