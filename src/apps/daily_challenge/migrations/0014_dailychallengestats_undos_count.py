# Generated by Django 5.0.2 on 2024-03-20 22:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "daily_challenge",
            "0013_rename_played_count_dailychallengestats_attempts_count",
        ),
    ]

    operations = [
        migrations.AddField(
            model_name="dailychallengestats",
            name="undos_count",
            field=models.IntegerField(default=0),
        ),
    ]
