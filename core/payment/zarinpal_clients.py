import requests
from django.conf import settings


class ZarinPalSandbox:
    ZP_API_REQUEST = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
    ZP_API_VERIFY = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
    ZP_API_STARTPAY = "https://sandbox.zarinpal.com/pg/StartPay/"

    def __init__(self, merchant, amount, callback_url=None):
        self.merchant = merchant
        self.amount = int(amount)
        self.callback_url = callback_url or settings.ZARINPAL_CALLBACK_URL

    def payment_request(self, description="پرداخت سفارش"):
        payload = {
            "merchant_id": self.merchant,
            "amount": self.amount,
            "callback_url": self.callback_url,
            "description": description,
        }

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        response = requests.post(
            self.ZP_API_REQUEST,
            json=payload,
            headers=headers,
            timeout=15
        )

        if response.status_code != 200:
            raise Exception("ZarinPal request connection error")

        data = response.json().get("data")
        errors = response.json().get("errors")

        if errors:
            raise Exception(f"ZarinPal error: {errors}")

        authority = data.get("authority")
        if not authority:
            raise Exception("Authority not returned from ZarinPal")

        return authority

    def payment_verify(self, authority):
        payload = {
            "merchant_id": self.merchant,
            "amount": self.amount,
            "authority": authority
        }

        headers = {
            "Content-Type": "application/json"
        }

        response = requests.post(
            self.ZP_API_VERIFY,
            json=payload,
            headers=headers,
            timeout=15
        )

        if response.status_code != 200:
            raise Exception("ZarinPal verify connection error")

        data = response.json().get("data")
        errors = response.json().get("errors")

        if errors:
            return {
                "success": False,
                "errors": errors
            }

        return {
            "success": data.get("code") in (100, 101),
            "ref_id": data.get("ref_id"),
            "code": data.get("code"),
            "raw": data
        }

    def generate_payment_url(self, authority):
        return f"{self.ZP_API_STARTPAY}{authority}"