# Generated by Django 2.2.16 on 2022-11-01 17:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0031_auto_20221005_1902'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'default_related_name': 'commentary', 'ordering': ('-created',), 'verbose_name': 'комментарий', 'verbose_name_plural': 'Комментарии'},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'default_related_name': 'post', 'ordering': ('-created',), 'verbose_name': 'пост', 'verbose_name_plural': 'Посты'},
        ),
    ]