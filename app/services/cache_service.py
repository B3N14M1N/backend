from typing import Optional, List

from app.core.caching import redis_client


class CacheService:
    """Service for caching operations."""
    
    def __init__(self):
        self.redis = redis_client()
    
    async def get_templates_cache(self, cache_key: str) -> Optional[List[dict]]:
        """Get cached templates."""
        try:
            cached = self.redis.get(cache_key)
            if cached:
                # Parse the custom serialization format
                items = []
                for s in cached.split("||"):
                    if not s:
                        continue
                    parts = s.split("::", 3)
                    items.append({
                        "id": int(parts[0]),
                        "title": parts[1],
                        "status": parts[2],
                        "created_at": parts[3]
                    })
                return items
        except Exception:
            pass
        return None
    
    async def set_templates_cache(self, cache_key: str, templates: List[dict], ttl: int = 30) -> None:
        """Set templates cache."""
        try:
            # Use the same serialization format for compatibility
            serialized = "||".join([
                f"{item['id']}::{item['title']}::{item['status']}::{item['created_at']}"
                for item in templates
            ])
            self.redis.set(cache_key, serialized, ex=ttl)
        except Exception:
            pass
    
    async def invalidate_cache(self, cache_key: str) -> None:
        """Invalidate cache entry."""
        try:
            self.redis.delete(cache_key)
        except Exception:
            pass
