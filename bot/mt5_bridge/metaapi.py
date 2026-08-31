import json
import os
import urllib.error
import urllib.parse
import urllib.request


METAAPI_TOKEN = os.getenv("METAAPI_TOKEN", "").strip()
METAAPI_ACCOUNT_ID = os.getenv(
    "METAAPI_ACCOUNT_ID",
    "bcdad976-5c83-4cf9-bff6-dda16f505373",
).strip()

METAAPI_REGION = os.getenv(
    "METAAPI_REGION",
    "new-york",
).strip()

BASE_URL = (
    f"https://mt-client-api-v1.{METAAPI_REGION}."
    "agiliumtrade.ai"
)


class MetaApiError(RuntimeError):
    pass


def _request(path):
    if not METAAPI_TOKEN:
        raise MetaApiError(
            "METAAPI_TOKEN is not configured"
        )

    url = BASE_URL + path

    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "auth-token": METAAPI_TOKEN,
            "User-Agent": "HMB-FOREX-AI/1.0",
        },
        method="GET",
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=20,
        ) as response:
            return json.loads(response.read())

    except urllib.error.HTTPError as error:
        body = error.read().decode(
            "utf-8",
            errors="replace",
        )

        raise MetaApiError(
            f"MetaApi HTTP {error.code}: {body[:500]}"
        ) from error

    except urllib.error.URLError as error:
        raise MetaApiError(
            f"MetaApi connection error: {error.reason}"
        ) from error


def get_price(symbol="EURUSD"):
    encoded_symbol = urllib.parse.quote(
        symbol,
        safe="",
    )

    data = _request(
        f"/users/current/accounts/"
        f"{METAAPI_ACCOUNT_ID}/symbols/"
        f"{encoded_symbol}/current-price"
        "?keepSubscription=true"
    )

    return {
        "symbol": data["symbol"],
        "bid": float(data["bid"]),
        "ask": float(data["ask"]),
        "time": data.get("time"),
        "brokerTime": data.get("brokerTime"),
    }


def get_account_information():
    return _request(
        f"/users/current/accounts/"
        f"{METAAPI_ACCOUNT_ID}/account-information"
    )
