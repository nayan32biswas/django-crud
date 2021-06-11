from django.urls import path

from allauth.account.views import LoginView, SignupView, LogoutView

from . import views

urlpatterns = [
    path('', views.user_profile, name='profile'),
    path('register/', SignupView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
]
