import json

from bot.auth.database import Database
from bot.auth.service import AuthService


class AuthAPI:
    def __init__(self):
        self.db = Database()
        self.auth = AuthService(self.db)

    def register(self, payload):
        email = payload.get("email", "")
        password = payload.get("password", "")

        user = self.auth.register(
            email,
            password,
        )

        return {
            "ok": True,
            "user": user,
        }

    def login(self, payload):
        email = payload.get("email", "")
        password = payload.get("password", "")

        user = self.auth.login(
            email,
            password,
        )

        if user is None:
            return {
                "ok": False,
                "error": "Invalid email or password",
            }

        return {
            "ok": True,
            "user": user,
        }
