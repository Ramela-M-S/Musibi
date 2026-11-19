from django.test import TestCase
from django.contrib.auth.models import User
from register.models import Campus, UserProfile
from .models import Post, toggle_upvote_atomic


class PostModelTests(TestCase):
    def setUp(self):
        self.campus = Campus.objects.create(
            name="Panimalar Engineering College",
            code="PEC",
            passkey="PEC2026"
        )
        self.user = User.objects.create_user(
            username="author1",
            password="securepassword123"
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            campus=self.campus,
            department="CSE"
        )
        self.post = Post.objects.create(
            user=self.user,
            campus=self.campus,
            category="ACADEMICS",
            title="CS301 Distributed Systems Notes",
            desc="Comprehensive lecture summary for unit 1."
        )

    def test_post_creation_and_defaults(self):
        self.assertEqual(self.post.upvotes, 0)
        self.assertEqual(self.post.campus.code, "PEC")
        self.assertEqual(self.post.category, "ACADEMICS")

    def test_atomic_upvote_toggle(self):
        upvoted, count = toggle_upvote_atomic(self.user, self.post)
        self.assertTrue(upvoted)
        self.assertEqual(count, 1)

        # Toggle again should remove upvote
        upvoted_again, count_again = toggle_upvote_atomic(self.user, self.post)
        self.assertFalse(upvoted_again)
        self.assertEqual(count_again, 0)

