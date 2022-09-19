from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()


class CreationForm(UserCreationForm):
    """Форма регистрации нового пользователя."""

    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput())
    password2 = forms.CharField(
        label="Подтверждение пароля", widget=forms.PasswordInput()
    )
    gender = forms.ChoiceField(
        label="Укажите пол",
        choices=[("м", "Мужской"), ("ж", "Женский")],
        required=False,
        help_text="По дефолту будешь мужиком",
    )
    email = forms.EmailField(label="Введите почту", required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
            "gender",
        )
