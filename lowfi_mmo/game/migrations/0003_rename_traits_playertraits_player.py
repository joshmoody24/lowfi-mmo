# Generated by Django 4.2.2 on 2023-06-24 22:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_alter_npcprefab_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='playertraits',
            old_name='traits',
            new_name='player',
        ),
    ]