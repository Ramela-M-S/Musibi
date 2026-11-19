from django.db import models
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import F
from .validators import validate_academic_attachment, validate_image_upload


class Post(models.Model):
    CATEGORY_CHOICES = [
        ('ACADEMICS', 'Academics & Notes'),
        ('EVENTS', 'Events & Workshops'),
        ('LOST_FOUND', 'Lost & Found'),
        ('DISCUSSIONS', 'Campus Life & Discussions'),
        ('OPPORTUNITIES', 'Internships & Projects'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    campus = models.ForeignKey('register.Campus', on_delete=models.CASCADE, related_name="posts", default=1)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='DISCUSSIONS')
    title = models.CharField(max_length=200)
    desc = models.TextField(blank=True)
    post_image = models.ImageField(
    upload_to='post_pics/',
    blank=True,
    null=True,
    validators=[validate_image_upload]
)
    attachment = models.FileField(
    upload_to='campus_docs/',
    blank=True,
    null=True,
    help_text="PDF/DOC notes attachment",
    validators=[validate_academic_attachment]
    )
    upvotes = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['campus', 'category', '-created_at'], name='post_cmp_cat_created_idx'),
            models.Index(fields=['campus', '-created_at'], name='post_cmp_created_idx'),
            models.Index(fields=['user', '-created_at'], name='post_usr_created_idx'),
        ]

    @property
    def image_url(self):
        if not self.post_image:
            return ""
        try:
            return self.post_image.url
        except Exception:
            val = str(self.post_image)
            if val.startswith("http://") or val.startswith("https://"):
                return val
            if val.startswith("/media/"):
                return val
            return f"/media/{val.lstrip('/')}"

    @property
    def attachment_url(self):
        if not self.attachment:
            return ""
        try:
            return self.attachment.url
        except Exception:
            val = str(self.attachment)
            if val.startswith("http://") or val.startswith("https://"):
                return val
            return f"/media/{val.lstrip('/')}"

    @property
    def is_document(self):
        if self.attachment:
            name = str(self.attachment).lower()
            return name.endswith('.pdf') or name.endswith('.doc') or name.endswith('.docx')
        return False

    def __str__(self):
        return f"[{self.campus.code}][{self.category}] {self.title} by @{self.user.username}"


class Upvote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="upvotes")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_upvotes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')
        indexes = [
            models.Index(fields=['user', 'post'], name='upvote_usr_post_idx'),
        ]

    def __str__(self):
        return f"@{self.user.username} upvoted Post {self.post_id}"


def toggle_upvote_atomic(user, post):
    """
    Toggles an upvote atomically within an ACID transaction.
    Executes an atomic F() expression update on the database to prevent lost updates under concurrency.
    """
    with transaction.atomic():
        post = Post.objects.select_for_update().get(id=post.id)
        upvote, created = Upvote.objects.get_or_create(
            user=user,
            post=post
        )

        if created:
            Post.objects.filter(id=post.id).update(
                upvotes=F('upvotes') + 1
            )
            post.refresh_from_db(fields=['upvotes'])
            return True, post.upvotes
        else:
            upvote.delete()
            Post.objects.filter(id=post.id).update(
                upvotes=F('upvotes') - 1
            )
            post.refresh_from_db(fields=['upvotes'])
            return False, post.upvotes
