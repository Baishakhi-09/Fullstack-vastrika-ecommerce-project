from __future__ import annotations

import json
import logging
from threading import Lock
from typing import Any

import redis.asyncio as redis

from django.conf import settings

from redis.exceptions import (
    RedisError,
)


logger = logging.getLogger(__name__)


# =========================================================
# CACHE SERVICE
# =========================================================
class AsyncCacheService:
    _client: redis.Redis | None = None

    _lock = Lock()

    DEFAULT_TIMEOUT = getattr(
        settings,
        "CACHE_DEFAULT_TIMEOUT",
        1800,
    )

    REDIS_URL = getattr(
        settings,
        "REDIS_URL",
        "redis://127.0.0.1:6379/1",
    )

    # CLIENT MANAGEMENT
    @classmethod
    def get_client(
        cls,
    ) -> redis.Redis:
        with cls._lock:
            if cls._client is None:
                logger.info(
                    "Initializing Redis client."
                )

                cls._client = (
                    redis.Redis.from_url(
                        cls.REDIS_URL,
                        decode_responses=True,
                    )
                )

                logger.info(
                    "Redis client initialized."
                )

        return cls._client

    # KEY HELPERS
    @staticmethod
    def build_key(
        namespace: str,
        key: str,
    ) -> str:
        return (
            f"{namespace.strip()}:"
            f"{key.strip()}"
        )

    # SERIALIZATION
    @staticmethod
    def serialize(
        value: Any,
    ) -> str:
        try:
            return json.dumps(
                value,
                default=str,
            )

        except Exception as exc:
            logger.exception(
                (
                    "Cache serialization "
                    "failed: %s"
                ),
                exc,
            )

            raise

    @staticmethod
    def deserialize(
        value: str,
    ) -> Any:
        try:
            return json.loads(value)

        except Exception as exc:
            logger.exception(
                (
                    "Cache deserialization "
                    "failed: %s"
                ),
                exc,
            )

            raise

    # CACHE OPERATIONS
    @classmethod
    async def get(
        cls,
        key: str,
        namespace: str = "default",
    ) -> Any | None:
        try:
            redis_client = cls.get_client()

            cache_key = cls.build_key(
                namespace,
                key,
            )

            data = await redis_client.get(
                cache_key,
            )

            if data is None:
                logger.info(
                    (
                        "Cache miss for key: %s"
                    ),
                    cache_key,
                )

                return None

            logger.info(
                (
                    "Cache hit for key: %s"
                ),
                cache_key,
            )

            return cls.deserialize(data)

        except RedisError as exc:
            logger.exception(
                (
                    "Redis GET operation "
                    "failed: %s"
                ),
                exc,
            )

            return None

    @classmethod
    async def set(
        cls,
        key: str,
        value: Any,
        timeout: int | None = None,
        namespace: str = "default",
    ) -> bool:
        try:
            redis_client = cls.get_client()

            cache_key = cls.build_key(
                namespace,
                key,
            )

            ttl = (
                timeout
                if timeout is not None
                else cls.DEFAULT_TIMEOUT
            )

            if ttl <= 0:
                raise ValueError(
                    (
                        "Cache timeout "
                        "must be positive."
                    )
                )

            serialized_value = (
                cls.serialize(value)
            )

            await redis_client.set(
                cache_key,
                serialized_value,
                ex=ttl,
            )

            logger.info(
                (
                    "Cache set successful "
                    "for key: %s"
                ),
                cache_key,
            )

            return True

        except (
            RedisError,
            ValueError,
        ) as exc:
            logger.exception(
                (
                    "Redis SET operation "
                    "failed: %s"
                ),
                exc,
            )

            return False

    @classmethod
    async def delete(
        cls,
        key: str,
        namespace: str = "default",
    ) -> bool:
        try:
            redis_client = cls.get_client()

            cache_key = cls.build_key(
                namespace,
                key,
            )

            await redis_client.delete(
                cache_key,
            )

            logger.info(
                (
                    "Cache delete successful "
                    "for key: %s"
                ),
                cache_key,
            )

            return True

        except RedisError as exc:
            logger.exception(
                (
                    "Redis DELETE operation "
                    "failed: %s"
                ),
                exc,
            )

            return False

    @classmethod
    async def exists(
        cls,
        key: str,
        namespace: str = "default",
    ) -> bool:
        try:
            redis_client = cls.get_client()

            cache_key = cls.build_key(
                namespace,
                key,
            )

            result = await redis_client.exists(
                cache_key,
            )

            return bool(result)

        except RedisError as exc:
            logger.exception(
                (
                    "Redis EXISTS operation "
                    "failed: %s"
                ),
                exc,
            )

            return False

    # HEALTH CHECKS
    @classmethod
    async def ping(
        cls,
    ) -> bool:
        try:
            redis_client = cls.get_client()

            result = await redis_client.ping()

            logger.info(
                "Redis ping successful."
            )

            return bool(result)

        except RedisError as exc:
            logger.exception(
                (
                    "Redis ping failed: %s"
                ),
                exc,
            )

            return False

    # CONNECTION MANAGEMENT
    @classmethod
    async def close(
        cls,
    ) -> None:
        try:
            if cls._client is not None:
                logger.info(
                    "Closing Redis client."
                )

                await cls._client.close()

                cls._client = None

                logger.info(
                    "Redis client closed."
                )

        except RedisError as exc:
            logger.exception(
                (
                    "Redis client close "
                    "failed: %s"
                ),
                exc,
            )