from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["title", "category", "desc", "post_image", "attachment"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g., CS301 Lecture Notes / Hackathon Team / Lost Item",
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "desc": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Provide details, context, notes summary, or discussion points...",
                    "rows": 4,
                }
            ),
            "post_image": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/*",
                }
            ),
            "attachment": forms.FileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".pdf,.doc,.docx,.txt",
                }
            ),
        }
        labels = {
            "title": "Post Title",
            "category": "Campus Channel",
            "desc": "Description / Notes Details",
            "post_image": "Optional Photo",
            "attachment": "Academic Document / PDF Attachment",
        }