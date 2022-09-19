from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post

User = get_user_model()

russian_alphabet_pattern = r"[а-яА-ЯёЁ()\-\.\!\?=' ]+"


class PostModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_user = User.objects.create_user("test_user")
        cls.test_group = Group.objects.create(
            title="Тестовая группа",
            slug="Тестовый слаг",
            description="Тестовое описание",
        )
        cls.test_post = Post.objects.create(
            text=(
                "Тестовый текст и еще несколько дополнительный символов, "
                "чтобы наверняка"
            ),
            author=cls.test_user,
        )

    def test_posts_post_model_str_return_text_and_correct_length(self):
        """Проверка того, что метод __str__ вернет поле text с длиной не

        более 15 символов.
        """

        required_length = 15
        test_post = PostModelTests.test_post

        self.assertIn(
            str(test_post),
            test_post.text,
            "Метод __str__ должен обращаться к полю text",
        )

        self.assertTrue(
            len(str(test_post)) <= required_length,
            "Метод __str__ должен возвращать строку не длиннее 15" " символов",
        )

    def test_posts_post_model_text_help_text_and_verbose_name_in_russian(self):
        """Проверка наличия verbose_name и help_text на русском языке."""

        fields = ["text", "image", "author", "group"]
        test_post = PostModelTests.test_post

        for field in fields:
            with self.subTest(field=field):
                test_verbose_text = test_post._meta.get_field(
                    field
                ).verbose_name

                self.assertRegex(
                    test_verbose_text,
                    russian_alphabet_pattern,
                    f"Добавьте параметр help_text на русском "
                    f"языке в поле {field}",
                )

                test_help_text_text = test_post._meta.get_field(
                    field
                ).help_text

                self.assertRegex(
                    test_help_text_text,
                    russian_alphabet_pattern,
                    f"Добавьте параметр help_text на русском "
                    f"языке в поле {field}",
                )

    def test_posts_post_model_fields_blank_value(self):
        """Проверка полей на обязательность к заполнению."""

        fields_true = ["image", "group", "created"]
        fields_false = ["text", "author"]

        test_post = PostModelTests.test_post
        for field in fields_true:
            with self.subTest(field=field):
                self.assertTrue(
                    test_post._meta.get_field(field).blank,
                    f"Поле {field} должно быть обязательным",
                )

        for field in fields_false:
            with self.subTest(field=field):
                self.assertFalse(
                    test_post._meta.get_field(field).blank,
                    f"Поле {field} должно быть опциональным",
                )

    def test_posts_post_model_has_absolute_url(self):
        """Проверка наличия get_absolute_url()."""

        test_post = PostModelTests.test_post
        try:
            test_post.get_absolute_url()
        except AttributeError:
            self.fail("Переопределите метод get_absolute_url()")


class GroupModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_group = Group.objects.create(
            title="test_group",
            slug="test_slug",
            description="test_description",
        )

    def test_posts_text_verbose_name_in_russian_not_blank(self):
        """Проверка наличия verbose_name на русском языке"""

        fields = ["title", "slug", "description"]

        for field in fields:
            with self.subTest(field=field):
                test_text = self.test_group._meta.get_field(field).verbose_name

                self.assertRegex(
                    test_text,
                    russian_alphabet_pattern,
                    f"Добавьте параметр help_text на русском "
                    f"языке в поле {field}",
                )

    def test_posts_group_fields_max_length(self):
        """Проверка наличия атрибута max_length для полей title и slug и

        проверка их длины.
        """
        fields_max_lengths = {"title": 200, "slug": 50}
        for field, test_max_length in fields_max_lengths.items():
            with self.subTest(max_length=test_max_length):
                self.assertEqual(
                    self.test_group._meta.get_field(field).max_length,
                    test_max_length,
                    f"max_length должно быть равно {test_max_length}",
                )

    def test_posts_group_model_str_return_title(self):
        """Проверка длины выводимого текста (должна быть не менее 15

        символов).
        """

        self.assertEqual(
            str(self.test_group),
            self.test_group.title,
            "Метод __str__ должен возвращать строку c title",
        )
