from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from django.conf import settings

class GoogleSearchConsoleService:
    SCOPES = [
        "https://www.googleapis.com/auth/webmasters.readonly"
    ]

    def __init__(self):
        credentials = Credentials.from_service_account_file(
            settings.GSC_CREDENTIALS_PATH,
            scopes=self.SCOPES,
        )

        self.service = build(
            "searchconsole",
            "v1",
            credentials=credentials,
        )

    def get_search_analytics(self, site_url, page_url):
        request = {
            "startDate": "2025-01-01",
            "endDate": "2025-12-31",
            "dimensions": ["query"],
            "dimensionFilterGroups": [
                {
                    "filters": [
                        {
                            "dimension": "page",
                            "operator": "equals",
                            "expression": page_url,
                        }
                    ]
                }
            ],
        }

        response = (
            self.service.searchanalytics()
            .query(siteUrl=site_url, body=request)
            .execute()
        )

        return response