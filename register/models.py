from django.db import models
from django.contrib.auth.models import User


class Campus(models.Model):
    name = models.CharField(max_length=150, unique=True)
    code = models.CharField(max_length=20, unique=True, help_text="e.g., NIT, IITM, BITS")
    passkey = models.CharField(max_length=50, help_text="Passcode required for students to join this campus")
    location = models.CharField(max_length=150, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Campuses"
        indexes = [
            models.Index(fields=['code'], name='campus_code_idx'),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"


class UserProfile(models.Model):
    DEPARTMENT_CHOICES = [
        ('CSBS', 'Computer Science And Business Systems'),
        ('AIDS', 'Artificial Intelligence And Data Science'),
        ('CSE', 'Computer Science & Engineering'),
        ('ECE', 'Electronics & Communication'),
        ('MECH', 'Mechanical Engineering'),
        ('CIVIL', 'Civil Engineering'),
        ('IT', 'Information Technology'),
        ('BIOTECH', 'Biotechnology'),
        ('MGMT', 'Management & Business'),
        ('OTHER', 'Other Sciences & Arts'),
    ]

    ROLE_CHOICES = [
        ('STUDENT', 'Student'),
        ('FACULTY', 'Faculty / Professor'),
        ('CLUB_LEAD', 'Club Lead / Organizer'),
        ('CAMPUS_ADMIN', 'Campus Administrator'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    campus = models.ForeignKey(Campus, on_delete=models.CASCADE, related_name='members')
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES, default='CSE')
    roll_number = models.CharField(max_length=30, blank=True)
    batch_year = models.PositiveIntegerField(default=2026, help_text="Graduation year")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT')
    bio = models.TextField(blank=True, max_length=300)

    class Meta:
        indexes = [
            models.Index(fields=['campus', 'department'], name='profile_campus_dept_idx'),
            models.Index(fields=['campus', 'roll_number'], name='profile_campus_roll_idx'),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.campus.code} ({self.department} '{str(self.batch_year)[-2:]})"