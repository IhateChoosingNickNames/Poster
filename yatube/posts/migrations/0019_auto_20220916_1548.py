# Generated by Django 2.2.16 on 2022-09-16 12:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0018_auto_20220916_1538'),
    ]

    operations = [
        migrations.RenameField(
            model_name='comment',
            old_name='commentary',
            new_name='post',
        ),
    ]