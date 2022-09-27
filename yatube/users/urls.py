from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeDoneView,
    PasswordResetCompleteView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
)
from django.urls import path

from . import views

app_name = "users"

urlpatterns = [
    path(
        "logout/",
        views.MyLogoutView.as_view(),
        name="logout",
    ),
    path("signup/", views.SignUp.as_view(), name="signup"),
    path(
        "login/",
        views.MyLoginView.as_view(),
        name="login",
    ),
    path(
        "password_change/done/",
        PasswordChangeDoneView.as_view(
            template_name="users/password_change_done.html"
        ),
        name="password_change_done",
    ),
    path(
        "password_change/",
        views.ChangePassword.as_view(),
        name="password_change_form",
    ),
    path(
        "password_reset/done/",
        PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password_reset/",
        views.ResetPasswordView.as_view(),
        name="password_reset_form",
    ),
    path(
        "reset/<uidb64>/<token>/",
        PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]
