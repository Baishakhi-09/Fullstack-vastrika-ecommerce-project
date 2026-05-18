from __future__ import annotations

import logging
from datetime import (
    date,
    timedelta,
)
from functools import lru_cache
from typing import Any

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.utils.timezone import now

from google.oauth2.service_account import (
    Credentials,
)
from googleapiclient.discovery import (
    Resource,
    build,
)
from googleapiclient.errors import (
    HttpError,
)


logger = logging.getLogger(__name__)


# CONSTANTS
DEFAULT_ANALYTICS_DAYS = 30

DEFAULT_ROW_LIMIT = 100

CACHE_TIMEOUT = 60 * 30

SCOPES = (
    "https://www.googleapis.com/auth/webmasters.readonly",
)


# =========================================================
# GOOGLE SEARCH CONSOLE SERVICE
# =========================================================
class GoogleSearchConsoleService:
    # INITIALIZATION
    def __init__(
        self,
    ) -> None:

        self.service = (
            self.get_service()
        )

    # GOOGLE CLIENT
    @staticmethod
    @lru_cache(maxsize=1)
    def get_service() -> Resource:
        credentials_path = getattr(
            settings,
            "GSC_CREDENTIALS_PATH",
            None,
        )

        if not credentials_path:
            raise ValidationError(
                (
                    "GSC_CREDENTIALS_PATH "
                    "is not configured."
                )
            )

        credentials = (
            Credentials.from_service_account_file(
                credentials_path,
                scopes=SCOPES,
            )
        )

        logger.info(
            (
                "Initializing Google "
                "Search Console client."
            )
        )

        return build(
            "searchconsole",
            "v1",
            credentials=credentials,
            cache_discovery=False,
        )

    # ANALYTICS API
    def get_search_analytics(
        self,
        *,
        site_url: str,
        page_url: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        dimensions: list[str] | None = None,
        row_limit: int = DEFAULT_ROW_LIMIT,
    ) -> dict[str, Any]:
        self.validate_site_url(
            site_url,
        )

        if page_url:
            self.validate_page_url(
                page_url,
            )

        end_date = (
            end_date
            or now().date()
        )

        start_date = (
            start_date
            or (
                end_date
                - timedelta(
                    days=DEFAULT_ANALYTICS_DAYS
                )
            )
        )

        dimensions = (
            dimensions
            or ["query"]
        )

        cache_key = (
            f"gsc_analytics:"
            f"{site_url}:"
            f"{page_url}:"
            f"{start_date}:"
            f"{end_date}:"
            f"{','.join(dimensions)}:"
            f"{row_limit}"
        )

        cached_data = cache.get(
            cache_key,
        )

        if cached_data:
            logger.debug(
                (
                    "Returning cached GSC "
                    "analytics response."
                )
            )

            return cached_data

        request_body = {
            "startDate": str(
                start_date
            ),
            "endDate": str(
                end_date
            ),
            "dimensions": dimensions,
            "rowLimit": row_limit,
        }

        if page_url:
            request_body[
                "dimensionFilterGroups"
            ] = [
                {
                    "filters": [
                        {
                            "dimension": "page",
                            "operator": "equals",
                            "expression": page_url,
                        }
                    ]
                }
            ]

        logger.info(
            (
                "Fetching GSC analytics "
                "for site=%s"
            ),
            site_url,
        )

        try:
            response = (
                self.service.searchanalytics()
                .query(
                    siteUrl=site_url,
                    body=request_body,
                )
                .execute()
            )

            normalized_response = (
                self.normalize_response(
                    response,
                )
            )

            cache.set(
                cache_key,
                normalized_response,
                timeout=CACHE_TIMEOUT,
            )

            return normalized_response

        except HttpError as exc:
            logger.exception(
                (
                    "Google Search Console "
                    "API error: %s"
                ),
                exc,
            )

            raise ValidationError(
                (
                    "Failed to fetch "
                    "Google Search Console "
                    "analytics."
                )
            ) from exc

        except Exception as exc:
            logger.exception(
                (
                    "Unexpected GSC "
                    "service error: %s"
                ),
                exc,
            )

            raise

    # RESPONSE NORMALIZATION
    @staticmethod
    def normalize_response(
        response: dict[str, Any],
    ) -> dict[str, Any]:
        rows = response.get(
            "rows",
            [],
        )

        normalized_rows = []

        for row in rows:
            normalized_rows.append(
                {
                    "keys": row.get(
                        "keys",
                        [],
                    ),
                    "clicks": row.get(
                        "clicks",
                        0,
                    ),
                    "impressions": row.get(
                        "impressions",
                        0,
                    ),
                    "ctr": row.get(
                        "ctr",
                        0,
                    ),
                    "position": row.get(
                        "position",
                        0,
                    ),
                }
            )

        return {
            "rows": normalized_rows,
            "total_rows": len(
                normalized_rows
            ),
        }

    # VALIDATION
    @staticmethod
    def validate_site_url(
        site_url: str,
    ) -> None:
        """
        Validate GSC property URL.
        """

        if not site_url:

            raise ValidationError(
                "Site URL is required."
            )

        if not (
            site_url.startswith(
                "http://"
            )
            or site_url.startswith(
                "https://"
            )
        ):

            raise ValidationError(
                (
                    "Invalid site URL "
                    "format."
                )
            )

    @staticmethod
    def validate_page_url(
        page_url: str,
    ) -> None:
        """
        Validate page URL.
        """

        if not (
            page_url.startswith(
                "http://"
            )
            or page_url.startswith(
                "https://"
            )
        ):

            raise ValidationError(
                (
                    "Invalid page URL "
                    "format."
                )
            )