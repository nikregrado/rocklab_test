# Generated by Django 2.2 on 2019-08-01 10:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='is_student',
            new_name='is_blogger',
        ),
        migrations.RenameField(
            model_name='userprofile',
            old_name='is_teacher',
            new_name='is_reader',
        ),
    ]
