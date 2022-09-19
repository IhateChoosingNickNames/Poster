import http.client

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


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

    def setUp(self):
        self.test_client = Client()
        self.authorized_client = Client

    def test_posts_correct_templates_used(self):
        """Проверка использования корректных шаблонов для всех страниц."""

        self.test_client.force_login(self.test_user_author)

        used_paths = {
            reverse("posts:index"): "posts/index.html",
            reverse(
                "posts:group_list", args=[self.test_group.slug]
            ): "posts/group_list.html",
            reverse(
                "posts:show_profile", args=[self.test_user_author.username]
            ): "posts/profile.html",
            reverse(
                "posts:show_post", args=[self.test_post.id]
            ): "posts/show_post.html",
            reverse("posts:post_create"): "posts/creation.html",
            reverse(
                "posts:post_edit", args=[self.test_post.id]
            ): "posts/creation.html",
        }

        for adress, template in used_paths.items():
            cache.clear()
            with self.subTest(adress=adress):
                response = self.test_client.get(adress)
                self.assertTemplateUsed(
                    response,
                    template,
                    (
                        f"Проверьте, что адресу {adress} "
                        f"соответствует шаблон {template}"
                    ),
                )

    def test_posts_index_grouplist_profile_showpost_exists_for_anonymous(self):
        """Проверка доступности главной страницы, страницы группы, страницы

        поста и страницы профиля автора для неавторизованного пользователя.
        """

        test_pages = [
            reverse("posts:index"),
            reverse("posts:group_list", args=[self.test_group.slug]),
            reverse(
                "posts:show_profile", args=[self.test_user_author.username]
            ),
            reverse("posts:show_post", args=[self.test_post.id]),
        ]

        for page in test_pages:
            with self.subTest(page=page):
                response = self.test_client.get(page)
                self.assertEqual(
                    response.status_code,
                    http.client.OK,
                    (
                        f"Проверьте, что страница {page} "
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
            reverse("posts:post_create"), follow=True
        )
        self.assertEqual(
            response.redirect_chain,
            [("/auth/login/?next=/create/", http.client.FOUND)],
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
            reverse("posts:post_edit", args=[self.test_post.id]), follow=True
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
            reverse("posts:post_edit", args=[self.test_post.id]), follow=True
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
            reverse("posts:post_edit", args=[self.test_post.id])
        )
        self.assertEqual(
            response.status_code,
            http.client.OK,
            "Проверьте, что автор может редактировать свой пост",
        )
