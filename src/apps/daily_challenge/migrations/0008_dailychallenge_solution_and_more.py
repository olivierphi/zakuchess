# Generated by Django 5.0.2 on 2024-02-12 19:00

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("daily_challenge", "0007_alter_dailychallengestats_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="dailychallenge",
            name="solution",
            field=models.CharField(
                blank=True,
                help_text="A comma-separated list of UCI moves",
                max_length=150,
                validators=[
                    django.core.validators.RegexValidator(
                        r"^(?:[a-h][1-8][a-h][1-8],){1,}[a-h][1-8][a-h][1-8]$"
                    )
                ],
            ),
        ),
        migrations.AddField(
            model_name="dailychallenge",
            name="solution_turns_count",
            field=models.PositiveSmallIntegerField(editable=False, null=True),
        ),
    ]
