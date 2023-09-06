import importlib
import subprocess

from django.conf import settings
from django.core.management.base import BaseCommand

_FILE_PATH = (
    settings.BASE_DIR
    / "src"
    / "apps"
    / "chess"
    / "domain"
    / "data"
    / "team_member_names.py"
)
_MODULE_PATH = "apps.chess.domain.data.team_member_names"

_MODULE_TEMPLATE = """from typing import Final

FIRST_NAMES: Final = {FIRST_NAMES!r}

LAST_NAMES: Final = {LAST_NAMES!r}

"""


class Command(BaseCommand):
    help = "Normalise the first and last names we use in 'apps/chess/domain/data/team_member_names.py'."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Don't actually update the file.",
        )

    def handle(self, *args, dry_run: bool, **options):
        database = importlib.import_module(_MODULE_PATH)

        # We use sets to remove duplicates:
        first_names_set, last_names_set = set(database.FIRST_NAMES), set(
            database.LAST_NAMES
        )
        # ...And we then turn them into sorted tuples:
        first_names = tuple(sorted(first_names_set))
        last_names = tuple(sorted(last_names_set))

        module_new_content = _MODULE_TEMPLATE.format(
            FIRST_NAMES=first_names,
            LAST_NAMES=last_names,
        )

        if not dry_run:
            file_path = _FILE_PATH.resolve()
            self.stdout.write(f"Updating file '{file_path}'...")
            file_path.write_text(module_new_content)

            self.stdout.write("Formatting this file with Black...")
            subprocess.run(f"black '{file_path}'", shell=True, check=True)

            self.stdout.write("Adding it to git...")
            subprocess.run(f"git add '{file_path}'", shell=True, check=True)

            self.stdout.write("Done.")

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully normalised {len(first_names)} first names amd {len(last_names)} last names."
            )
        )
