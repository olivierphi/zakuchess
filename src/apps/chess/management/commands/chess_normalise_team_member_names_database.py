import importlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

_FILE_PATH = (
    settings.BASE_DIR / "src" / "apps" / "chess" / "data" / "team_member_names.py"
)
_MODULE_PATH = "apps.chess.data.team_member_names"

_MODULE_TEMPLATE = """from typing import Final

FIRST_NAMES: Final = {FIRST_NAMES!r}

LAST_NAMES: Final = {LAST_NAMES!r}

"""


class Command(BaseCommand):
    help = (
        "Normalise the first and last names we use in "
        " 'apps/chess/domain/data/team_member_names.py'."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Don't actually update the file.",
        )
        parser.add_argument(
            "--check",
            action="store_true",
            help="Don't actually update the file, but exits with an error code "
            "if the file is not normalised.",
        )

    def handle(self, *args, check: bool, dry_run: bool, **options):
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

        if check:
            self._check(module_new_content)
            return

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
                f"Successfully normalised {len(first_names)} first names "
                f"and {len(last_names)} last names."
            )
        )

    def _check(self, module_new_content) -> None:
        # We have to write the module to a temporary file, because normalisation
        # includes Black (that doesn't seem to have a Python API to work on strings)
        # (this is very quick and dirty code it's 11pm - and I'm tired 😅)
        module_current_content = _FILE_PATH.read_text()

        fd, tmp_file_path = tempfile.mkstemp(
            prefix="zakuchess-team-members-normalisation-check", text=True
        )
        fp = os.fdopen(fd, "wt")
        fp.write(module_new_content)
        fp.close()

        subprocess.run(f"black '{tmp_file_path}'", shell=True, check=True)

        module_after_black_path = Path(tmp_file_path)
        module_new_content_after_black = module_after_black_path.read_text()
        module_after_black_path.unlink()

        if module_current_content != module_new_content_after_black:
            self.stdout.write(
                self.style.ERROR(
                    f"The file '{_FILE_PATH}' is not normalised. "
                    "Please run this command without the '--check' flag "
                    "to normalise it."
                )
            )
            print(module_current_content)
            print(module_new_content_after_black)
            sys.exit(1)

        self.stdout.write(self.style.SUCCESS("The file is normalised."))
