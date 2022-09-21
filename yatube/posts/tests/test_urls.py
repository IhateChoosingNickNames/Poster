import http.client

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, User


class PostsURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_group = Group.objects.create(
            title="test_title_1",
            slug="test_slug_1",
            description="Test descripition 1",
        )

        cls.test_user_author = User.objects.create_user("test_user_author")

        cls.test_user_not_author = User.objects.create_user(
            "test_user_not_author"
        )

        cls.test_post = Post.objects.create(
            text=(
                "Тестовый текст и еще несколько дополнительный символов, "
                "чтобы наверняка"
            ),
            author=cls.test_user_author,
        )

        cls.correct_page_data = {
            "index": {
                "namespace:name": "posts:index",
                "args": "",
                "url": "/",
                "template": "posts/index.html",
            },
            "group_list": {
                "namespace:name": "posts:group_list",
                "args": [cls.test_group.slug],
                "url": f"/group/{cls.test_group.slug}/",
                "template": "posts/group_list.html",
            },
            "show_profile": {
                "namespace:name": "posts:show_profile",
                "args": [cls.test_user_author.username],
                "url": f"/profile/{cls.test_user_author.username}/",
                "template": "posts/profile.html",
            },
            "show_post": {
                "namespace:name": "posts:show_post",
                "args": [cls.test_post.id],
                "url": f"/posts/{cls.test_post.id}/",
                "template": "posts/show_post.html",
            },
            "post_create": {
                "namespace:name": "posts:post_create",
                "args": "",
                "url": "/create/",
                "template": "posts/creation.html",
            },
            "post_edit": {
                "namespace:name": "posts:post_edit",
                "args": [cls.test_post.id],
                "url": f"/posts/{cls.test_post.id}/edit/",
                "template": "posts/creation.html",
            },
        }

    def setUp(self):
        self.test_client = Client()
        self.authorized_client = Client

    def test_posts_reverses_names_namespaces_have_correct_urls(self):
        """Проверка соответствия reverse(namespace:name) нужным урлам."""

        for adress_name in self.correct_page_data:
            cache.clear()
            page = self.correct_page_data[adress_name]
            with self.subTest(adress=adress_name):
                self.assertEqual(
                    reverse(page["namespace:name"], args=page["args"]),
                    page["url"],
                    ("Проверьте, что верно указали namespace и name для "
                     f"{page['url']}"),
                )

    def test_posts_correct_templates_used(self):
        """Проверка использования корректных шаблонов для всех страниц."""

        self.test_client.force_login(self.test_user_author)

        for adress_name in self.correct_page_data:
            cache.clear()
            page = self.correct_page_data[adress_name]

            with self.subTest(adress=adress_name):
                response = self.test_client.get(page["url"])
                self.assertTemplateUsed(
                    response,
                    page["template"],
                    (
                        f"Проверьте, что адресу {page['url']} "
                        f"соответствует шаблон {page['template']}"
                    ),
                )

    def test_posts_index_grouplist_profile_showpost_exists_for_anonymous(self):
        """Проверка доступности главной страницы, страницы группы, страницы

        поста и страницы профиля автора для неавторизованного пользователя.
        """

        test_pages = [
            self.correct_page_data['index'],
            self.correct_page_data['group_list'],
            self.correct_page_data['show_profile'],
            self.correct_page_data['show_post'],
        ]

        for page in test_pages:

            with self.subTest(page=page):
                response = self.test_client.get(page['url'])
                self.assertEqual(
                    response.status_code,
                    http.client.OK,
                    (
                        f"Проверьте, что страница {page['url']} "
                        f"доступна для неавторизованного "
                        f"пользователя"
                    ),
                )

    def test_posts_get_404_when_page_not_exists(self):
        """Проверка получения ошибки 404 при попытке перехода на

        несуществующую страницу.
        """

        self.test_client.force_login(self.test_user_author)
        response = self.test_client.get("/some_test_page/")
        self.assertEqual(response.status_code, http.client.NOT_FOUND)

        response = self.test_client.get("/some_test_page/")

        self.assertTemplateUsed(
            response,
            "core/404.html",
            "Убедитесь, что используется кастомный шаблон для страницы 404",
        )

    def test_posts_create_post_redirect_to_login_page_for_anonymous_user(self):
        """Проверка перенаправления на страницу авторизациии при попытке

        создать пост для неавторизованного пользователя.
        """

        response = self.test_client.get(
            self.correct_page_data['post_create']['url'], follow=True
        )

        redirect = (
            reverse("users:login") + "?next=" + reverse("posts:post_create")
        )

        self.assertEqual(
            response.redirect_chain,
            [(redirect, http.client.FOUND)],
            (
                "Проверьте, что перенаправляете "
                "незарегистрированного пользователя на страницу"
                "авторизации"
            ),
        )

    def test_posts_post_edit_redirect_to_show_post_for_anonymous_user(self):
        """Проверка редиректа при попытке редактирования поста для

        неавторизованного пользователя.
        """

        response = self.test_client.get(
            self.correct_page_data['post_edit']['url'], follow=True
        )
        self.assertEqual(
            response.redirect_chain,
            [(f"/posts/{self.test_post.id}/", http.client.FOUND)],
            (
                "Проверьте, что перенаправляете "
                "незарегистрированного пользователя на страницу"
                "авторизации"
            ),
        )

    def test_posts_post_edit_redirect_to_show_post_for_not_author(self):
        """Проверка редиректа при попытке редактирования поста для

        не автора поста.
        """

        self.test_client.force_login(self.test_user_not_author)

        response = self.test_client.get(
            self.correct_page_data['post_edit']['url'], follow=True
        )

        self.assertEqual(
            response.redirect_chain,
            [(f"/posts/{self.test_post.id}/", http.client.FOUND)],
            (
                "Проверьте, что перенаправляете "
                "незарегистрированного пользователя на страницу"
                "авторизации"
            ),
        )

    def test_posts_post_edit_correctly_working_for_author(self):
        """Проверка возможности редактирования поста автором."""

        self.test_client.force_login(self.test_user_author)
        response = self.test_client.get(
            self.correct_page_data['post_edit']['url']
        )
        self.assertEqual(
            response.status_code,
            http.client.OK,
            "Проверьте, что автор может редактировать свой пост",
        )
