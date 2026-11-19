from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.cache import cache
from .forms import PostForm
from .models import Post, toggle_upvote_atomic
from .utils import get_feed_cache_key, FEED_CACHE_TIMEOUT, invalidate_campus_feed_cache


@login_required
def menu_view(request):
    """
    Renders the student dashboard menu with profile summary and navigation links.
    """
    return render(request, "posts/menu.html")


@login_required
def create_view(request):
    """
    Handles new post creation, assigning the post to the authenticated student's campus.
    """
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            user_profile = getattr(request.user, 'profile', None)
            if user_profile:
                post.campus = user_profile.campus
            post.save()
            return redirect("all_posts")
    else:
        form = PostForm()
    return render(request, "posts/create_post.html", {"form": form})


@login_required
def all_posts(request):
    """
    Renders the campus feed with category channel filtering and read-through caching.
    Queries leverage compound B-Tree indexes and select_related to eliminate N+1 queries.
    """
    user_profile = getattr(request.user, 'profile', None)
    user_campus = user_profile.campus if user_profile else None
    selected_category = request.GET.get('category', '').upper()

    campus_id = user_campus.id if user_campus else 0
    cache_key = get_feed_cache_key(campus_id, selected_category)

    # Read-through cache lookup
    cached_posts = cache.get(cache_key)
    if cached_posts is not None:
        posts = cached_posts
    else:
        # Cache miss: query database with tenant filter, index ordering, and foreign key joins
        posts_query = Post.objects.filter(campus=user_campus)
        if selected_category and selected_category != 'ALL':
            posts_query = posts_query.filter(category=selected_category)

        posts = list(
            posts_query.select_related('user', 'user__profile', 'campus').order_by('-created_at')
        )
        cache.set(cache_key, posts, timeout=FEED_CACHE_TIMEOUT)

    categories = [
        ('ALL', 'All Channels', 'dynamic_feed'),
        ('ACADEMICS', 'Academics & Notes', 'menu_book'),
        ('EVENTS', 'Events & Workshops', 'event'),
        ('LOST_FOUND', 'Lost & Found', 'search'),
        ('DISCUSSIONS', 'Campus Life', 'forum'),
        ('OPPORTUNITIES', 'Internships', 'work'),
    ]

    return render(request, "posts/my_post.html", {
        "posts": posts,
        "page_title": f"{user_campus.name if user_campus else 'Campus'} Feed",
        "campus": user_campus,
        "categories": categories,
        "selected_category": selected_category or 'ALL',
        "is_all_posts": True,
        "empty_title": "No posts in this channel yet",
        "empty_desc": "Be the first from your campus to share notes, questions, or updates in this channel!",
        "empty_btn": "Create a Post",
    })


@login_required
def my_posts(request):
    """
    Displays posts authored specifically by the currently authenticated student.
    """
    posts = Post.objects.filter(user=request.user).select_related('campus', 'user__profile').order_by('-created_at')

    return render(request, "posts/my_post.html", {
        "posts": posts,
        "page_title": "My Campus Activity",
        "is_all_posts": False,
        "empty_title": "You haven't posted anything yet",
        "empty_desc": "Share lecture notes, club announcements, or campus questions with your peers.",
        "empty_btn": "Create Your First Post",
    })


@login_required
def upvote_post_view(request, post_id):
    """
    Toggles post upvote atomically using database-level F() expressions to prevent lost updates.
    Enforces cross-tenant authorization and triggers event-driven cache invalidation.
    """
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        user_campus = getattr(request.user.profile, 'campus', None)
        if post.campus != user_campus:
            return JsonResponse({"error": "Unauthorized cross-campus action"}, status=403)

        upvoted, total_upvotes = toggle_upvote_atomic(request.user, post)
        invalidate_campus_feed_cache(post.campus_id)

        return JsonResponse({"upvoted": upvoted, "total_upvotes": total_upvotes})
    return JsonResponse({"error": "POST required"}, status=400)
