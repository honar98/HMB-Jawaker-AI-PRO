import time
from datetime import datetime, timezone

import urllib.request
import json

SYMBOL = "EURUSD"
INTERVAL = 3600

print("=== HMB FOREX AI V302 LIVE PAPER ===")
print("MODE: PAPER ONLY")
print("REAL ORDERS: DISABLED")
print("SIDE: BUY ONLY")

def get_price():
    url = "https://query1.finance.yahoo.com/v8/finance/chart/EURUSD=X?interval=1h&range=1d"
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
    )

    with urllib.request.urlopen(req, timeout=15) as response:
        data = json.loads(response.read())

    result = data["chart"]["result"][0]
    price = result["meta"]["regularMarketPrice"]

    return float(price)

last_price = None

while True:
    try:
        price = get_price()
        now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        print(f"[{now}] {SYMBOL} = {price:.5f}")

        if last_price is not None:
            if price > last_price:
                print("  PAPER SIGNAL: BUY")
            else:
                print("  PAPER SIGNAL: WAIT")

        last_price = price

    except Exception as e:
        print("ERROR:", e)

    time.sleep(INTERVAL)
