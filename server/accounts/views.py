from django.contrib.auth import (
    get_user_model,
    logout,
)
from django.shortcuts import render, redirect
from django.http import Http404


User = get_user_model()


def user_profile(request):
    if not request.user.is_authenticated:
        # If unauthenticated user raise error
        raise Http404
    user_data = request.user
    context = {
        "user_data": user_data,
    }
    return render(request, "pages/profile.html", context)


def logout_view(request):
    logout(request)
    return redirect("/")
