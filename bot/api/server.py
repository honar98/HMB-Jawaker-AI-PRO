import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from bot.auth.database import Database
from bot.auth.service import AuthService
from bot.api.subscription_api import SubscriptionAPI
from bot.subscription.plans import get_plans


PORT = 8081

db = Database()
db.initialize()

auth = AuthService(db)
subscriptions = SubscriptionAPI(db)


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

        self.send_json(
            404,
            {"error": "Not found"},
        )

    def do_POST(self):

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

            self.send_json(
                200,
                {
                    "ok": True,
                    "user": user,
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
