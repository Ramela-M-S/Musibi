from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Post
from .utils import invalidate_campus_feed_cache


@receiver(post_save, sender=Post)
def on_post_saved(sender, instance, created, **kwargs):
    """
    Invalidates cached campus feeds when a post is created or updated.
    """
    if instance.campus_id:
        invalidate_campus_feed_cache(instance.campus_id)


@receiver(post_delete, sender=Post)
def on_post_deleted(sender, instance, **kwargs):
    """
    Invalidates cached campus feeds when a post is deleted.
    """
    if instance.campus_id:
        invalidate_campus_feed_cache(instance.campus_id)
