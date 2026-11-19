from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Campus, UserProfile


class RegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'student@example.com'})
    )
    campus = forms.ModelChoiceField(
        queryset=Campus.objects.all(),
        empty_label="-- Select Your College / Campus --",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    campus_passkey = forms.CharField(
        label="Campus Access Code",
        help_text="Enter the security code for your campus (e.g., PEC2026, NIT2026, IITM2026)",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'e.g., PEC2026'})
    )
    department = forms.ChoiceField(
        choices=UserProfile.DEPARTMENT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    batch_year = forms.IntegerField(
        initial=2026,
        label="Graduation Year",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2026'})
    )
    roll_number = forms.CharField(
        required=False,
        label="Student Roll / Registration No.",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CS2026042'})
    )

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "campus",
            "campus_passkey",
            "department",
            "batch_year",
            "roll_number",
            "password1",
            "password2",
        ]

    def clean(self):
        cleaned_data = super().clean()
        campus = cleaned_data.get('campus')
        passkey = cleaned_data.get('campus_passkey')

        # Enforce institutional access-code validation
        if campus and passkey:
            if passkey.strip() != campus.passkey.strip():
                self.add_error(
                    'campus_passkey',
                    f"Invalid access code for {campus.name}. Please contact your campus coordinator."
                )
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            campus = self.cleaned_data.get('campus')
            department = self.cleaned_data.get('department')
            batch_year = self.cleaned_data.get('batch_year', 2026)
            roll_number = self.cleaned_data.get('roll_number', '')

            UserProfile.objects.create(
                user=user,
                campus=campus,
                department=department,
                batch_year=batch_year,
                roll_number=roll_number,
                role='STUDENT',
            )
        return user