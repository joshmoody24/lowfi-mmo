# Generated by Django 4.2.2 on 2023-07-29 14:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0012_remove_path_name_path_noun_path_preposition'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='path',
            unique_together={('start', 'preposition', 'noun'), ('start', 'end')},
        ),
    ]