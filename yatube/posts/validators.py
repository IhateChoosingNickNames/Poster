from django import forms
from django.utils.translation import gettext_lazy as _

MIN_TEXT_LENGTH = 10
PROHIBITED_WORDS = []

def clean_text(data):

    if len(data) < MIN_TEXT_LENGTH:
        raise forms.ValidationError(
            _(
                "Длинна текста меньше допустимых "
                f"{MIN_TEXT_LENGTH} символов."
            )
        )

    for word in PROHIBITED_WORDS:
        if word in data.lower():
            raise forms.ValidationError(_("Не надо материться."))

    return data
