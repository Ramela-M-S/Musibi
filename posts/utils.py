from django.core.cache import cache

FEED_CACHE_TIMEOUT = 300


def get_feed_cache_key(campus_id, category=None):
    """
    Generates an isolated, namespaced cache key per campus and channel category.
    Example: 'musubi:feed:campus_1:cat_ACADEMICS'
    """
    cat_str = category.upper() if category else "ALL"
    return f"musubi:feed:campus_{campus_id}:cat_{cat_str}"


def invalidate_campus_feed_cache(campus_id):
    """
    Purges all cached feed channels for a specific campus upon post creation,
    mutation, deletion, or upvote updates.
    """
    categories = ['ALL', 'ACADEMICS', 'EVENTS', 'LOST_FOUND', 'DISCUSSIONS', 'OPPORTUNITIES']
    keys_to_purge = [get_feed_cache_key(campus_id, cat) for cat in categories]
    cache.delete_many(keys_to_purge)
