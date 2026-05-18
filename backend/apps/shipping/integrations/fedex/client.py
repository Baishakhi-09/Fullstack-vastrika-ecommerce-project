import requests
from django.conf import settings

class FedExClient:

    BASE_URL = "https://api.fedex.com"

    def __init__(self):

        self.api_key = settings.FEDEX_API_KEY

        self.secret_key = settings.FEDEX_SECRET_KEY

    def get_shipping_rates(self, payload):

        response = requests.post(
            f"{self.BASE_URL}/rates",
            json=payload,
            timeout=30,
        )

        return response.json()