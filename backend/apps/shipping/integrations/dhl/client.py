import requests
from django.conf import settings


class DHLClient:
    BASE_URL = "https://api.dhl.com"

    def __init__(self):
        self.api_key = settings.DHL_API_KEY

    def get_rates(self, payload):
        response = requests.post(
            f"{self.BASE_URL}/rates",
            json=payload,
            timeout=30,
        )

        return response.json()