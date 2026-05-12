import json

import redis.asyncio as redis
from django.conf import settings


class AsyncCacheService:
    """
    Enterprise async Redis cache service.
    """

    _client = redis.Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
    )

    @classmethod
    async def get(cls, key: str):
        data = await cls._client.get(key)

        if not data:
            return None

        return json.loads(data)

    @classmethod
    async def set(
        cls,
        key: str,
        value,
        timeout: int = 1800,
    ):
        await cls._client.set(
            key,
            json.dumps(value),
            ex=timeout,
        )