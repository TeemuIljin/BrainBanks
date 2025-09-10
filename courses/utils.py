"""
Utility functions for the courses app.
"""
from django.core.cache import cache
from django.db import models
from functools import wraps
import logging

logger = logging.getLogger(__name__)


def cache_view(timeout=300, key_prefix=''):
    """
    Decorator to cache view results.
    
    Args:
        timeout: Cache timeout in seconds (default: 5 minutes)
        key_prefix: Prefix for cache key
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Create cache key based on request path and user
            user_id = request.user.id if request.user.is_authenticated else 'anonymous'
            cache_key = f"{key_prefix}_{view_func.__name__}_{request.path}_{user_id}"
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_result
            
            # Execute view and cache result
            result = view_func(request, *args, **kwargs)
            cache.set(cache_key, result, timeout)
            logger.debug(f"Cached result for {cache_key}")
            
            return result
        return wrapper
    return decorator


def get_or_create_player_profile(user):
    """
    Get or create player profile with error handling.
    
    Args:
        user: Django User instance
        
    Returns:
        PlayerProfile instance or None if error
    """
    try:
        from .models import PlayerProfile
        profile, created = PlayerProfile.objects.get_or_create(user=user)
        if created:
            logger.info(f"Created new player profile for user {user.username}")
        return profile
    except Exception as e:
        logger.error(f"Error getting/creating player profile for user {user.id}: {e}")
        return None


def invalidate_user_cache(user_id):
    """
    Invalidate all cache entries for a specific user.
    
    Args:
        user_id: User ID to invalidate cache for
    """
    # This is a simple implementation - in production you might want
    # to use cache versioning or more sophisticated invalidation
    cache.clear()
    logger.info(f"Cleared cache for user {user_id}")


def get_cached_leaderboard(timeout=300):
    """
    Get cached leaderboard data.
    
    Args:
        timeout: Cache timeout in seconds
        
    Returns:
        Cached leaderboard data or None
    """
    cache_key = 'leaderboard_data'
    return cache.get(cache_key)


def set_cached_leaderboard(data, timeout=300):
    """
    Cache leaderboard data.
    
    Args:
        data: Leaderboard data to cache
        timeout: Cache timeout in seconds
    """
    cache_key = 'leaderboard_data'
    cache.set(cache_key, data, timeout)
    logger.debug("Cached leaderboard data")
