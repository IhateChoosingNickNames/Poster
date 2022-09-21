import http.client
import math
import shutil
import tempfile
from random import choice

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostsViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_group_1 = Group.objects.create(
            title="test_group_1", slug="test_slug_1", description="test_1"
        )
        cls.test_group_2 = Group.objects.create(
            title="test_group_2", slug="test_slug_2", description="test_2"
        )

        cls.test_user_1 = User.objects.create_user("test_user_1")
        cls.test_user_2 = User.objects.create_user("test_user_2")

        authors = [cls.test_user_1, cls.test_user_2]
        groups = [cls.test_group_1, cls.test_group_2, None]
        test_posts_amount = 15

        posts_fields = [
            Post(
                text=f"Тестовый пост {num}",
                author=choice(authors),
                group=choice(groups),
            )
            for num in range(test_posts_amount)
        ]

        Post.objects.bulk_create(posts_fields)

    def setUp(self):
        self.test_client = Client()
        cache.clear()

    def test_posts_index_has_correct_context(self):
        """Проверка передачи корректного котекста на главную страницу."""

        response = self.test_client.get(reverse("posts:index"))

        # context_object_name = "posts"
        latest_post = Post.objects.first()
        first_index_post = response.context.get("posts")[0]

        self.assertEqual(
            latest_post,
            first_index_post,
            (
                "Проверьте, что передаете посты на главную страницу"
                "в отсортированном по дате добавления порядке"
            ),
        )

    def test_posts_group_list_has_correct_context(self):
        """Проверка передачи корректного котекста на страницу группы."""

        test_groups = [self.test_group_1, self.test_group_2]

        for test_group in test_groups:
            response = self.test_client.get(
                reverse("posts:group_list", args=[test_group.slug])
            )
            self.assertEqual(
                response.status_code,
                http.client.OK,
                ("Проверьте, что создается страница группы " "по slug"),
            )

            group_posts = response.context.get("posts")
            test_group_posts = Post.objects.filter(group=test_group)

            for post, test_post in zip(group_posts, test_group_posts):
                with self.subTest(post=post):
                    self.assertEqual(
                        post.group,
                        test_group,
                        ("Проверьте, что фильтруете посты по " "группе"),
                    )
                    self.assertEqual(
                        post,
                        test_post,
                        (
                            "Проверьте, что выводите посты в "
                            "правильном порядке"
                        ),
                    )

    def test_posts_profile_has_correct_context(self):
        """Проверка передачи корректного котекста на страницу профиля юзера."""

        test_users = [self.test_user_1, self.test_user_2]
        paginate_by = 10

        for test_user in test_users:
            response = self.test_client.get(
                reverse("posts:show_profile", args=[(test_user.username)])
            )
            self.assertEqual(
                response.status_code,
                http.client.OK,
                ("Проверьте, что создается страница профиля " "по username"),
            )

            # CBV на DetailView + MultipleObjectMixin, поэтому такая проверка
            profile_posts = response.context["object_list"]
            test_profile_posts = Post.objects.filter(author=test_user)[
                :paginate_by
            ]

            for post, test_post in zip(profile_posts, test_profile_posts):
                with self.subTest(post=post):
                    self.assertEqual(
                        post.author,
                        test_user,
                        ("Проверьте, что фильтруете посты по " "юзеру"),
                    )
                    self.assertEqual(
                        post,
                        test_post,
                        (
                            "Проверьте, что выводите посты в "
                            "правильном порядке"
                        ),
                    )

    def test_posts_post_detail_has_correct_context(self):
        """Проверка передачи корректного котекста на страницу поста."""

        posts = Post.objects.all()

        test_posts_amount = 3
        test_posts = [choice(posts) for _ in range(test_posts_amount)]

        for test_post in test_posts:

            response = self.test_client.get(
                reverse("posts:show_post", args=[test_post.id])
            )
            self.assertEqual(
                response.status_code,
                http.client.OK,
                "Проверьте, что создаете страницу поста по id",
            )

            self.assertEqual(
                response.context["object"],
                test_post,
                "Проверьте, что выводите правильный пост",
            )

    def test_posts_post_create_has_correct_context(self):
        """Проверка передачи корректного котекста на страницу создания

        поста.
        """

        self.test_client.force_login(self.test_user_1)
        response = self.test_client.get(reverse("posts:post_create"))
        self.assertEqual(
            response.status_code,
            http.client.OK,
            ("Проверьте правильность работы страницы создания " "поста"),
        )

        form_fields = {
            "group": forms.models.ModelChoiceField,
            "text": forms.fields.CharField,
            "image": forms.fields.ImageField,
        }

        for field_name, test_field_type in form_fields.items():
            with self.subTest(field_name=field_name):
                field = response.context.get("form").fields.get(field_name)
                self.assertEqual(
                    type(field),
                    test_field_type,
                    (
                        f"Поле {field_name} должно иметь тип"
                        f"{test_field_type}"
                    ),
                )

    def test_posts_post_edit_has_correct_context(self):
        """Проверка передачи корректного котекста на страницу редактирования

        поста.
        """

        self.test_client.force_login(self.test_user_2)

        # Защита от рандома из фикстур
        tmp = Post.objects.filter(author=self.test_user_2)
        if not tmp:
            tmp = Post.objects.filter(author=self.test_user_1)

        test_post = tmp[0]

        response = self.test_client.get(
            reverse("posts:post_edit", args=[test_post.id])
        )

        self.assertEqual(
            response.status_code,
            http.client.OK,
            (
                "Проверьте правильность работы страницы "
                "редактирования поста для автора"
            ),
        )

        self.assertIn("post", response.context)

        self.assertEqual(
            response.context["post"],
            test_post,
            (
                "Проверьте, что передаете правильный объект на "
                "страницу редактирования поста"
            ),
        )

        self.assertIn(
            "is_edit",
            response.context,
            "Проверьте, что передаете is_edit в контексте",
        )

        self.assertEqual(
            response.context["is_edit"],
            True,
            "Проверьте, что передаете is_edit == True",
        )

    def test_posts_new_created_posts_exists_in_index_grouplist_profile(self):
        """Проверка публикации нового поста после создания на главной странице,

        на странице группы, на странице профиля юзера и не публикации на

        странице другой группы.
        """

        self.test_client.force_login(self.test_user_1)

        post_data = {
            "title": "Тестовый заголовок",
            "text": "Проверка добавления поста на все страницы",
            "author": self.test_user_1,
            "group": self.test_group_1.id,
        }

        response = self.test_client.post(
            reverse("posts:post_create"), data=post_data
        )

        self.assertIn(
            response.status_code,
            [http.client.FOUND, http.client.MOVED_PERMANENTLY],
            (
                "Проверьте, что вы перенаправляете пользователя после "
                "создания поста"
            ),
        )

        pages = {
            "index": reverse("posts:index"),
            "group": reverse(
                "posts:group_list", args=[self.test_group_1.slug]
            ),
            "profile": reverse("posts:show_profile", args=[self.test_user_1]),
        }

        for name, page in pages.items():
            cache.clear()
            with self.subTest(page=page):
                response = self.test_client.get(page)
                post = response.context.get("object_list")[0]

                self.assertEqual(
                    post.text,
                    post_data["text"],
                    "Убедитесь, что новый пост добавляется на "
                    f"страницу {name}",
                )

        response = self.test_client.get(
            reverse("posts:group_list", args=[self.test_group_2.slug])
        )

        self.assertNotEqual(
            response.context.get("object_list")[0],
            post_data["text"],
            "Убедитесь, что пост публикуется только в своей группе",
        )


class PostsPaginationTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_paginator_user = User.objects.create_user(
            "test_paginator_user"
        )
        cls.test_group = Group.objects.create(
            title="test_group", slug="test_slug", description="test"
        )
        cls.test_cases = 15

        posts_fields = [
            Post(
                text=f"Тестовый пост {str(_)}",
                author=cls.test_paginator_user,
                group=cls.test_group,
            )
            for _ in range(cls.test_cases)
        ]

        Post.objects.bulk_create(posts_fields)

    def setUp(self):
        self.test_client = Client()

    def test_posts_index_grouplist_profile_has_paginator(self):
        """Проверка корректности работы пагинатора на главной странице,

        странице группы и странице профиля.
        """

        paginate_by = 10
        page_count = math.ceil(self.test_cases / paginate_by)

        used_adresses = {
            "index": reverse("posts:index"),
            "group": reverse("posts:group_list", args=[self.test_group.slug]),
            "profile": reverse(
                "posts:show_profile", args=[self.test_paginator_user.username]
            ),
        }

        for name, adress in used_adresses.items():
            cache.clear()
            with self.subTest(adress=adress):

                response = self.test_client.get(adress)

                self.assertTrue(
                    response.context.get("is_paginated"),
                    f"Проверьте, что добавили пагинатор на "
                    f"страницу {name}",
                )

                self.assertEqual(
                    len(response.context.get("object_list")),
                    paginate_by,
                    f"Проверьте, что передаете ровно по "
                    f"{paginate_by} постов на страницу {name}",
                )

                self.assertEqual(
                    response.context.get("paginator").num_pages,
                    page_count,
                    "Убедитесь, что у вас корректное количество " "страниц",
                )


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class SprintSixTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_user_1 = User.objects.create_user("test_user_1")

        cls.test_user_2 = User.objects.create_user("test_user_2")

        cls.test_group = Group.objects.create(
            title="test_group", slug="test_slug", description="test"
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.test_client = Client()

    def test_posts_index_grouplist_profile_showpost_has_image(self):
        """Проверка наличия картинки в контексте поста на главной странице,

        на странице группы, на странице профиля, на странице поста.
        """

        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )

        uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )

        test_post = Post.objects.create(
            author=self.test_user_1,
            # Вырезано из-за тестов ЯП.
            # title="Тестовый заголовок",
            text="Тестовый текст",
            image=uploaded,
            group=self.test_group,
        )

        pages = {
            "index": reverse("posts:index"),
            "group": reverse("posts:group_list", args=[self.test_group.slug]),
            "profile": reverse("posts:show_profile", args=[self.test_user_1]),
        }

        for name, page in pages.items():
            cache.clear()
            with self.subTest(page=page):
                response = self.test_client.get(page)
                post = response.context.get("object_list")[0]
                self.assertTrue(
                    post.image,
                    (
                        f"Убедитесь, что на странице {page} в последнем "
                        "созданном посте есть картинка"
                    ),
                )
                self.assertEqual(
                    post.image,
                    test_post.image,
                    (
                        f"Убедитесь, что на странице {page} в последнем "
                        "созданном посте корректная картинка"
                    ),
                )

        response = self.test_client.get(
            reverse("posts:show_post", args=[test_post.id])
        )
        post = response.context.get("object")
        self.assertTrue(
            post.image,
            (
                "Убедитесь, что на странице show_post в последнем созданном "
                "посте есть картинка"
            ),
        )
        self.assertEqual(
            post.image,
            test_post.image,
            (
                "Убедитесь, что на странице show_post в последнем созданном "
                "посте корректная картинка"
            ),
        )

    def test_posts_post_edit_with_image(self):
        """Проверка добавления картинки при редактировании поста."""

        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )

        uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )

        post = Post.objects.create(
            text="Тестовый текст без картинки",
            author=self.test_user_1,
            image=uploaded,
        )

        form_data = {
            "text": "Тестовый текст с картинкой",
        }

        self.test_client.force_login(self.test_user_1)
        self.test_client.post(
            reverse("posts:post_edit", args=[post.id]), data=form_data
        )

        changed_post = Post.objects.get(id=post.id)

        self.assertEqual(
            changed_post.text,
            form_data["text"],
            "Убедитесь, что редактирования поста работает",
        )
        self.assertTrue(
            changed_post.image,
            "Убедитесь, что картинка добавляется при редактировании поста",
        )

    def test_posts_comments_correctly_working(self):
        """Проверка появления комментария на странице поста. Запрет на

        комментирование для неавторизованного.
        """

        test_post = Post.objects.create(
            # title="Тестовый заголовок",
            author=self.test_user_1,
            text="Тестовый пост",
        )

        test_comment = Comment.objects.create(
            author=self.test_user_2,
            text="Тестовый комментарий",
            post=test_post,
        )

        test_comment_to_post = {
            "author": self.test_user_1.id,
            "text": "Тестовый комментарий 2",
            "post": test_post.id,
        }
        initital_amount_of_comments = Comment.objects.count()
        response = self.test_client.get(
            reverse("posts:show_post", args=[test_post.id])
        )

        self.assertTrue(
            response.context.get("object_list"),
            "Проверьте, что у вас появился комментарий у нужного поста",
        )
        self.assertEqual(response.context.get("object_list")[0], test_comment)

        self.test_client.post(
            reverse("posts:post_comment", args=[test_post.id]),
            data=test_comment_to_post,
        )

        self.assertEqual(
            Comment.objects.count(),
            initital_amount_of_comments,
            (
                "Проверьте, что неавторизованный пользователь не может "
                "комментировать"
            ),
        )

        self.test_client.force_login(self.test_user_1)

        self.test_client.post(
            reverse("posts:post_comment", args=[test_post.id]),
            data=test_comment_to_post,
        )
        self.assertEqual(
            Comment.objects.count(),
            initital_amount_of_comments + 1,
            "Проверьте, что авторизованный пользователь может комментировать",
        )


class FollowViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_user_with_posts_sub = User.objects.create_user("test_user_1")

        cls.test_user_with_posts_not_sub = User.objects.create_user(
            "test_user_2"
        )

        cls.test_user_without_posts_not_sub = User.objects.create_user(
            "test_user_3"
        )

        cls.test_cases = 3

        users = [
            cls.test_user_with_posts_sub,
            cls.test_user_with_posts_not_sub,
        ]

        for user in users:
            posts_fields = [
                Post(
                    text=f"Тестовый пост {str(num)} от {user.username}",
                    author=user,
                )
                for num in range(cls.test_cases)
            ]

            Post.objects.bulk_create(posts_fields)

    def setUp(self):
        self.test_client = Client()
        self.test_client_not_sub = Client()

    def test_posts_follow_correctly_working(self):
        """Неавторизованный не может подписаться.

        Автор не может подписаться сам на себя.

        Авторизованный пользователь может подписываться.
        """

        initial_amount_follows = Follow.objects.count()

        self.test_client.get(
            reverse(
                "posts:profile_follow", args=[self.test_user_with_posts_sub]
            )
        )
        current_amount_follows = Follow.objects.count()

        self.assertEqual(
            initial_amount_follows,
            current_amount_follows,
            (
                "Убедитесь, что неавторизованный пользователь не может "
                "подписываться на авторов"
            ),
        )

        self.test_client.force_login(self.test_user_with_posts_sub)
        self.test_client.get(
            reverse(
                "posts:profile_follow", args=[self.test_user_with_posts_sub]
            )
        )
        current_amount_follows = Follow.objects.count()

        self.assertEqual(
            initial_amount_follows,
            current_amount_follows,
            "Убедитесь, что автор не может подписываться сам на себя",
        )

        self.test_client.get(
            reverse(
                "posts:profile_follow",
                args=[self.test_user_with_posts_not_sub],
            )
        )
        current_amount_follows = Follow.objects.count()

        self.assertNotEqual(
            initial_amount_follows,
            current_amount_follows,
            (
                "Убедитесь, что авторизованный пользователь может "
                "подписываться на авторов"
            ),
        )

    def test_posts_follow_subscriber_has_correct_feed(self):
        """У подписчика корректные посты в ленте.

        У неподписчика в ленте нет постов от автора.
        """

        posts = Post.objects.filter(author=self.test_user_with_posts_not_sub)

        self.test_client.force_login(self.test_user_with_posts_sub)
        self.test_client_not_sub.force_login(
            self.test_user_without_posts_not_sub
        )

        self.test_client.get(
            reverse(
                "posts:profile_follow",
                args=[self.test_user_with_posts_not_sub],
            )
        )

        response_sub = self.test_client.get(reverse("posts:show_follows"))
        response_not_sub = self.test_client_not_sub.get(
            reverse("posts:show_follows")
        )

        self.assertEqual(
            response_sub.status_code,
            http.HTTPStatus.OK,
            "Убедитесь, что страница /follow/ работает корректно",
        )
        self.assertEqual(
            response_not_sub.status_code,
            http.HTTPStatus.OK,
            "Убедитесь, что страница /follow/ работает корректно",
        )

        for post in posts:
            with self.subTest(post=post):
                self.assertIn(
                    post,
                    response_sub.context["object_list"],
                    (
                        "Убедитесь, что в ленте отображаются все посты автора,"
                        " на которого подписан пользователь"
                    ),
                )
                self.assertNotIn(
                    post,
                    response_not_sub.context["object_list"],
                    (
                        "Убедитесь, что в ленте отображаются все посты автора,"
                        " на которого подписан пользователь"
                    ),
                )


