# Generated by Django 5.0.2 on 2024-02-15 21:07

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("daily_challenge", "0009_set_fallback_game_solution"),
    ]

    operations = [
        migrations.AddField(
            model_name="dailychallengestats",
            name="see_solution_count",
            field=models.IntegerField(default=0),
        ),
    ]
