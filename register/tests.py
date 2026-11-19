from django.test import TestCase
from django.contrib.auth.models import User
from .models import Campus, UserProfile


class CampusModelTests(TestCase):
    def setUp(self):
        self.campus = Campus.objects.create(
            name="Panimalar Engineering College",
            code="PEC",
            passkey="PEC2026",
            location="Chennai"
        )
        self.user = User.objects.create_user(
            username="student1",
            password="securepassword123"
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            campus=self.campus,
            department="CSE",
            roll_number="CS2026001",
            batch_year=2026,
            role="STUDENT"
        )

    def test_campus_string_representation(self):
        self.assertEqual(str(self.campus), "Panimalar Engineering College (PEC)")

    def test_profile_linkage(self):
        self.assertEqual(self.user.profile.campus.code, "PEC")
        self.assertEqual(self.user.profile.department, "CSE")

