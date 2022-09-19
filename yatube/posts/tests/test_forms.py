import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Group, Post

User = get_user_model()

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

        cls.test_user = User.objects.create_user("test_user")

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()

        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.test_client = Client()

    def test_posts_form_post_create_fields(self):
        """Проверка полей в форме."""

        test_form = PostForm()
        required_fields = [
            "text",
            "group",
            'image'
        ]

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
        self.test_client.post(reverse("posts:post_create"), data=form_data)

        self.assertEqual(
            Post.objects.count(),
            initial_amount_of_posts + 1,
            "Убедитесь, что корректные данные создают пост",
        )

        # Вырезано из-за тестов ЯП.
        # now = datetime.datetime.today()

        self.assertTrue(
            Post.objects.filter(
                text="Тестовый текст",
                image="posts/small.gif",
                # Вырезано из-за тестов ЯП.
                # image=f"photos/posts/{now.year}/{now.month:02d}/"
                # f"{now.day:02d}/small.gif",
                group=self.test_group,
            ).exists(),
            (
                "Убедитесь, что сохраняется пост и картинка в правильной папке"
                "по пути photos/posts/%Y/%m/%d/"
            ),
        )

        last_post = Post.objects.last()

        self.assertEqual(
            last_post.author,
            self.test_user,
            "Пост создается не от нужного автора",
        )

        self.assertEqual(
            last_post.group,
            self.test_group,
            "У поста создается неверная группа",
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

        self.test_client.post(
            reverse("posts:post_edit", args=[test_post.id]),
            {
                # "title": test_post.title,
                "text": changed_text
            },
        )

        post = Post.objects.last()

        self.assertEqual(
            post.text,
            changed_text,
            "Проверьте, что при редактировании поста сохраняются " "изменения",
        )
