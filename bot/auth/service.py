import uuid

from .database import Database
from .store import UserStore


class AuthService:
    def __init__(self, database=None):
        self.db = database or Database()
        self.db.initialize()
        self.passwords = UserStore()

    def register(self, email, password):
        email = email.strip().lower()

        if not email:
            raise ValueError("Email is required")

        user_id = str(uuid.uuid4())
        password_hash = self.passwords.hash_password(password)

        try:
            self.db.connection.execute(
                """
                INSERT INTO users
                (user_id, email, password_hash, created_at)
                VALUES (?, ?, ?, datetime('now'))
                """,
                (user_id, email, password_hash),
            )
            self.db.connection.commit()

        except Exception as error:
            self.db.connection.rollback()

            if "UNIQUE constraint failed" in str(error):
                raise ValueError(
                    "Email already registered"
                ) from error

            raise

        return {
            "user_id": user_id,
            "email": email,
        }

    def login(self, email, password):
        row = self.db.connection.execute(
            """
            SELECT user_id, email, password_hash
            FROM users
            WHERE email = ?
            """,
            (email.strip().lower(),),
        ).fetchone()

        if row is None:
            return None

        if not self.passwords.verify_password(
            password,
            row["password_hash"],
        ):
            return None

        return {
            "user_id": row["user_id"],
            "email": row["email"],
        }
