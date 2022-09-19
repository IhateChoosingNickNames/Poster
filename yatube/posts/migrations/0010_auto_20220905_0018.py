# Generated by Django 2.2.6 on 2022-09-04 21:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_auto_20220904_1920'),
    ]

    operations = [
        migrations.AddField(
            model_name='commentary',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='photos/comments/%Y/%m/%d/', verbose_name='Изображение'),
        ),
        migrations.AddField(
            model_name='post',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='photos/posts/%Y/%m/%d/', verbose_name='Изображение'),
        ),
    ]
