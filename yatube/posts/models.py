from django.core.validators import MaxValueValidator, MinValueValidator

from core.models import CreatedModel
from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

User = get_user_model()
TEXT_TRANCATECHARS = 30

class Group(models.Model):
    """Создание модели группы."""

    title = models.CharField(max_length=200, verbose_name="Название группы")
    slug = models.SlugField(
        max_length=50, unique=True, verbose_name="Slug для url"
    )
    description = models.TextField(verbose_name="Описание")

    class Meta:
        """Мета для вывода человекочитаемых имен и сортировки"""

        default_related_name = "group"
        verbose_name_plural = "Группы"
        verbose_name = "группа"

    def get_absolute_url(self):
        return reverse("posts:group_list", kwargs={"slug": self.slug})

    def __str__(self):
        """Переопределение вывода"""
        return self.title


class Post(CreatedModel):
    """Создание модели постов."""

    title = models.CharField(
        verbose_name="Название поста",
        help_text="Введите Название поста (обязательное поле)",
        max_length=255
    )
    image = models.ImageField(
        upload_to="photos/posts/%Y/%m/%d/",
        verbose_name="Изображение",
        blank=True,
        null=True,
        help_text="Выберите картинку (опционально)",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts",
        verbose_name="Автор",
        help_text="Укажите автора поста (обязательное поле)",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="posts",
        verbose_name="Группа",
        help_text="Выберите группу из списка (опционально)",
    )

    class Meta:
        """Мета для вывода человекочитаемых имен"""

        default_related_name = "post"
        ordering = ("-created", )
        verbose_name = "пост"
        verbose_name_plural = "Посты"

    def __str__(self):
        return self.text[:TEXT_TRANCATECHARS]

    def get_absolute_url(self):
        return reverse("posts:show_post", kwargs={"post_id": self.pk})


class Comment(CreatedModel):
    """Создание модели комментария."""

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Автор",
        help_text="Укажите автора комментария (обязательное поле)",
    )
    image = models.ImageField(
        upload_to="photos/comments/%Y/%m/%d/",
        verbose_name="Изображение",
        blank=True,
        null=True,
        help_text="Выберите файл (опционально)",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Комментарий к посту",
        help_text="Выберите пост из списка (обязательное поле)",
    )
    child = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="commentaries",
        verbose_name="Комментарий в треде",
        blank=True,
        null=True,
        help_text="Выберите комментарий из списка (опционально)",
    )
    is_child = models.BooleanField(default=False)

    class Meta:
        """Мета для вывода человекочитаемых имен и сортировки"""

        ordering = ("-created", )
        default_related_name = "commentary"
        verbose_name_plural = "Комментарии"
        verbose_name = "комментарий"

    def __str__(self):
        return self.text[:TEXT_TRANCATECHARS]


class Follow(models.Model):
    """Модель подписки на авторов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="follower",
        verbose_name="Пользователь",
        help_text="Укажите пользователя ленты",
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="following",
        verbose_name="Авторы",
        help_text="Укажите авторов для подписки",
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'following'),
                name='unique_follow'
            ),
        )


class Rating(models.Model):
    """Модель лайков/дизлайков на авторов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="liker",
        verbose_name="Пользователь",
        help_text="Пользователь, который ставит лайк/дизлайк",
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="Лайк поста",
        help_text="Пост, которому ставят лайк/дизлайк",
    )
    rating = models.IntegerField(
        verbose_name="Лайки",
        help_text="Укажите лайк или дизлайк",
        default=0,
        validators=[
            MinValueValidator(-1),
            MaxValueValidator(1)
        ]
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'post', 'rating'),
                name='unique_rating'
            ),
        )
