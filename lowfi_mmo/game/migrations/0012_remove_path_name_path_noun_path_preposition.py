# Generated by Django 4.2.2 on 2023-07-29 14:01

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0011_alter_entity_appearance_alter_entity_description'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='path',
            name='name',
        ),
        migrations.AddField(
            model_name='path',
            name='noun',
            field=models.CharField(blank=True, max_length=20, validators=[django.core.validators.RegexValidator("^[a-zA-Z0-9\\s\\']*$", 'Only alphanumeric characters, spaces and single quotes are allowed.')]),
        ),
        migrations.AddField(
            model_name='path',
            name='preposition',
            field=models.CharField(blank=True, max_length=20, validators=[django.core.validators.RegexValidator("^[a-zA-Z0-9\\s\\']*$", 'Only alphanumeric characters, spaces and single quotes are allowed.')]),
        ),
    ]