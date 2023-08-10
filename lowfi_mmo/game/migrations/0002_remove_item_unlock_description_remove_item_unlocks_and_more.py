# Generated by Django 4.2.2 on 2023-08-10 00:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='item',
            name='unlock_description',
        ),
        migrations.RemoveField(
            model_name='item',
            name='unlocks',
        ),
        migrations.AddField(
            model_name='block',
            name='unlock_description',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='block',
            name='unlocked_by',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='game.item'),
            preserve_default=False,
        ),
    ]
