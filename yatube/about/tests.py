import http

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class StaticURLTest(TestCase):
    def setUp(self):
        self.test_client = Client()

    def test_about_tech_and_author_correct_working_and_correct_templates(self):
        """Проверка доступности адресов <Об авторе> и <О технологиях> и

        использования корректных шаблонов.
        """

        used_adresses = {
            reverse("about:tech"): "about/tech.html",
            reverse("about:author"): "about/author.html",
        }

        for adress, template in used_adresses.items():
            with self.subTest(adress=adress):
                response = self.test_client.get(adress)
                self.assertEqual(
                    response.status_code,
                    http.client.OK,
                    (
                        f"Проверьте работоспособность страницы "
                        f"{adress} для неавторизованного "
                        f"пользователя"
                    ),
                )
                self.assertTemplateUsed(
                    response,
                    template,
                    f"Проверьте, что для {adress} "
                    f"используется шаблон {template}",
                )
