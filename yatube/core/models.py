from django.db import models


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания."""

    created = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата публикации", db_index=True
    )

    text = models.TextField(
        verbose_name="Текстовое поле",
        help_text="Введите текст (обязательное поле)",
    )

    class Meta:
        abstract = True
