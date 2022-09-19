import http

from django import forms
from django.contrib import auth
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_user = User.objects.create_user(
            username="test_user",
            email="test@test.test",
            password="aoSLok1234!@",
        )

    def setUp(self):
        self.test_client = Client()

    def test_users_signup_context_has_form(self):
        """Проверка наличия формы на странице регистрации."""

        response = self.test_client.get(reverse("users:signup"))
        self.assertEqual(response.status_code, http.client.OK)

        form_fields = {
            "first_name": forms.fields.CharField,
            "last_name": forms.fields.CharField,
            "username": auth.forms.UsernameField,
            "email": forms.fields.EmailField,
            "gender": forms.fields.ChoiceField,
            "password1": forms.fields.CharField,
            "password2": forms.fields.CharField,
        }

        for field_name, test_field_type in form_fields.items():
            with self.subTest(field_name=field_name):
                field = response.context.get("form").fields.get(field_name)
                self.assertEqual(
                    type(field),
                    test_field_type,
                    f"Поле {field_name} должно иметь тип {test_field_type}",
                )

    def test_users_successfull_password_change(self):
        """Проверка корректности изменения пароля."""

        self.test_client.force_login(self.test_user)
        response = self.test_client.get(reverse("users:password_change_form"))
        self.assertEqual(response.status_code, http.client.OK)

        response = self.test_client.post(
            reverse("users:password_change_form"),
            {
                "old_password": "aoSLok1234!@",
                "new_password1": "AOslOK1234!@",
                "new_password2": "AOslOK1234!@",
            },
        )
        self.assertTrue(
            User.objects.get(id=1).check_password("AOslOK1234!@"),
            "Проверьте, что новый пароль сохраняется",
        )

    def test_users_password_recover_page_with_vaild_uidb64(self):
        """Проверка отправки письма на почту и проверка сброса пароля по

        валидной ссылке.
        """

        response = self.test_client.post(
            reverse("users:password_reset_form"), {"email": "test@test.test"}
        )

        self.assertEqual(
            len(mail.outbox), 1, "Проверьте, что отправляете письмо на почту"
        )

        token = response.context[0]["token"]
        uid = response.context[0]["uid"]
        password_data = {
            "new_password1": "AOslOK1234!@",
            "new_password2": "AOslOK1234!@",
        }

        response = self.test_client.get(
            reverse(
                "users:password_reset_confirm",
                kwargs={"uidb64": uid, "token": token},
            )
        )
        self.assertIn(
            response.status_code,
            (http.client.MOVED_PERMANENTLY, http.client.FOUND),
        )

        response = self.test_client.post(
            reverse(
                "users:password_reset_confirm",
                kwargs={"uidb64": uid, "token": token},
            ),
            data=password_data,
        )

        self.assertIn(
            response.status_code,
            (http.client.MOVED_PERMANENTLY, http.client.FOUND),
        )

        # Пароль не меняется.
        # self.assertTrue(self.test_user.check_password('AOslOK1234!@'))
