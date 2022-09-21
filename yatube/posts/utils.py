from django import forms
from django.utils.translation import gettext_lazy as _


class TemplateMixin:
    """Контейнер хранения шаблонов."""

    INDEX_TEMPLATE = "posts/index.html"
    GROUPS_TEMPLATE = "posts/group_list.html"
    GROUP_LIST_TEMPLATE = "posts/list_of_groups.html"
    SHOW_POST_TEMPLATE = "posts/show_post.html"
    ADD_POST_TEMPLATE = "posts/creation.html"
    POST_PROFILE_TEMPLATE = "posts/profile.html"
    FEEDBACK_TEMPLATE = "posts/feedback.html"


class PaginationMixin:
    """Миксин пагинации."""

    paginate_by = 10


class ValidationMixin:

    MIN_TEXT_LENGTH = 10
    PROHIBITED_WORDS = []

    def clean_text(self):
        data = self.cleaned_data["text"]
        if len(data) < self.MIN_TEXT_LENGTH:
            raise forms.ValidationError(
                _(
                    "Длинна текста меньше допустимых "
                    f"{self.MIN_TEXT_LENGTH} символов."
                )
            )

        for word in self.PROHIBITED_WORDS:
            if word in data.lower():
                raise forms.ValidationError(_("Не надо материться."))

        return data
