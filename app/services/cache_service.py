from typing import Optional, List
import json

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
                # Try JSON first (new format)
                try:
                    return json.loads(cached)
                except json.JSONDecodeError:
                    # Fall back to old custom format for backward compatibility
                    items = []
                    for s in cached.split("||"):
                        if not s:
                            continue
                        parts = s.split("::", 3)
                        items.append({
                            "id": int(parts[0]),  # This will fail with UUID
                            "title": parts[1],
                            "status": parts[2],
                            "created_at": parts[3]
                        })
                    return items
        except Exception as e:
            print(f"CACHE DEBUG: Error getting cache: {e}")
        return None
    
    async def set_templates_cache(self, cache_key: str, templates: List[dict], ttl: int = 30) -> None:
        """Set templates cache using JSON format."""
        try:
            # Use JSON format for better compatibility with UUIDs and complex data
            serialized = json.dumps(templates, default=str)  # default=str handles UUID serialization
            self.redis.set(cache_key, serialized, ex=ttl)
            print(f"CACHE DEBUG: Set cache {cache_key} with {len(templates)} templates")
        except Exception as e:
            print(f"CACHE DEBUG: Error setting cache: {e}")
    
    async def invalidate_cache(self, cache_key: str) -> None:
        """Invalidate cache entry."""
        try:
            deleted = self.redis.delete(cache_key)
            print(f"CACHE DEBUG: Invalidated cache {cache_key}, deleted: {deleted}")
        except Exception as e:
            print(f"CACHE DEBUG: Error invalidating cache: {e}")
        except Exception:
            pass
