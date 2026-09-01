import json
import os
import urllib.error
import urllib.request


class PayTabsError(Exception):
    pass


class PayTabsClient:
    def __init__(self):
        self.profile_id = os.getenv("PAYTABS_PROFILE_ID")
        self.server_key = os.getenv("PAYTABS_SERVER_KEY")

        self.base_url = os.getenv(
            "PAYTABS_BASE_URL",
            "https://secure-iraq.paytabs.com",
        ).rstrip("/")

        if not self.profile_id:
            raise PayTabsError(
                "PAYTABS_PROFILE_ID is not configured"
            )

        if not self.server_key:
            raise PayTabsError(
                "PAYTABS_SERVER_KEY is not configured"
            )

        try:
            self.profile_id = int(self.profile_id)
        except ValueError as error:
            raise PayTabsError(
                "PAYTABS_PROFILE_ID must be a number"
            ) from error

    def create_payment(
        self,
        cart_id,
        amount,
        plan,
        customer_email,
        return_url,
        callback_url,
        customer_name=None,
        customer_phone=None,
    ):
        if not cart_id:
            raise PayTabsError("cart_id is required")

        if not plan:
            raise PayTabsError("plan is required")

        if not customer_email:
            raise PayTabsError("customer_email is required")

        if not return_url:
            raise PayTabsError("return_url is required")

        if not callback_url:
            raise PayTabsError("callback_url is required")

        try:
            amount = float(amount)
        except (TypeError, ValueError) as error:
            raise PayTabsError(
                "amount must be a number"
            ) from error

        if amount <= 0:
            raise PayTabsError(
                "amount must be greater than zero"
            )

        customer_details = {
            "email": customer_email,
        }

        if customer_name:
            customer_details["name"] = customer_name

        if customer_phone:
            customer_details["phone"] = customer_phone

        payload = {
            "profile_id": self.profile_id,
            "tran_type": "sale",
            "tran_class": "ecom",
            "cart_id": str(cart_id),
            "cart_description": (
                f"HMB FOREX AI - {plan} subscription"
            ),
            "cart_currency": "IQD",
            "cart_amount": amount,
            "callback": callback_url,
            "return": return_url,
            "customer_details": customer_details,
        }

        data = json.dumps(
            payload,
            separators=(",", ":"),
        ).encode("utf-8")

        request = urllib.request.Request(
            f"{self.base_url}/payment/request",
            data=data,
            method="POST",
            headers={
                "Authorization": self.server_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=20,
            ) as response:
                body = response.read().decode(
                    "utf-8",
                    errors="replace",
                )

                status_code = response.status

        except urllib.error.HTTPError as error:
            body = error.read().decode(
                "utf-8",
                errors="replace",
            )

            raise PayTabsError(
                f"PayTabs HTTP {error.code}: {body}"
            ) from error

        except urllib.error.URLError as error:
            raise PayTabsError(
                f"PayTabs connection error: {error}"
            ) from error

        except TimeoutError as error:
            raise PayTabsError(
                "PayTabs request timed out"
            ) from error

        try:
            result = json.loads(body)
        except json.JSONDecodeError as error:
            raise PayTabsError(
                "PayTabs returned invalid JSON"
            ) from error

        if status_code < 200 or status_code >= 300:
            raise PayTabsError(
                f"PayTabs HTTP {status_code}: {body}"
            )

        if not isinstance(result, dict):
            raise PayTabsError(
                "PayTabs returned an invalid response"
            )

        return result
