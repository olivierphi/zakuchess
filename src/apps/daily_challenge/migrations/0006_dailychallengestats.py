# Generated by Django 5.0.1 on 2024-01-29 21:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        (
            "daily_challenge",
            "0005_dailychallenge_created_at_dailychallenge_source_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="DailyChallengeStats",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("day", models.DateField(unique=True)),
                (
                    "created_count",
                    models.IntegerField(default=0, help_text="Number of games created"),
                ),
                (
                    "played_count",
                    models.IntegerField(
                        default=0,
                        help_text="Number of games where the player played at least 1 move",
                    ),
                ),
                ("turns_count", models.IntegerField(default=0)),
                ("restarts_count", models.IntegerField(default=0)),
                ("wins_count", models.IntegerField(default=0)),
                (
                    "challenge",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="daily_challenge.dailychallenge",
                    ),
                ),
            ],
        ),
    ]
