# Generated by Django 5.0.2 on 2024-03-23 16:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("daily_challenge", "0014_dailychallengestats_undos_count"),
    ]

    operations = [
        migrations.AddField(
            model_name="dailychallengestats",
            name="returning_players_count",
            field=models.IntegerField(
                default=0, help_text="Number of players who played on any previous day"
            ),
        ),
    ]
