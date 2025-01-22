from functools import wraps
import json
from typing import Optional, Any, Callable
import redis
import logging
import hashlib
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class TravelCache:
    def __init__(self, redis_url: str = "redis://localhost:6379/0", default_ttl: int = 3600):
        """Initialize Redis cache with connection and default TTL."""
        try:
            self.redis_client = redis.from_url(redis_url)
            self.default_ttl = default_ttl
        except redis.RedisError as e:
            logger.warning(f"Failed to initialize Redis connection: {str(e)}. Caching will be disabled.")
            self.redis_client = None

    def _generate_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate a unique cache key based on function arguments."""
        key_parts = [prefix]
        if args:
            key_parts.append(str(args))
        if kwargs:
            sorted_kwargs = sorted(kwargs.items())
            key_parts.append(str(sorted_kwargs))
        
        key_string = ":".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()

    def cache_decorator(self, ttl: Optional[int] = None, prefix: Optional[str] = None):
        """Decorator for caching function results."""
        def decorator(func: Callable):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                if not self.redis_client:
                    return await func(*args, **kwargs)

                cache_prefix = prefix or func.__name__
                cache_key = self._generate_cache_key(cache_prefix, *args, **kwargs)
                
                try:
                    # Try to get cached result
                    cached_result = self.redis_client.get(cache_key)
                    if cached_result:
                        logger.debug(f"Cache hit for key: {cache_key}")
                        return json.loads(cached_result)
                except redis.RedisError as e:
                    logger.error(f"Redis error while getting cached value: {str(e)}")
                    return await func(*args, **kwargs)
                
                # Execute function if cache miss
                logger.debug(f"Cache miss for key: {cache_key}")
                result = await func(*args, **kwargs)
                
                # Cache the result
                try:
                    cache_ttl = ttl or self.default_ttl
                    self.redis_client.setex(
                        cache_key,
                        cache_ttl,
                        json.dumps(result)
                    )
                except (redis.RedisError, TypeError) as e:
                    logger.error(f"Failed to cache result: {str(e)}")
                
                return result
            return wrapper
        return decorator

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all cache keys matching the given pattern."""
        if not self.redis_client:
            return 0
            
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except redis.RedisError as e:
            logger.error(f"Failed to invalidate cache pattern {pattern}: {str(e)}")
            raise HTTPException(status_code=500, detail="Cache invalidation failed")