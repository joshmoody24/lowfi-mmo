# Generated by Django 4.2.2 on 2023-06-26 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='appearance',
            field=models.TextField(blank=True),
        ),
    ]
