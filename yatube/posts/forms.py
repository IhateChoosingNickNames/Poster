from email.mime.image import MIMEImage

from captcha.fields import CaptchaField
from django import forms
from django.core.mail import EmailMessage
from django.utils.translation import gettext_lazy as _

from .models import Comment, Post
from .utils import ValidationMixin
from .validators import clean_text


class PostForm(forms.ModelForm, ValidationMixin):
    """Форма добавления нового поста и редактирования существующего."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["group"].empty_label = _("Группа не выбрана")

    class Meta:
        model = Post
        # Вырезано из-за тестов ЯП.
        # fields = ("title", "group", "text", "image")
        fields = ("group", "text", "image")
        widgets = {"text": forms.Textarea(attrs={"cols": 60, "rows": 10})}
        labels = {
            "title": _("Название поста"),
            "text": _("Текст поста"),
            "group": _("Добавить в группу"),
            "image": _("Изображение"),
        }

        help_texts = {
            "title": _("Укажите название поста (обязательное поле)"),
            "group": _("Выберите группу из списка (опционально)"),
            "text": _(
                "Введите текст поста (обязательное поле). Минимальная "
                f"длина текста - {ValidationMixin.MIN_TEXT_LENGTH} символов"
            ),
            "image": _("Загрузите фото (опционально)"),
        }


class CommentForm(forms.ModelForm, ValidationMixin):
    """Форма добавления нового поста и редактирования существующего."""

    class Meta:
        model = Comment
        # Вырезано из-за тестов ЯП.
        # fields = ("text", "image")
        fields = ("text",)
        labels = {"text": _("Текст комментария"), "image": _("Изображение")}
        help_texts = {
            "text": _(
                "Введите текст поста (обязательное поле). Минимальная "
                f"длина текста - {ValidationMixin.MIN_TEXT_LENGTH} символов"
            ),
            "image": _("Загрузите фото (опционально)"),
        }


class FeedbackForm(forms.Form):
    """Форма обратной связи."""

    name = forms.CharField(
        label=_("Имя"), help_text=_("Укажите ваше имя"), max_length=255
    )

    email = forms.EmailField(
        label=_("Почта"), help_text=_("Введите вашу почту для связи с вами")
    )

    description = forms.CharField(
        label=_("Описание"),
        help_text=_("Кратко опишите вашу проблему"),
        max_length=255,
    )

    message = forms.CharField(
        label=_("Текст сообщения"),
        help_text=_("Опишите суть вашего обращения"),
        widget=forms.Textarea(attrs={"cols": 60, "rows": 10}),
        validators=[clean_text],
    )

    image = forms.ImageField(
        label=_("Файл"),
        help_text=_("Прикрепите скриншот (опционально)"),
        required=False,
    )

    captcha = CaptchaField(
        label=_("Капча"),
        help_text=_("Докажите, что вы не робот - введите текст с картинки"),
    )

    def save(self):

        image = self.cleaned_data.get("image", None)
        name = self.cleaned_data["name"]
        msg = self.cleaned_data["message"]
        from_email = self.cleaned_data["email"]
        subject = self.cleaned_data["description"]

        body = f"""Обращение от {name}.
        Текст обращения: {msg}
        """

        message = EmailMessage(
            subject,
            body,
            from_email,
            [
                "yatubesupport@yandex.com",
            ],
        )

        message.content_subtype = "html"
        if image:
            mime_image = MIMEImage(image.read())
            mime_image.add_header("Content-ID", "<image>")
            message.attach(mime_image)

        message.send()
