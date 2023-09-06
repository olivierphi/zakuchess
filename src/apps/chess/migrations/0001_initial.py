# Generated by Django 4.1.3 on 2023-08-28 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []  # type: ignore

    operations = [
        migrations.CreateModel(
            name="DailyChallenge",
            fields=[
                (
                    "id",
                    models.CharField(max_length=20, primary_key=True, serialize=False),
                ),
                ("fen", models.CharField(max_length=90)),
                (
                    "fen_before_bot_first_move",
                    models.CharField(editable=False, max_length=90),
                ),
                ("piece_role_by_square", models.JSONField(editable=False)),
                ("teams", models.JSONField(editable=False)),
                ("bot_first_move", models.CharField(max_length=5)),
            ],
        ),
    ]
