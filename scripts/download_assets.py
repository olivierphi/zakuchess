#!/usr/bin/env python

from time import monotonic
from typing import TypeAlias
from pathlib import Path

# N.B. "urllib" is not part of our direct dependencies, but it's so ubiquitous that
# we can be pretty sure that one of our transitive dependencies depends on it ^_^
from urllib.request import urlretrieve


URL: TypeAlias = str

BASE_DIR = Path(__file__).parent.resolve() / ".."  # points to our git repo's root

FRONTEND_SRC = BASE_DIR / "frontend-src"
WEBUI_STATIC = BASE_DIR / "src" / "apps" / "webui" / "static" / "webui"
CHESS_STATIC = BASE_DIR / "src" / "apps" / "chess" / "static" / "chess"

ASSETS_PATTERNS: dict[str, str] = {
    "GOOGLE_FONTS": "https://fonts.gstatic.com/s/{font_name}/{v}/{file_id}.woff2",
    "STOCKFISH_CDN": "https://cdnjs.cloudflare.com/ajax/libs/stockfish.js/10.0.2/{file}",
    "WESNOTH_UNITS_GITHUB": "https://github.com/wesnoth/wesnoth/raw/master/data/core/images/units/{path}",
    "WESNOTH_CAMPAIGN_UNITS_GITHUB": "https://github.com/wesnoth/wesnoth/raw/master/data/campaigns/{campaign}/images/units/{path}",
    # @link https://commons.wikimedia.org/wiki/Category:SVG_chess_pieces
    "WIKIMEDIA_CHESS_SVG_LIGHT": "https://upload.wikimedia.org/wikipedia/commons/{folder}/Chess_{piece}lt45.svg",
    "WIKIMEDIA_CHESS_SVG_DARK": "https://upload.wikimedia.org/wikipedia/commons/{folder}/Chess_{piece}dt45.svg",
}

ASSETS_MAP: dict[URL, Path] = {
    # fmt: off
    # Fonts:
    ASSETS_PATTERNS["GOOGLE_FONTS"].format(font_name="opensans", file_id="mem8YaGs126MiZpBA-UFVZ0b", v="v35"): WEBUI_STATIC / "fonts" / "OpenSans.woff2",
    # Stockfish:
    ASSETS_PATTERNS["STOCKFISH_CDN"].format(file="stockfish.min.js"): CHESS_STATIC / "js" / "bot" / "stockfish.js",
    ASSETS_PATTERNS["STOCKFISH_CDN"].format(file="stockfish.wasm"): CHESS_STATIC / "js" / "bot" / "stockfish.wasm",
    ASSETS_PATTERNS["STOCKFISH_CDN"].format(file="stockfish.wasm.min.js"): CHESS_STATIC / "js" / "bot" / "stockfish.wasm.js",
    # Wesnoth assets:
    # "The good folks" units:
    ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"].format(path="human-loyalists/fencer.png"): CHESS_STATIC / "units" / "humans" / "pawn.png",
    ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"].format(path="human-loyalists/horseman/horseman.png"): CHESS_STATIC / "units" / "humans" / "knight.png",
    ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"].format(path="human-outlaws/ranger.png"): CHESS_STATIC / "units" / "humans" / "bishop.png",
    ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"].format(path="human-loyalists/shocktrooper.png"): CHESS_STATIC / "units" / "humans" / "rook.png",
    ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"].format(path="human-magi/red-mage+female.png"): CHESS_STATIC / "units" / "humans" / "queen.png",
    ASSETS_PATTERNS["WESNOTH_CAMPAIGN_UNITS_GITHUB"].format(campaign="Heir_To_The_Throne", path="konrad-lord-scepter-leading.png"): CHESS_STATIC / "units" / "humans" / "king.png",
    # "The bad folks" units:
    ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"].format(path="undead-skeletal/deathblade.png"): CHESS_STATIC / "units" / "undeads" / "pawn.png",
    ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"].format(path="undead-skeletal/chocobone.png"): CHESS_STATIC / "units" / "undeads" / "knight.png",
    ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"].format(path="undead-skeletal/banebow.png"): CHESS_STATIC / "units" / "undeads" / "bishop.png",
    ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"].format(path="undead-skeletal/draug.png"): CHESS_STATIC / "units" / "undeads" / "rook.png",
    ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"].format(path="undead-necromancers/necromancer+female.png"): CHESS_STATIC / "units" / "undeads" / "queen.png",
    ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"].format(path="undead-necromancers/ancient-lich-melee-2.png"): CHESS_STATIC / "units" / "undeads" / "king.png",
    # Chess pieces symbols:
    ## white pieces:
    ASSETS_PATTERNS["WIKIMEDIA_CHESS_SVG_LIGHT"].format(folder="4/45", piece="p"): CHESS_STATIC / "symbols" / "w-pawn.svg",
    ASSETS_PATTERNS["WIKIMEDIA_CHESS_SVG_LIGHT"].format(folder="7/70", piece="n"): CHESS_STATIC / "symbols" / "w-knight.svg",
    ASSETS_PATTERNS["WIKIMEDIA_CHESS_SVG_LIGHT"].format(folder="b/b1", piece="b"): CHESS_STATIC / "symbols" / "w-bishop.svg",
    ASSETS_PATTERNS["WIKIMEDIA_CHESS_SVG_LIGHT"].format(folder="7/72", piece="r"): CHESS_STATIC / "symbols" / "w-rook.svg",
    ASSETS_PATTERNS["WIKIMEDIA_CHESS_SVG_LIGHT"].format(folder="1/15", piece="q"): CHESS_STATIC / "symbols" / "w-queen.svg",
    ASSETS_PATTERNS["WIKIMEDIA_CHESS_SVG_LIGHT"].format(folder="4/42", piece="k"): CHESS_STATIC / "symbols" / "w-king.svg",
    ## black pieces:
    ASSETS_PATTERNS["WIKIMEDIA_CHESS_SVG_DARK"].format(folder="c/c7", piece="p"): CHESS_STATIC / "symbols" / "b-pawn.svg",
    ASSETS_PATTERNS["WIKIMEDIA_CHESS_SVG_DARK"].format(folder="e/ef", piece="n"): CHESS_STATIC / "symbols" / "b-knight.svg",
    ASSETS_PATTERNS["WIKIMEDIA_CHESS_SVG_DARK"].format(folder="9/98", piece="b"): CHESS_STATIC / "symbols" / "b-bishop.svg",
    ASSETS_PATTERNS["WIKIMEDIA_CHESS_SVG_DARK"].format(folder="f/ff", piece="r"): CHESS_STATIC / "symbols" / "b-rook.svg",
    ASSETS_PATTERNS["WIKIMEDIA_CHESS_SVG_DARK"].format(folder="4/47", piece="q"): CHESS_STATIC / "symbols" / "b-queen.svg",
    ASSETS_PATTERNS["WIKIMEDIA_CHESS_SVG_DARK"].format(folder="f/f0", piece="k"): CHESS_STATIC / "symbols" / "b-king.svg",
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
        print(f"Downloaded (took {monotonic() - dl_start_time:.1f}s.)")


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
