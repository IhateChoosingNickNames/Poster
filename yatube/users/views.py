from django.contrib.auth import logout
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import CreationForm


class SignUp(CreateView):
    """Отображение страницы регистрации."""

    form_class = CreationForm
    success_url = reverse_lazy("users:login")
    template_name = "users/signup.html"

    def get(self, request, *args, **kwargs):
        logout(request)
        return super().get(request, *args, **kwargs)


class ChangePassword(PasswordChangeView):
    """Отображение страницы смены пароля."""

    form_class = PasswordChangeForm
    success_url = reverse_lazy("users:password_change_done")
    template_name = "users/password_change_form.html"


class ResetPasswordView(PasswordResetView):
    """Отображение страницы сброса пароля."""

    form_class = PasswordResetForm
    success_url = reverse_lazy("users:password_reset_done")
    template_name = "users/password_reset_form.html"
