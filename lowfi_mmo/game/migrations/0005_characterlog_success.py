# Generated by Django 4.2.2 on 2023-07-28 01:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0004_characterlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='characterlog',
            name='success',
            field=models.BooleanField(default=True),
        ),
    ]