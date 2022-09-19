import http

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from users.forms import CreationForm

User = get_user_model()


class UserCreateFormTests(TestCase):
    """Тесты на случай переопределения модельки юзеров."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_user = User.objects.create_user("test_user")

    def setUp(self):
        self.test_client = Client()

    def test_posts_form_post_create_fields(self):
        """Проверка полей в форме."""

        test_form = CreationForm()
        required_fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
            "gender",
        ]

        for field in required_fields:
            with self.subTest(field=field):
                self.assertIn(
                    field,
                    test_form.fields,
                    f"Проверьте, что добавили поле {field} в форму "
                    "создания поста",
                )

    def test_users_form_user_signup(self):
        """Валидная форма создает нового пользователя."""

        initial_amount_of_users = User.objects.count()

        form_data = {
            "first_name": "test_first_name",
            "last_name": "test_last_name",
            "username": "test_username",
            "email": "test@test.test",
            "password1": "aoSLok1234!@",
            "password2": "aoSLok1234!@",
        }
        self.test_client.post(reverse("users:signup"), data=form_data)
        self.assertEqual(
            User.objects.count(),
            initial_amount_of_users + 1,
            "Проверьте правильность работы регистрации " "пользователя",
        )

    def test_users_form_user_signup_no_rewrite_existing_user(self):
        """Проверка отсутсвия перезаписи существующего пользователя."""

        form_data = {
            "first_name": "test_first_name_rewrite",
            "last_name": "test_last_name",
            "username": self.test_user.username,
            "email": "test@test.test",
            "password1": "aoSLok1234!@",
            "password2": "aoSLok1234!@",
        }

        response = self.test_client.post(
            reverse("users:signup"), data=form_data
        )
        self.assertEqual(response.status_code, http.client.OK)

        self.assertFormError(
            response,
            "form",
            "username",
            "Пользователь с таким именем уже существует.",
        )
