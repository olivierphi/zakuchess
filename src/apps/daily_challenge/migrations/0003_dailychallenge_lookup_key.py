# Generated by Django 4.1.3 on 2023-09-19 17:51

from django.db import migrations, models


def _copy_id_to_lookup_key(apps, schema_editor):
    DailyChallenge = apps.get_model("daily_challenge", "DailyChallenge")
    DailyChallenge.objects.all().update(lookup_key=models.F("id"))


class Migration(migrations.Migration):

    dependencies = [
        ("daily_challenge", "0002_populate_fallback_game"),
    ]

    operations = [
        migrations.AddField(
            model_name="dailychallenge",
            name="lookup_key",
            field=models.CharField(max_length=20, null=True, unique=True),
        ),
        migrations.RunPython(
            _copy_id_to_lookup_key, reverse_code=migrations.RunPython.noop
        ),
        migrations.AlterField(
            model_name="dailychallenge",
            name="lookup_key",
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.RemoveField(
            model_name="dailychallenge",
            name="id",
            field=models.CharField(max_length=20, primary_key=True, serialize=False),
        ),
        migrations.AddField(
            model_name="dailychallenge",
            name="id",
            field=models.BigAutoField(
                auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
            ),
        ),
    ]
