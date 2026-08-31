import hashlib
import hmac
import secrets


class UserStore:
    def __init__(self):
        self._users = {}

    @staticmethod
    def hash_password(password):
        if not isinstance(password, str) or len(password) < 8:
            raise ValueError(
                "Password must contain at least 8 characters"
            )

        salt = secrets.token_bytes(16)

        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            310_000,
        )

        return (
            salt.hex()
            + "$"
            + digest.hex()
        )

    @staticmethod
    def verify_password(password, stored_hash):
        try:
            salt_hex, digest_hex = stored_hash.split("$", 1)

            salt = bytes.fromhex(salt_hex)

            expected = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt,
                310_000,
            )

            return hmac.compare_digest(
                expected.hex(),
                digest_hex,
            )

        except (ValueError, TypeError):
            return False

    def create_user(self, user_id, email, password):
        email = email.strip().lower()

        if not email:
            raise ValueError("Email is required")

        if email in self._users:
            raise ValueError("User already exists")

        password_hash = self.hash_password(password)

        self._users[email] = {
            "user_id": user_id,
            "email": email,
            "password_hash": password_hash,
        }

        return self._users[email].copy()

    def authenticate(self, email, password):
        user = self._users.get(
            email.strip().lower()
        )

        if not user:
            return None

        if not self.verify_password(
            password,
            user["password_hash"],
        ):
            return None

        return user.copy()
