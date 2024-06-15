import csv
import re
from pathlib import Path

import chess
from django.core.management import BaseCommand
from django.db.models.functions import Substr

from apps.daily_challenge.models import DailyChallenge

THEMES_TO_IGNORE = {
    "oneMove",
    "mateIn1",
    "mateIn2",
}


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "csv_file_path",
            type=existing_path,
            help="input CSV file, as downloaded from 'https://database.lichess.org/lichess_db_puzzle.csv.zst'.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=10,  # low batch size to avoid OOM on low-end Fly.io plan
            help="DailyChallenges creation batch size.",
        )
        parser.add_argument(
            "--min-popularity",
            type=int,
            default=90,
            help="Only consider puzzles that have at least that Popularity.",
        )
        parser.add_argument(
            "--rating-range",
            type=rating_range,
            dest="rating_min_max",
            default=(900, 1100),
            help="Only consider puzzles that have a Rating in this 'min-max' range.",
        )
        parser.add_argument(
            "--stop-after",
            type=int,
            help="Stop after having created N DailyChallenges.",
        )

    def handle(
        self,
        *args,
        csv_file_path: Path,
        batch_size: int,
        min_popularity: int,
        rating_min_max: tuple[int, int],
        stop_after: int | None,
        **options,
    ):
        rating_min, rating_max = rating_min_max
        already_imported_ids = set(
            DailyChallenge.objects.filter(source__startswith="lichess-").values_list(
                Substr("source", 9), flat=True
            )
        )
        print(f"already_imported_ids: {already_imported_ids}")

        created_count = 0
        current_batch: list[DailyChallenge] = []
        with csv_file_path.open(newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                themes: set[str] = set(row.get("Themes", "").split())
                if themes & THEMES_TO_IGNORE:
                    self.stdout.write("Skipping too short puzzle")
                    continue
                if (popularity := int(row["Popularity"])) < min_popularity:
                    self.stdout.write(f"Skipping puzzle with Popularity {popularity}")
                    continue
                if (rating := int(row["Rating"])) < rating_min or rating > rating_max:
                    self.stdout.write(f"Skipping puzzle with Rating {rating}")
                    continue

                puzzle_id = row["PuzzleId"]
                if puzzle_id in already_imported_ids:
                    self.stdout.write(f"Skipping already imported puzzle '{puzzle_id}'")
                    continue
                fen = row["FEN"]

                self.stdout.write(
                    f"Creating DailyChallenge for puzzle '{puzzle_id}' with Popularity {popularity}, rating {rating}, FEN '{fen}'"
                )

                if " b " in fen:  # quick and dirty way to detect if black is to move
                    self.stdout.write("Mirroring puzzle with black to move")
                    fen = chess.Board(fen).mirror().fen()

                current_batch.append(
                    DailyChallenge(
                        source=f"lichess-{puzzle_id}",
                        fen=fen,
                    )
                )

                if len(current_batch) == batch_size:
                    DailyChallenge.objects.bulk_create(current_batch)
                    self.stdout.write(f"Created {batch_size} puzzles.")
                    current_batch = []

                created_count += 1
                if stop_after is not None and created_count == stop_after:
                    self.stdout.write(f"Stopping after {created_count} puzzles.")
                    break

        if current_batch:
            DailyChallenge.objects.bulk_create(current_batch)
            self.stdout.write(f"Created {len(current_batch)} puzzles.")


def existing_path(value: str) -> Path:
    path = Path(value)
    if not path.exists():
        raise ValueError(f"Path does not exist: {path}")
    return path


def rating_range(value: str) -> tuple[int, int]:
    match = re.match(r"^(\d+)-(\d+)$", value)
    if not match:
        raise ValueError(
            f"Invalid rating range: {value} - should be '[int]-[int]' e.g. 800-1300"
        )
    return int(match[1]), int(match[2])
