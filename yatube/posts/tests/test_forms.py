import http.client
import os.path
import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_group = Group.objects.create(
            title="test_title",
            slug="test_slug",
            description="test_description",
        )

        cls.test_group_2 = Group.objects.create(
            title="test_title_2",
            slug="test_slug_2",
            description="test_description_2",
        )

        cls.test_user = User.objects.create_user("test_user")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.test_client = Client()

    def field_checker(self, check_data):

        for check_pair in check_data:
            with self.subTest(field=check_pair[0]):
                self.assertEqual(
                    check_pair[1],
                    check_pair[2],
                    ("Значение поля не соответствует ожидаемому"),
                )

    def test_posts_anonymous_cannot_post(self):
        """Проверка пост-запроса от неавторизованного пользователя."""

        initial_amount = Post.objects.count()

        post_data_without_author = {"text": "Тестовый текст"}

        post_data_with_author = {
            "text": "Тестовый текст",
            "author": self.test_user,
        }

        self.test_client.post(
            reverse("posts:post_create"), data=post_data_with_author
        )

        self.assertEqual(
            initial_amount,
            Post.objects.count(),
            (
                (
                    "Проверьте, что неавторизованный пользователь не может "
                    "создавать посты"
                )
            ),
        )

        self.test_client.post(
            reverse("posts:post_create"), data=post_data_without_author
        )

        self.assertEqual(
            initial_amount,
            Post.objects.count(),
            (
                (
                    "Проверьте, что неавторизованный пользователь не может "
                    "создавать посты"
                )
            ),
        )

    def test_posts_form_post_create_fields(self):
        """Проверка полей в форме."""

        test_form = PostForm()
        required_fields = ["text", "group", "image"]

        for field in required_fields:
            with self.subTest(field=field):
                self.assertIn(
                    field,
                    test_form.fields,
                    f"Проверьте, что добавили поле {field} в форму "
                    "создания поста",
                )

    def test_posts_form_post_create_valid_data(self):
        """Валидная форма создает пост с картинкой."""

        initial_amount_of_posts = Post.objects.count()

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

        form_data = {
            "title": "Тестовый заголовок",
            "text": "Тестовый текст",
            "image": uploaded,
            "group": self.test_group.id,
        }

        self.test_client.force_login(self.test_user)

        response = self.test_client.post(
            reverse("posts:post_create"), data=form_data, follow=True
        )

        self.assertEqual(
            Post.objects.count(),
            initial_amount_of_posts + 1,
            "Убедитесь, что корректные данные создают пост",
        )

        last_post = Post.objects.last()

        image_path = os.path.join(TEMP_MEDIA_ROOT, "posts", uploaded.name)

        with open(image_path, "rb") as file:
            saved_image = file.read()

        check_data = [
            ("image", saved_image, small_gif),
            ("author", last_post.author, self.test_user),
            ("group", last_post.group, self.test_group),
        ]

        self.field_checker(check_data)

        # Вырезано из-за тестов ЯП.
        # now = datetime.datetime.today()

        image_path = "posts/" + uploaded.name

        self.assertTrue(
            Post.objects.filter(
                text=form_data["text"],
                image=image_path,
                # Вырезано из-за тестов ЯП.
                # image=f"photos/posts/{now.year}/{now.month:02d}/"
                # f"{now.day:02d}/small.gif",
                group=self.test_group,
            ).exists(),
            (
                "Убедитесь, что сохраняется пост и картинка в правильной папке"
                # "по пути photos/posts/%Y/%m/%d/"
                "по пути /posts/"
            ),
        )

        redirect_chain = [
            reverse("posts:show_profile", args=[self.test_user]),
            http.client.FOUND,
        ]

        self.assertRedirects(
            response,
            *redirect_chain,
            msg_prefix=(
                "Проверьте, что перенаправляете пользователя на "
                "страницу своего профиля после создания поста"
            ),
        )

    def test_posts_form_post_create_not_valid_data(self):
        """Проверка несоздания поста с невалидными данными (наличие мата и

        длина менее 10 символов).
        """

        initial_amount_of_posts = Post.objects.count()

        invalid_data = [
            {"text": "менее10"},
            {"text": ""},
        ]

        self.test_client.force_login(self.test_user)

        for data in invalid_data:
            with self.subTest(data=data["text"]):

                self.test_client.post(reverse("posts:post_create"), data=data)

                self.assertEqual(
                    Post.objects.count(),
                    initial_amount_of_posts,
                    "Проверьте корректность работы валидатора.",
                )

    def test_posts_form_post_edit_valid_data(self):
        """Проверка редактирования поста."""

        test_post = Post.objects.create(
            # title="Тестовый заголовок",
            text="Тестовый пост",
            author=self.test_user,
            group=self.test_group,
        )

        self.test_client.force_login(self.test_user)

        changed_text = "Проверка редактирования поста"

        response = self.test_client.post(
            reverse("posts:post_edit", args=[test_post.id]),
            {
                # "title": test_post.title,
                "text": changed_text,
                "group": self.test_group_2.id,
            },
        )

        redirect_chain = [
            reverse("posts:show_post", args=[test_post.id]),
            http.client.FOUND,
        ]

        self.assertRedirects(
            response,
            *redirect_chain,
            msg_prefix=(
                "Проверьте, что перенаправляете пользователя на "
                "страницу своего поста после создания"
            ),
        )

        post = Post.objects.last()

        check_data = [
            ("text", post.text, changed_text),
            ("author", post.author, self.test_user),
            ("group", post.group, self.test_group_2),
        ]

        self.field_checker(check_data)
