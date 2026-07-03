"""
Accounts app urls.
"""
from django.urls import path

from .views import (UserRegistrationView, UserLoginView, UserProfileView, UserChangePasswordView,
                    SentResetPasswordEmailView, UserPasswordResetView,
                    LogoutUserView)

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name="register"),
    path('login/', UserLoginView.as_view(), name="login"),
    path('profile/', UserProfileView.as_view(), name="profile"),
    path('changepassword/', UserChangePasswordView.as_view(), name='changepassword'),
    path('reset-password/', SentResetPasswordEmailView.as_view(), name='reset-password'),
    path('reset-password/<uid>/<token>/', UserPasswordResetView.as_view(), name='user-reset-password'),
    path('logout/', LogoutUserView.as_view(), name="logout"),
]
