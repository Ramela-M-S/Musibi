from django.shortcuts import render


def home_view(request):
    """
    Renders the platform public landing page.
    """
    return render(request, "feed/home.html")

