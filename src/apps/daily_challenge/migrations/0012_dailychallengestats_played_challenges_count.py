# Generated by Django 5.0.2 on 2024-03-16 17:02

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("daily_challenge", "0011_dailychallenge_bot_depth_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="dailychallengestats",
            name="played_challenges_count",
            field=models.IntegerField(
                default=0,
                help_text="Number of times where the player played at least 2 moves on their 1st attempt of the day",
            ),
        ),
    ]
