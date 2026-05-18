from apps.shipping.integrations.fedex.client import FedExClient
from apps.shipping.integrations.dhl.client import DHLClient


class ShippingRateService:
    @staticmethod
    def get_live_rates(payload):
        fedex = FedExClient()

        dhl = DHLClient()

        fedex_rates = fedex.get_shipping_rates(payload)

        dhl_rates = dhl.get_rates(payload)

        return {
            "fedex": fedex_rates,
            "dhl": dhl_rates,
        }