from django.contrib.auth import (
    # authenticate,
    get_user_model,
    # login,
    logout,
)
from django.shortcuts import render, redirect
from django.http import Http404

# from django.utils import timezone
# from django.views.generic import DetailView
# from .forms import UserLoginForm, UserRegisterForm, UserProfileForm
# from posts.models import Post

User = get_user_model()


def user_profile(request):
    if not request.user.is_authenticated:
        raise Http404
    user_data = request.user
    # draft = Post.objects.filter(user=user_data.id, draft=True)
    # publish = Post.objects.filter(user=user_data.id, draft=False)
    context = {
        "user_data": user_data,
        # "draft": draft,
        # "publish": publish,
    }
    return render(request, "pages/profile.html", context)


def logout_view(request):
    logout(request)
    return redirect("/")
