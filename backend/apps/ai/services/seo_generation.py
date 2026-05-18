from __future__ import annotations

import hashlib
import logging
import time
from dataclasses import (
    asdict,
    dataclass,
)
from threading import Lock
from typing import Any, Literal

from django.conf import settings

from openai import (
    AsyncOpenAI,
    OpenAIError,
)

from apps.ai.services.cache_service import (
    AsyncCacheService,
)


logger = logging.getLogger(__name__)


# TYPES
SEOContentType = Literal[
    "meta_title",
    "meta_description",
]


# DTOs
@dataclass(
    frozen=True,
    slots=True,
)
class SEOGenerationResult:
    content_type: SEOContentType

    generated_text: str

    model: str

    prompt_tokens: int

    completion_tokens: int

    total_tokens: int

    generation_time_seconds: float

    cache_hit: bool

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Serialize result safely.
        """

        return asdict(self)


# =========================================================
# SEO AI SERVICE
# =========================================================
class AISEOService:
    _client: AsyncOpenAI | None = None

    _lock = Lock()

    DEFAULT_MODEL = getattr(
        settings,
        "OPENAI_SEO_MODEL",
        "gpt-4o-mini",
    )

    MAX_INPUT_LENGTH = getattr(
        settings,
        "SEO_MAX_INPUT_LENGTH",
        5000,
    )

    DEFAULT_TEMPERATURE = getattr(
        settings,
        "SEO_TEMPERATURE",
        0.4,
    )

    CACHE_TIMEOUT = getattr(
        settings,
        "SEO_CACHE_TIMEOUT",
        3600,
    )

    # CLIENT MANAGEMENT
    @classmethod
    def get_client(
        cls,
    ) -> AsyncOpenAI:
        with cls._lock:
            if cls._client is None:
                logger.info(
                    (
                        "Initializing "
                        "OpenAI SEO client."
                    )
                )

                cls._client = AsyncOpenAI(
                    api_key=(
                        settings.OPENAI_API_KEY
                    ),
                )

                logger.info(
                    (
                        "OpenAI SEO client "
                        "initialized."
                    )
                )

        return cls._client

    # PUBLIC API
    @classmethod
    async def generate_meta_title(
        cls,
        product_name: str,
        description: str,
    ) -> SEOGenerationResult:
        """
        Generate SEO meta title.
        """

        prompt = cls.build_meta_title_prompt(
            product_name=product_name,
            description=description,
        )

        return await cls.generate(
            prompt=prompt,
            content_type="meta_title",
        )

    @classmethod
    async def generate_meta_description(
        cls,
        product_name: str,
        description: str,
    ) -> SEOGenerationResult:
        """
        Generate SEO meta description.
        """

        prompt = (
            cls.build_meta_description_prompt(
                product_name=product_name,
                description=description,
            )
        )

        return await cls.generate(
            prompt=prompt,
            content_type=(
                "meta_description"
            ),
        )

    # CORE GENERATION
    @classmethod
    async def generate(
        cls,
        prompt: str,
        content_type: SEOContentType,
    ) -> SEOGenerationResult:
        """
        Core SEO generation pipeline.
        """

        start_time = time.perf_counter()

        try:

            prompt = cls.validate_prompt(
                prompt,
            )

            cache_key = (
                cls.generate_cache_key(
                    prompt=prompt,
                    content_type=(
                        content_type
                    ),
                )
            )

            cached_result = (
                await AsyncCacheService.get(
                    key=cache_key,
                    namespace="seo",
                )
            )

            if cached_result:

                logger.info(
                    (
                        "SEO generation "
                        "loaded from cache."
                    )
                )

                return SEOGenerationResult(
                    **cached_result,
                )

            client = cls.get_client()

            logger.info(
                (
                    "Generating SEO %s "
                    "using model %s."
                ),
                content_type,
                cls.DEFAULT_MODEL,
            )

            response = (
                await client.chat.completions.create(
                    model=cls.DEFAULT_MODEL,
                    temperature=(
                        cls.DEFAULT_TEMPERATURE
                    ),
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are an expert "
                                "SEO strategist and "
                                "conversion-focused "
                                "copywriter."
                            ),
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                )
            )

            generated_text = (
                response.choices[0]
                .message.content.strip()
            )

            usage = response.usage

            elapsed_time = round(
                time.perf_counter()
                - start_time,
                4,
            )

            result = SEOGenerationResult(
                content_type=content_type,
                generated_text=(
                    generated_text
                ),
                model=cls.DEFAULT_MODEL,
                prompt_tokens=(
                    usage.prompt_tokens
                ),
                completion_tokens=(
                    usage.completion_tokens
                ),
                total_tokens=(
                    usage.total_tokens
                ),
                generation_time_seconds=(
                    elapsed_time
                ),
                cache_hit=False,
            )

            await AsyncCacheService.set(
                key=cache_key,
                value=result.to_dict(),
                timeout=(
                    cls.CACHE_TIMEOUT
                ),
                namespace="seo",
            )

            logger.info(
                (
                    "SEO generation "
                    "completed in %s seconds."
                ),
                elapsed_time,
            )

            return result

        except OpenAIError as exc:
            logger.exception(
                (
                    "OpenAI SEO generation "
                    "failed: %s"
                ),
                exc,
            )

            raise

        except Exception as exc:
            logger.exception(
                (
                    "Unexpected SEO "
                    "generation error: %s"
                ),
                exc,
            )

            raise

    # PROMPT BUILDERS
    @staticmethod
    def build_meta_title_prompt(
        product_name: str,
        description: str,
    ) -> str:
        """
        Build SEO meta title prompt.
        """

        return f"""
Generate a professional SEO meta title.

Requirements:
- Maximum 60 characters
- SEO optimized
- Human readable
- High CTR focused
- Use sentence case
- No quotation marks

Product Name:
{product_name}

Description:
{description}
""".strip()

    @staticmethod
    def build_meta_description_prompt(
        product_name: str,
        description: str,
    ) -> str:
        """
        Build SEO meta description prompt.
        """

        return f"""
Generate a professional SEO meta description.

Requirements:
- Maximum 155 characters
- SEO optimized
- Human readable
- High CTR focused
- Use sentence case
- No quotation marks

Product Name:
{product_name}

Description:
{description}
""".strip()

    # VALIDATION
    @classmethod
    def validate_prompt(
        cls,
        prompt: str,
    ) -> str:
        """
        Validate and sanitize prompt safely.
        """

        prompt = (
            str(prompt or "")
            .strip()
        )

        if not prompt:

            raise ValueError(
                "Prompt cannot be empty."
            )

        if (
            len(prompt)
            > cls.MAX_INPUT_LENGTH
        ):

            raise ValueError(
                (
                    "Prompt exceeds "
                    "maximum allowed length."
                )
            )

        return prompt

    # CACHE HELPERS
    @staticmethod
    def generate_cache_key(
        prompt: str,
        content_type: str,
    ) -> str:
        """
        Generate stable cache key.
        """

        cache_payload = (
            f"{content_type}:{prompt}"
        )

        content_hash = hashlib.sha256(
            cache_payload.encode("utf-8")
        ).hexdigest()

        return (
            f"seo-generation:"
            f"{content_hash}"
        )

    # HEALTH UTILITIES
    @classmethod
    def is_initialized(
        cls,
    ) -> bool:
        return (
            cls._client
            is not None
        )