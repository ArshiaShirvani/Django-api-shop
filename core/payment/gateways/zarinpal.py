import requests

from django.conf import settings

from .base import BasePaymentGateway


class ZarinPalGateway(BasePaymentGateway):

    # =========================================================
    # PRODUCTION
    # =========================================================

    PRODUCTION_REQUEST_URL = (
        "https://api.zarinpal.com/pg/v4/payment/request.json"
    )

    PRODUCTION_VERIFY_URL = (
        "https://api.zarinpal.com/pg/v4/payment/verify.json"
    )

    PRODUCTION_STARTPAY_URL = (
        "https://www.zarinpal.com/pg/StartPay/"
    )

    # =========================================================
    # SANDBOX
    # =========================================================

    SANDBOX_REQUEST_URL = (
        "https://sandbox.zarinpal.com/pg/v4/payment/request.json"
    )

    SANDBOX_VERIFY_URL = (
        "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"
    )

    SANDBOX_STARTPAY_URL = (
        "https://sandbox.zarinpal.com/pg/StartPay/"
    )

    # =========================================================
    # INIT
    # =========================================================

    def __init__(self):

        self.merchant_id = getattr(
            settings,
            "ZARINPAL_MERCHANT_ID",
            "",
        )

        self.sandbox = getattr(
            settings,
            "ZARINPAL_SANDBOX",
            True,
        )

        if not self.merchant_id:
            raise ValueError(
                "ZARINPAL_MERCHANT_ID "
                "در settings تنظیم نشده است."
            )

    # =========================================================
    # URLS
    # =========================================================

    @property
    def request_url(self):

        if self.sandbox:
            return self.SANDBOX_REQUEST_URL

        return self.PRODUCTION_REQUEST_URL

    @property
    def verify_url(self):

        if self.sandbox:
            return self.SANDBOX_VERIFY_URL

        return self.PRODUCTION_VERIFY_URL

    @property
    def startpay_url(self):

        if self.sandbox:
            return self.SANDBOX_STARTPAY_URL

        return self.PRODUCTION_STARTPAY_URL

    # =========================================================
    # REQUEST PAYMENT
    # =========================================================

    def request_payment(
        self,
        *,
        payment,
        callback_url,
    ):

        data = {
            "merchant_id": self.merchant_id,

            "amount": int(payment.amount),

            "description": (
                f"پرداخت سفارش #{payment.order_id}"
            ),

            "callback_url": callback_url,

            "metadata": {
                "mobile": payment.user.phone_number,
            },
        }

        try:

            response = requests.post(
                self.request_url,
                json=data,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                timeout=15,
            )

        except requests.RequestException as exc:

            return {
                "success": False,
                "error_code": "REQUEST_ERROR",
                "error_message": str(exc),
                "raw_response": {},
            }

        # =====================================================
        # RESPONSE PARSE
        # =====================================================

        try:

            result = response.json()

        except ValueError:

            return {
                "success": False,
                "error_code": "INVALID_RESPONSE",
                "error_message": (
                    "پاسخ دریافتی از زرین‌پال JSON معتبر نیست."
                ),
                "raw_response": {
                    "http_status": response.status_code,
                    "response_text": response.text,
                },
            }

        # =====================================================
        # RESPONSE DATA
        # =====================================================

        data_result = result.get(
            "data",
            {},
        )

        errors = result.get(
            "errors",
            {},
        )

        code = data_result.get(
            "code"
        )

        # =====================================================
        # ERROR
        # =====================================================

        if response.status_code >= 400 or code != 100:

            error_code = (
                errors.get("code")
                or data_result.get("code")
                or response.status_code
            )

            error_message = (
                errors.get("message")
                or result.get("message")
                or "خطا در ایجاد درخواست پرداخت."
            )

            return {
                "success": False,

                "error_code": error_code,

                "error_message": error_message,

                "raw_response": {
                    "http_status": response.status_code,
                    "response": result,
                },
            }

        # =====================================================
        # AUTHORITY
        # =====================================================

        authority = data_result.get(
            "authority"
        )

        if not authority:

            return {
                "success": False,

                "error_code": "NO_AUTHORITY",

                "error_message": (
                    "زرین‌پال Authority برنگرداند."
                ),

                "raw_response": {
                    "http_status": response.status_code,
                    "response": result,
                },
            }

        # =====================================================
        # SUCCESS
        # =====================================================

        return {
            "success": True,

            "authority": authority,

            "payment_url": self.get_payment_url(
                authority
            ),

            "raw_response": {
                "http_status": response.status_code,
                "response": result,
            },
        }

    # =========================================================
    # VERIFY PAYMENT
    # =========================================================

    def verify_payment(
        self,
        *,
        payment,
    ):

        # =====================================================
        # AUTHORITY CHECK
        # =====================================================

        if not payment.authority:

            return {
                "success": False,

                "error_code": "NO_AUTHORITY",

                "error_message": (
                    "Authority برای این پرداخت وجود ندارد."
                ),

                "raw_response": {},
            }

        # =====================================================
        # VERIFY DATA
        # =====================================================

        data = {
            "merchant_id": self.merchant_id,

            "amount": int(payment.amount),

            "authority": payment.authority,
        }

        # =====================================================
        # REQUEST
        # =====================================================

        try:

            response = requests.post(
                self.verify_url,
                json=data,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                timeout=15,
            )

        except requests.RequestException as exc:

            return {
                "success": False,

                "error_code": "VERIFY_REQUEST_ERROR",

                "error_message": str(exc),

                "raw_response": {},
            }

        # =====================================================
        # RESPONSE PARSE
        # =====================================================

        try:

            result = response.json()

        except ValueError:

            return {
                "success": False,

                "error_code": "INVALID_RESPONSE",

                "error_message": (
                    "پاسخ Verify از زرین‌پال "
                    "JSON معتبر نیست."
                ),

                "raw_response": {
                    "http_status": response.status_code,
                    "response_text": response.text,
                },
            }

        # =====================================================
        # RESPONSE DATA
        # =====================================================

        data_result = result.get(
            "data",
            {},
        )

        errors = result.get(
            "errors",
            {},
        )

        code = data_result.get(
            "code"
        )

        # =====================================================
        # VERIFY ERROR
        # =====================================================

        if response.status_code >= 400 or code not in (100, 101):

            error_code = (
                errors.get("code")
                or data_result.get("code")
                or response.status_code
            )

            error_message = (
                errors.get("message")
                or result.get("message")
                or "پرداخت تأیید نشد."
            )

            return {
                "success": False,

                "error_code": error_code,

                "error_message": error_message,

                "raw_response": {
                    "http_status": response.status_code,
                    "response": result,
                },
            }

        # =====================================================
        # VERIFY SUCCESS
        # =====================================================

        return {
            "success": True,

            "ref_id": data_result.get(
                "ref_id"
            ),

            "raw_response": {
                "http_status": response.status_code,
                "response": result,
            },
        }

    # =========================================================
    # PAYMENT URL
    # =========================================================

    def get_payment_url(
        self,
        authority,
    ):

        if not authority:

            raise ValueError(
                "Authority معتبر نیست."
            )

        return (
            f"{self.startpay_url}"
            f"{authority}"
        )