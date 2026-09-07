from abc import ABC, abstractmethod


class BasePaymentGateway(ABC):

    @abstractmethod
    def request_payment(self, *, payment, callback_url):
        pass

    @abstractmethod
    def verify_payment(self, *, payment):
        pass

    @abstractmethod
    def get_payment_url(self, authority):
        pass