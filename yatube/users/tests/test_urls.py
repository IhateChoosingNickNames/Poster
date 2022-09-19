import http.client

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersURLTest(TestCase):
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

    def test_users_correct_templates_used(self):
        """Проверка всех страниц и соответствующих им шаблонов."""

        used_adresses = {
            reverse(
                "users:password_change_done"
            ): "users/password_change_done.html",
            reverse(
                "users:password_change_form"
            ): "users/password_change_form.html",
            reverse(
                "users:password_reset_done"
            ): "users/password_reset_done.html",
            reverse(
                "users:password_reset_form"
            ): "users/password_reset_form.html",
            reverse(
                "users:password_reset_complete"
            ): "users/password_reset_complete.html",
            reverse("users:logout"): "users/logged_out.html",
            reverse("users:signup"): "users/signup.html",
            reverse("users:login"): "users/login.html",
        }

        self.test_client.force_login(self.test_user)

        for adress, template in used_adresses.items():
            with self.subTest(adress=adress):
                response = self.test_client.get(adress)

                self.assertEqual(
                    response.status_code,
                    http.client.OK,
                    f"Проверьте корректность работы {adress}",
                )

                self.assertTemplateUsed(
                    response,
                    template,
                    (
                        f"Проверьте, что для {adress} вы "
                        f"используете шаблон {template}"
                    ),
                )

    def test_users_password_change_redirect_for_anonymous_user(self):
        """Проверка редиректа на страницу авторизации при попытке изменить

        пароль для неавторизованного пользователя
        """

        response = self.test_client.get(
            reverse("users:password_change_form"), follow=True
        )
        # print(reverse('posts:index'))
        self.assertEqual(
            response.redirect_chain,
            [("/auth/login/?next=/auth/password_change/", http.client.FOUND)],
            (
                "Проверьте, что перенаправляете "
                "незарегистрированного пользователя на страницу "
                "авторизации"
            ),
        )

    def test_users_password_recover_page_with_not_vaild_uidb64_link(self):
        """Проверка невалидной ссылки с почты."""

        response = self.test_client.get(
            reverse("users:password_reset_confirm", args=["test", "test"])
        )

        self.assertFalse(response.context_data["validlink"])
