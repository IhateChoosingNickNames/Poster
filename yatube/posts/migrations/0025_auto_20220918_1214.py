# Generated by Django 2.2.16 on 2022-09-18 09:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0024_remove_post_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, help_text='Выберите картинку (опционально)', null=True, upload_to='posts/', verbose_name='Изображение'),
        ),
    ]