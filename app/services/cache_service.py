"""
Cache Service for Horoscope API
Handles caching of horoscope responses with TTL
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import redis
from app.config import settings


class CacheService:
    """Service for caching horoscope responses with TTL"""
    
    def __init__(self):
        self.redis_client = None
        self.cache_ttl = settings.cache_ttl_minutes * 60  # Convert to seconds
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection"""
        try:
            if settings.redis_url:
                self.redis_client = redis.from_url(settings.redis_url)
                # Test connection
                self.redis_client.ping()
                print("✅ Redis cache initialized successfully")
            else:
                print("⚠️ Redis URL not configured, caching disabled")
                self.redis_client = None
        except Exception as e:
            print(f"❌ Redis connection failed: {e}")
            print("⚠️ Caching disabled, continuing without cache")
            self.redis_client = None
    
    def _generate_cache_key(self, user_name: str, birth_date: str, birth_time: str, birth_place: str) -> str:
        """Generate a unique cache key for user details"""
        # Create a hash of user details for consistent cache key
        user_data = f"{user_name}_{birth_date}_{birth_time}_{birth_place}"
        return f"horoscope:{hashlib.md5(user_data.encode()).hexdigest()}"
    
    def get_cached_response(self, user_name: str, birth_date: str, birth_time: str, birth_place: str) -> Optional[Dict[str, Any]]:
        """
        Get cached horoscope response if it exists and is not expired
        
        Args:
            user_name: User's name
            birth_date: User's birth date
            birth_time: User's birth time
            birth_place: User's birth place
            
        Returns:
            Cached response dict or None if not found/expired
        """
        print(f"🔍 DEBUG: Cache lookup for user: {user_name}")
        
        if not self.redis_client:
            print(f"❌ DEBUG: Redis client not available, cache disabled")
            return None
        
        try:
            cache_key = self._generate_cache_key(user_name, birth_date, birth_time, birth_place)
            print(f"🔑 DEBUG: Generated cache key: {cache_key}")
            
            cached_data = self.redis_client.get(cache_key)
            
            if cached_data:
                response_data = json.loads(cached_data)
                print(f"✅ DEBUG: Cache HIT for user: {user_name}")
                print(f"📋 DEBUG: Cached data keys: {list(response_data.keys())}")
                if 'cached_at' in response_data:
                    print(f"⏰ DEBUG: Cached at: {response_data['cached_at']}")
                return response_data
            else:
                print(f"❌ DEBUG: Cache MISS for user: {user_name}")
                return None
                
        except Exception as e:
            print(f"❌ DEBUG: Error retrieving from cache: {e}")
            return None
    
    def cache_response(self, user_name: str, birth_date: str, birth_time: str, birth_place: str, response: Dict[str, Any]) -> bool:
        """
        Cache horoscope response with TTL
        
        Args:
            user_name: User's name
            birth_date: User's birth date
            birth_time: User's birth time
            birth_place: User's birth place
            response: Horoscope response to cache
            
        Returns:
            True if cached successfully, False otherwise
        """
        print(f"💾 DEBUG: Attempting to cache response for user: {user_name}")
        
        if not self.redis_client:
            print(f"❌ DEBUG: Redis client not available, cannot cache")
            return False
        
        try:
            cache_key = self._generate_cache_key(user_name, birth_date, birth_time, birth_place)
            print(f"🔑 DEBUG: Cache key for storage: {cache_key}")
            
            # Add cache timestamp
            response_with_timestamp = {
                **response,
                "cached_at": datetime.now().isoformat(),
                "cache_ttl_minutes": settings.cache_ttl_minutes
            }
            print(f"📋 DEBUG: Response with timestamp: {list(response_with_timestamp.keys())}")
            
            # Cache with TTL
            self.redis_client.setex(
                cache_key,
                self.cache_ttl,
                json.dumps(response_with_timestamp)
            )
            
            print(f"✅ DEBUG: Successfully cached response for user: {user_name}")
            print(f"⏰ DEBUG: TTL set to {settings.cache_ttl_minutes} minutes ({self.cache_ttl} seconds)")
            return True
            
        except Exception as e:
            print(f"❌ DEBUG: Error caching response: {e}")
            return False
    
    def invalidate_cache(self, user_name: str, birth_date: str, birth_time: str, birth_place: str) -> bool:
        """
        Invalidate cached response for a user
        
        Args:
            user_name: User's name
            birth_date: User's birth date
            birth_time: User's birth time
            birth_place: User's birth place
            
        Returns:
            True if invalidated successfully, False otherwise
        """
        if not self.redis_client:
            return False
        
        try:
            cache_key = self._generate_cache_key(user_name, birth_date, birth_time, birth_place)
            self.redis_client.delete(cache_key)
            print(f"🗑️ Invalidated cache for user: {user_name}")
            return True
            
        except Exception as e:
            print(f"❌ Error invalidating cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.redis_client:
            return {"status": "disabled", "reason": "Redis not configured"}
        
        try:
            # Get all horoscope cache keys
            keys = self.redis_client.keys("horoscope:*")
            total_keys = len(keys)
            
            # Get TTL for a sample key
            sample_ttl = None
            if keys:
                sample_ttl = self.redis_client.ttl(keys[0])
            
            return {
                "status": "active",
                "total_cached_responses": total_keys,
                "cache_ttl_minutes": settings.cache_ttl_minutes,
                "sample_ttl_seconds": sample_ttl,
                "redis_url": settings.redis_url
            }
            
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def clear_all_cache(self) -> bool:
        """Clear all cached horoscope responses"""
        if not self.redis_client:
            return False
        
        try:
            keys = self.redis_client.keys("horoscope:*")
            if keys:
                self.redis_client.delete(*keys)
                print(f"🗑️ Cleared {len(keys)} cached responses")
            return True
            
        except Exception as e:
            print(f"❌ Error clearing cache: {e}")
            return False
