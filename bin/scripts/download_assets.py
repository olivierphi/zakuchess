#!/usr/bin/env python

from time import monotonic
from typing import TypeAlias
from pathlib import Path

# N.B. "urllib" is not part of our direct dependencies, but it's so ubiquitous that
# we can be pretty sure that one of our transitive dependencies depends on it ^_^
from urllib.request import urlretrieve


URL: TypeAlias = str

BASE_DIR = Path(__file__).parent.resolve() / ".." / ".."  # points to our git repo's root

FRONTEND_SRC = BASE_DIR / "frontend-src"
CHESS_STATIC = BASE_DIR / "src" / "apps" / "chess" / "static" / "chess"

ASSETS_MAP: dict[URL, Path] = {
    # fmt: off
    # Stockfish:
    "https://cdnjs.cloudflare.com/ajax/libs/stockfish.js/10.0.2/stockfish.min.js": CHESS_STATIC / "js" / "bot" / "stockfish.js",
    "https://cdnjs.cloudflare.com/ajax/libs/stockfish.js/10.0.2/stockfish.wasm": CHESS_STATIC / "js" / "bot" / "stockfish.wasm",
    "https://cdnjs.cloudflare.com/ajax/libs/stockfish.js/10.0.2/stockfish.wasm.min.js": CHESS_STATIC / "js" / "bot" / "stockfish.wasm.js",
    # Wesnoth assets:
    "https://github.com/wesnoth/wesnoth/raw/master/data/core/images/units/human-loyalists/bowman.png": CHESS_STATIC / "units" / "default" / "bowman.png",
    "https://github.com/wesnoth/wesnoth/raw/master/data/core/images/units/human-loyalists/fencer.png": CHESS_STATIC / "units" / "default" / "fencer.png",
    "https://github.com/wesnoth/wesnoth/raw/master/data/core/images/units/human-loyalists/general.png": CHESS_STATIC / "units" / "default" / "general.png",
    "https://github.com/wesnoth/wesnoth/raw/master/data/core/images/units/human-loyalists/horseman/horseman.png": CHESS_STATIC / "units" / "default" / "horseman.png",
    "https://github.com/wesnoth/wesnoth/raw/master/data/core/images/units/human-magi/red-mage+female.png": CHESS_STATIC / "units" / "default" / "red-mage+female.png",
    "https://github.com/wesnoth/wesnoth/raw/master/data/core/images/units/human-loyalists/shocktrooper.png": CHESS_STATIC / "units" / "default" / "shocktrooper.png",
    "https://github.com/wesnoth/wesnoth/raw/master/data/core/images/units/human-loyalists/swordsman.png": CHESS_STATIC / "units" / "default" / "swordsman.png",
    # fmt: on
}


def download_assets(*, even_if_exists: bool) -> None:
    # TODO: download this stuff in parallel, using asyncio or threads
    for asset_url, target_path in ASSETS_MAP.items():
        if not even_if_exists and target_path.exists():
            print(f"Skipping download of '{asset_url}', since '{target_path.relative_to(BASE_DIR)}' already exists.")
            continue
        target_folder = target_path.parent
        if not target_folder.exists():
            target_folder.mkdir(parents=True)
        print(f"Downloading '{asset_url}' to '{target_path.relative_to(BASE_DIR)}'...")
        dl_start_time = monotonic()
        urlretrieve(asset_url, target_path)
        print(f"Downloaded (took {round(monotonic() - dl_start_time, 1)}s.)")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download some assets that are not versioned (yet).")
    parser.add_argument(
        "--even-if-exists",
        action="store_true",
        default=False,
        help="re-download files that already exists on the local filesystem",
    )
    args = parser.parse_args()

    download_assets(even_if_exists=args.even_if_exists)
