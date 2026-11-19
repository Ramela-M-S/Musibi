from django.contrib import admin
from .models import Post, Upvote


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'campus', 'category', 'upvotes', 'created_at')
    list_filter = ('campus', 'category', 'created_at')
    search_fields = ('title', 'desc', 'user__username')
    ordering = ('-created_at',)


@admin.register(Upvote)
class UpvoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'post__title')
