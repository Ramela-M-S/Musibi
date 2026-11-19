from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import RegistrationForm


def register_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(
                request,
                f"Welcome to Musubi, {user.username}! Your campus profile is ready. Please log in."
            )
            return redirect("login")
    else:
        form = RegistrationForm()

    return render(request, "register/register.html", {"form": form})