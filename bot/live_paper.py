import json
import threading
import time
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

SYMBOL = "EURUSD"
INTERVAL = 3600
PORT = 8080

last_price = None
last_update = None
last_signal = "WAIT"


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/healthz"):
            body = {
                "status": "ok",
                "service": "HMB FOREX AI V302",
                "mode": "PAPER ONLY",
                "real_orders": False,
                "side": "BUY ONLY",
                "symbol": SYMBOL,
                "last_price": last_price,
                "last_signal": last_signal,
                "last_update": last_update,
            }

            data = json.dumps(body).encode()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        return


def start_health_server():
    server = HTTPServer(("0.0.0.0", PORT), HealthHandler)
    print(f"Health server listening on 0.0.0.0:{PORT}")
    server.serve_forever()


def get_price():
    url = (
        "https://query1.finance.yahoo.com/v8/finance/chart/"
        "EURUSD=X?interval=1h&range=1d"
    )

    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
    )

    with urllib.request.urlopen(req, timeout=15) as response:
        data = json.loads(response.read())

    result = data["chart"]["result"][0]
    price = result["meta"]["regularMarketPrice"]

    return float(price)


print("======================================")
print(" HMB FOREX AI V302 LIVE PAPER")
print("======================================")
print("MODE        : PAPER ONLY")
print("REAL ORDERS : DISABLED")
print("SIDE        : BUY ONLY")
print(f"HEALTH      : 0.0.0.0:{PORT}")
print("--------------------------------------")

threading.Thread(
    target=start_health_server,
    daemon=True,
).start()

last_price = None

while True:
    try:
        price = get_price()

        now = datetime.now(timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S UTC"
        )

        previous_price = last_price
        last_price = price
        last_update = now

        if previous_price is not None:
            if price > previous_price:
                last_signal = "BUY"
            else:
                last_signal = "WAIT"

        print(f"[{now}] {SYMBOL} = {price:.5f}")
        print(f"  PAPER SIGNAL: {last_signal}")

    except Exception as e:
        print("ERROR:", e)

    time.sleep(INTERVAL)