class NewClass(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_user = User.objects.create_user("test_user")
        cls.test_group = Group.objects.create(
            title="test_group", slug="test_slug", description="test"
        )

    def setUp(self):
        self.test_client = Client()
        cache.clear()

    def test_posts_index_grouplist_profile_cache_check(self):
        """Проверка кэша на главной странице, странице группы и на странице

        профиля.
        """

        Post.objects.create(
            text="Тестовый пост",
            author=self.test_user,
            group=self.test_group,
        )

        cache_timer_seconds = 20

        response = self.test_client.get(reverse("posts:index"))
        initial_content = response.content

        Post.objects.get(id=1).delete()

        response = self.test_client.get(reverse("posts:index"))
        self.assertEqual(
            response.content,
            initial_content,
            "Проверьте, что добавили кэширование на главную страницу",
        )

        cache.clear()

        response = self.test_client.get(reverse("posts:index"))
        self.assertNotEqual(
            response.content,
            initial_content,
            "Кэширование работает некорректно",
        )

        cache_control = response.get("cache-control", None)
        cache_control_time = int(cache_control.split("=")[1])

        self.assertEqual(
            cache_control_time,
            cache_timer_seconds,
            (
                "Проверьте, что задали таймер обновления кэша в "
                f"{cache_timer_seconds} секунд"
            ),
        )
