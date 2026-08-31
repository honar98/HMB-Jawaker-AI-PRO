import json
import os
import threading
import time
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

from bot.paper_account import PaperAccount
from bot.mt5_bridge.metaapi import get_price as metaapi_get_price


SYMBOL = "EURUSD"
INTERVAL = 60
PORT = int(os.getenv("PORT", "8080"))

STARTING_BALANCE = 10000.0
PAPER_LOT = 0.01
SL_PIPS = 10
TP_PIPS = 20
PIP_SIZE = 0.0001

account = PaperAccount(STARTING_BALANCE)

last_price = None
last_update = None
last_signal = "WAIT"


def now_utc():
    return datetime.now(timezone.utc).strftime(
        "%Y-%m-%d %H:%M:%S UTC"
    )


class HealthHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path in ("/", "/healthz", "/status"):

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
                "paper_account": account.status(),
            }

            data = json.dumps(
                body,
                separators=(",", ":")
            ).encode()

            self.send_response(200)
            self.send_header(
                "Content-Type",
                "application/json"
            )
            self.send_header(
                "Content-Length",
                str(len(data))
            )
            self.end_headers()

            self.wfile.write(data)
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        return


def start_health_server():
    server = HTTPServer(
        ("0.0.0.0", PORT),
        HealthHandler
    )

    print(
        f"Health server listening on 0.0.0.0:{PORT}"
    )

    server.serve_forever()


def get_price():

    quote = metaapi_get_price(SYMBOL)

    # Use the mid price for the paper account.
    return (quote["bid"] + quote["ask"]) / 2


def open_paper_buy(price, timestamp):

    sl = price - (SL_PIPS * PIP_SIZE)
    tp = price + (TP_PIPS * PIP_SIZE)

    opened, reason = account.open_buy(
        price=price,
        size=PAPER_LOT,
        stop_loss=sl,
        take_profit=tp,
        timestamp=timestamp,
    )

    if opened:

        print("======================================")
        print(" PAPER BUY OPENED")
        print("======================================")
        print(f"ENTRY       : {price:.5f}")
        print(f"LOT         : {PAPER_LOT:.2f}")
        print(f"STOP LOSS   : {sl:.5f}")
        print(f"TAKE PROFIT : {tp:.5f}")
        print(f"BALANCE     : ${account.balance:.2f}")
        print("REAL ORDER  : NO")
        print("======================================")

    else:
        print(
            f"PAPER BUY BLOCKED: {reason}"
        )


print("======================================")
print(" HMB FOREX AI V302 LIVE PAPER")
print("======================================")
print("MODE        : PAPER ONLY")
print("REAL ORDERS : DISABLED")
print("SIDE        : BUY ONLY")
print(f"SYMBOL      : {SYMBOL}")
print(f"BALANCE     : ${STARTING_BALANCE:.2f}")
print(f"PAPER LOT   : {PAPER_LOT:.2f}")
print(f"SL          : {SL_PIPS} pips")
print(f"TP          : {TP_PIPS} pips")
print(f"HEALTH      : 0.0.0.0:{PORT}")
print("--------------------------------------")

threading.Thread(
    target=start_health_server,
    daemon=True,
).start()


while True:

    try:

        price = get_price()

        timestamp = now_utc()

        previous_price = last_price

        last_price = price
        last_update = timestamp

        # First check an already-open paper position.
        closed = account.update(
            price,
            timestamp
        )

        if closed:

            print("======================================")
            print(" PAPER POSITION CLOSED")
            print("======================================")
            print(
                f"REASON      : {closed['reason']}"
            )
            print(
                f"ENTRY       : {closed['entry']:.5f}"
            )
            print(
                f"EXIT        : {closed['exit']:.5f}"
            )
            print(
                f"P/L         : ${closed['pnl']:.2f}"
            )
            print(
                f"BALANCE     : ${closed['balance']:.2f}"
            )
            print("======================================")


        # Simple BUY-only paper signal.
        if previous_price is None:

            last_signal = "WAIT"

        elif price > previous_price:

            last_signal = "BUY"

            if account.position is None:
                open_paper_buy(
                    price,
                    timestamp
                )

        else:

            last_signal = "WAIT"


        print(
            f"[{timestamp}] "
            f"{SYMBOL} = {price:.5f}"
        )

        print(
            f"  PAPER SIGNAL: {last_signal}"
        )

        status = account.status()

        print(
            f"  BALANCE: ${status['balance']:.2f}"
        )

        if status["open_position"]:

            position = status["open_position"]

            print(
                f"  OPEN BUY: "
                f"{position['entry']:.5f}"
            )

            print(
                f"  SL: "
                f"{position['stop_loss']:.5f} | "
                f"TP: "
                f"{position['take_profit']:.5f}"
            )

        print("--------------------------------------")

    except Exception as error:

        print(
            f"[{now_utc()}] ERROR: {error}"
        )

    time.sleep(INTERVAL)
