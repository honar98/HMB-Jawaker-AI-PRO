import hashlib
import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer

from bot.auth.database import Database
from bot.auth.service import AuthService
from bot.auth.session import SessionManager
from bot.payment.paytabs import PayTabsClient, PayTabsError
from bot.api.subscription_api import SubscriptionAPI
from bot.subscription.plans import get_plans


PORT = int(os.getenv("PORT", "8080"))
PUBLIC_BASE_URL = os.getenv("HMB_PUBLIC_BASE_URL", "").rstrip("/")

db = Database()
db.initialize()

auth = AuthService(db)
subscriptions = SubscriptionAPI(db)
sessions = SessionManager()
paytabs = PayTabsClient()


class APIHandler(BaseHTTPRequestHandler):

    def send_json(self, status, body):
        data = json.dumps(
            body,
            separators=(",", ":"),
        ).encode()

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json",
        )
        self.send_header(
            "Content-Length",
            str(len(data)),
        )
        self.end_headers()

        self.wfile.write(data)

    def read_json(self):
        try:
            length = int(
                self.headers.get(
                    "Content-Length",
                    "0",
                )
            )

            raw = self.rfile.read(length)

            return json.loads(raw)

        except (ValueError, json.JSONDecodeError):
            return None

    def require_active_subscription(self):
        authorization = self.headers.get(
            "Authorization",
            "",
        )

        if not authorization.startswith("Bearer "):
            self.send_json(
                401,
                {
                    "ok": False,
                    "error": "Authentication required",
                },
            )
            return None

        token = authorization[7:].strip()
        user_id = sessions.get_user_id(token)

        if user_id is None:
            self.send_json(
                401,
                {
                    "ok": False,
                    "error": "Invalid or expired token",
                },
            )
            return None

        status = subscriptions.get_status(user_id)

        if not status.get("active"):
            self.send_json(
                403,
                {
                    "ok": False,
                    "error": "Active subscription required",
                },
            )
            return None

        return user_id

    def do_GET(self):

        if self.path == "/api/health":
            self.send_json(
                200,
                {
                    "status": "ok",
                    "service": "HMB FOREX AI API",
                },
            )
            return

        if self.path == "/api/plans":
            plans = get_plans()

            self.send_json(
                200,
                {
                    "ok": True,
                    "plans": plans,
                },
            )
            return

        if self.path == "/api/subscription":
            authorization = self.headers.get(
                "Authorization",
                "",
            )

            if not authorization.startswith("Bearer "):
                self.send_json(
                    401,
                    {
                        "ok": False,
                        "error": "Authentication required",
                    },
                )
                return

            token = authorization[7:].strip()
            user_id = sessions.get_user_id(token)

            if user_id is None:
                self.send_json(
                    401,
                    {
                        "ok": False,
                        "error": "Invalid or expired token",
                    },
                )
                return

            self.send_json(
                200,
                {
                    "ok": True,
                    "user_id": user_id,
                    "subscription": subscriptions.get_status(
                        user_id
                    ),
                },
            )
            return

        self.send_json(
            404,
            {"error": "Not found"},
        )

    def verify_paytabs_signature(self, raw_body):
        signature = self.headers.get(
            "Signature",
            "",
        ).strip()

        if not signature:
            return False

        expected = hmac.new(
            paytabs.server_key.encode("utf-8"),
            raw_body,
            hashlib.sha256,
        ).hexdigest()

        return hmac.compare_digest(
            expected,
            signature,
        )

    def payment_callback(self):
        length = int(
            self.headers.get(
                "Content-Length",
                "0",
            )
        )

        raw_body = self.rfile.read(length)

        if not self.verify_paytabs_signature(
            raw_body
        ):
            self.send_json(
                401,
                {
                    "ok": False,
                    "error": "Invalid PayTabs signature",
                },
            )
            return

        try:
            payload = json.loads(
                raw_body.decode("utf-8")
            )
        except (UnicodeDecodeError, json.JSONDecodeError):
            self.send_json(
                400,
                {
                    "ok": False,
                    "error": "Invalid JSON",
                },
            )
            return

        if payload.get("profile_id") != paytabs.profile_id:
            self.send_json(
                400,
                {
                    "ok": False,
                    "error": "Invalid profile",
                },
            )
            return

        if payload.get("cart_currency") != "IQD":
            self.send_json(
                400,
                {
                    "ok": False,
                    "error": "Invalid currency",
                },
            )
            return

        payment_result = payload.get(
            "payment_result",
            {},
        )

        if payment_result.get(
            "response_status"
        ) != "A":
            self.send_json(
                200,
                {
                    "ok": True,
                    "status": "payment_not_authorized",
                },
            )
            return

        tran_ref = payload.get("tran_ref")
        cart_id = str(
            payload.get("cart_id", "")
        )

        if not tran_ref or not cart_id:
            self.send_json(
                400,
                {
                    "ok": False,
                    "error": "Missing transaction data",
                },
            )
            return

        parts = cart_id.split(":", 2)

        if len(parts) != 3 or parts[0] != "HMB":
            self.send_json(
                400,
                {
                    "ok": False,
                    "error": "Invalid cart ID",
                },
            )
            return

        user_id = parts[1]
        plan = parts[2]

        plans = get_plans()

        if plan not in plans:
            self.send_json(
                400,
                {
                    "ok": False,
                    "error": "Invalid subscription plan",
                },
            )
            return

        try:
            amount = float(
                payload.get("cart_amount")
            )
        except (TypeError, ValueError):
            self.send_json(
                400,
                {
                    "ok": False,
                    "error": "Invalid amount",
                },
            )
            return

        expected_amount = float(
            plans[plan]["price"]
        )

        if amount != expected_amount:
            self.send_json(
                400,
                {
                    "ok": False,
                    "error": "Invalid payment amount",
                },
            )
            return

        activated = subscriptions.activate_payment(
            user_id=user_id,
            plan=plan,
            payment_reference=tran_ref,
        )

        self.send_json(
            200,
            {
                "ok": True,
                "activated": activated,
                "tran_ref": tran_ref,
                "plan": plan,
            },
        )

    def do_POST(self):

        if self.path == "/api/payment/callback":
            self.payment_callback()
            return

        if self.path == "/api/forex/signal":
            user_id = self.require_active_subscription()

            if user_id is None:
                return

            payload = self.read_json()

            if payload is None:
                self.send_json(
                    400,
                    {
                        "ok": False,
                        "error": "Invalid JSON",
                    },
                )
                return

            try:
                from bot.strategy.engine import generate_signal

                high = payload.get("high")
                low = payload.get("low")
                close = payload.get("close")

                if not isinstance(high, list) or not isinstance(low, list) or not isinstance(close, list):
                    raise ValueError(
                        "high, low and close must be arrays"
                    )

                if not (len(high) == len(low) == len(close)):
                    raise ValueError(
                        "high, low and close must have the same length"
                    )

                if len(close) < 50:
                    raise ValueError(
                        "at least 50 candles are required"
                    )

                signal = generate_signal(
                    high,
                    low,
                    close,
                )

                self.send_json(
                    200,
                    {
                        "ok": True,
                        "user_id": user_id,
                        "signal": signal,
                    },
                )

            except (ValueError, TypeError) as error:
                self.send_json(
                    400,
                    {
                        "ok": False,
                        "error": str(error),
                    },
                )

            except Exception as error:
                self.send_json(
                    500,
                    {
                        "ok": False,
                        "error": "Signal generation failed",
                        "details": str(error),
                    },
                )

            return

        payload = self.read_json()

        if payload is None:
            self.send_json(
                400,
                {
                    "ok": False,
                    "error": "Invalid JSON",
                },
            )
            return

        if self.path == "/api/register":

            try:
                user = auth.register(
                    payload.get("email", ""),
                    payload.get("password", ""),
                )

                self.send_json(
                    201,
                    {
                        "ok": True,
                        "user": user,
                    },
                )

            except ValueError as error:
                self.send_json(
                    400,
                    {
                        "ok": False,
                        "error": str(error),
                    },
                )

            return

        if self.path == "/api/login":

            user = auth.login(
                payload.get("email", ""),
                payload.get("password", ""),
            )

            if user is None:
                self.send_json(
                    401,
                    {
                        "ok": False,
                        "error": "Invalid email or password",
                    },
                )
                return

            token = sessions.create(
                user["user_id"]
            )

            self.send_json(
                200,
                {
                    "ok": True,
                    "user": user,
                    "token": token,
                    "token_type": "Bearer",
                },
            )

            return

        if self.path == "/api/payment/create":
            authorization = self.headers.get(
                "Authorization",
                "",
            )

            if not authorization.startswith("Bearer "):
                self.send_json(
                    401,
                    {
                        "ok": False,
                        "error": "Authentication required",
                    },
                )
                return

            token = authorization[7:].strip()
            user_id = sessions.get_user_id(token)

            if user_id is None:
                self.send_json(
                    401,
                    {
                        "ok": False,
                        "error": "Invalid or expired token",
                    },
                )
                return

            plan = str(payload.get("plan", "")).strip().lower()
            plans = get_plans()

            if plan not in plans:
                self.send_json(
                    400,
                    {
                        "ok": False,
                        "error": "Invalid subscription plan",
                    },
                )
                return

            user = auth.db.connection.execute(
                """
                SELECT email
                FROM users
                WHERE user_id = ?
                """,
                (user_id,),
            ).fetchone()

            if user is None:
                self.send_json(
                    401,
                    {
                        "ok": False,
                        "error": "User not found",
                    },
                )
                return

            try:
                cart_id = f"HMB:{user_id}:{plan}"

                result = paytabs.create_payment(
                    cart_id=cart_id,
                    amount=plans[plan]["price"],
                    plan=plan,
                    customer_email=user["email"],
                    return_url=f"{PUBLIC_BASE_URL}/payment/return",
                    callback_url=f"{PUBLIC_BASE_URL}/api/payment/callback",
                )

                self.send_json(
                    200,
                    {
                        "ok": True,
                        "plan": plan,
                        "currency": "IQD",
                        "amount": plans[plan]["price"],
                        "tran_ref": result.get("tran_ref"),
                        "redirect_url": result.get("redirect_url"),
                    },
                )

            except PayTabsError as error:
                self.send_json(
                    502,
                    {
                        "ok": False,
                        "error": "Payment provider error",
                        "details": str(error),
                    },
                )

            return

        self.send_json(
            404,
            {"error": "Not found"},
        )

    def log_message(self, format, *args):
        return


def run():
    server = HTTPServer(
        ("0.0.0.0", PORT),
        APIHandler,
    )

    print(
        f"HMB API listening on 0.0.0.0:{PORT}"
    )

    server.serve_forever()


if __name__ == "__main__":
    run()
