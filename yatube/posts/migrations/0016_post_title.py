# Generated by Django 2.2.16 on 2022-09-15 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0015_auto_20220915_1840'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='title',
            field=models.CharField(default='Без заголовка', help_text='Введите Название поста (обязательное поле)', max_length=255, verbose_name='Название поста'),
            preserve_default=False,
        ),
    ]