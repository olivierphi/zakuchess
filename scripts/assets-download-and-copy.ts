import { Readable } from "node:stream"
import type { PipelinePromise, Writable } from "node:stream"
import { pipeline } from "node:stream/promises"
import { copyFile } from "node:fs/promises"
import pLimit from "p-limit"
import { sprintf } from "sprintf-js"
import Path from "@mojojs/path"

type URL = string

const STATIC_FOLDER = "./static"
const DOWNLOADS_CONCURRENCY = 3

const ASSETS_PATTERNS: Record<string, string> = {
  GOOGLE_FONTS: "https://fonts.gstatic.com/s/%(fontName)s/%(v)s/%(fileId)s.woff2",
  STOCKFISH_CDN: "https://cdnjs.cloudflare.com/ajax/libs/stockfish.js/10.0.2/%(file)s",
  WESNOTH_UNITS_GITHUB:
    "https://github.com/wesnoth/wesnoth/raw/master/data/core/images/units/%(path)s",
  WESNOTH_CAMPAIGN_UNITS_GITHUB:
    "https://github.com/wesnoth/wesnoth/raw/master/data/campaigns/%(campaign)s/images/units/%(path)s",
  // @link https://commons.wikimedia.org/wiki/Category:SVG_chess_pieces
  WIKIMEDIA_CHESS_SVG_LIGHT:
    "https://upload.wikimedia.org/wikipedia/commons/%(folder)s/Chess_%(piece)slt45.svg",
  WIKIMEDIA_CHESS_SVG_DARK:
    "https://upload.wikimedia.org/wikipedia/commons/%(folder)s/Chess_%(piece)sdt45.svg",
}

// prettier-ignore
const ASSETS_TO_DOWNLOAD_MAP: Record<URL, string> = Object.fromEntries([
  // Fonts:
  [sprintf(ASSETS_PATTERNS["GOOGLE_FONTS"], {fontName: "opensans",fileId: "mem8YaGs126MiZpBA-UFVZ0b",v: "v35"}), `${STATIC_FOLDER}/fonts/OpenSans.woff2`],
  // Stockfish:
  [sprintf(ASSETS_PATTERNS["STOCKFISH_CDN"], {file: "stockfish.min.js"}), `${STATIC_FOLDER}/js/bot/stockfish.js`],
  [sprintf(ASSETS_PATTERNS["STOCKFISH_CDN"], {file: "stockfish.wasm"}), `${STATIC_FOLDER}/js/bot/stockfish.wasm`],
  [sprintf(ASSETS_PATTERNS["STOCKFISH_CDN"], {file: "stockfish.wasm.min.js"}), `${STATIC_FOLDER}/js/bot/stockfish.wasm.js`],
  // Wesnoth assets:
  // "The good folks" units:
  [sprintf(ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"], {path:"human-loyalists/fencer.png"}), `${STATIC_FOLDER}/img/units/humans/pawn.png`],
  [sprintf(ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"], {path:"human-loyalists/horseman/horseman.png"}), `${STATIC_FOLDER}/img/units/humans/knight.png`],
  [sprintf(ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"], {path:"human-outlaws/ranger.png"}), `${STATIC_FOLDER}/img/units/humans/bishop.png`],
  [sprintf(ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"], {path:"dwarves/gryphon-rider.png"}), `${STATIC_FOLDER}/img/units/humans/rook.png`],
  [sprintf(ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"], {path:"human-magi/red-mage+female.png"}), `${STATIC_FOLDER}/img/units/humans/queen.png`],
  [sprintf(ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"], {path:"human-loyalists/shocktrooper.png"}), `${STATIC_FOLDER}/img/units/humans/king.png`],
  // "The bad folks" units:
  [sprintf(ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"], {path:"undead-skeletal/deathblade.png"}), `${STATIC_FOLDER}/img/units/undeads/pawn.png`],
  [sprintf(ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"], {path:"undead-skeletal/chocobone.png"}), `${STATIC_FOLDER}/img/units/undeads/knight.png`],
  [sprintf(ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"], {path:"undead-skeletal/banebow.png"}), `${STATIC_FOLDER}/img/units/undeads/bishop.png`],
  [sprintf(ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"], {path:"monsters/skeletal-dragon/skeletal-dragon.png"}), `${STATIC_FOLDER}/img/units/undeads/rook.png`],
  [sprintf(ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"], {path:"undead-necromancers/necromancer+female.png"}), `${STATIC_FOLDER}/img/units/undeads/queen.png`],
  [sprintf(ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"], {path:"undead-skeletal/draug.png"}), `${STATIC_FOLDER}/img/units/undeads/king.png`],
])

// prettier-ignore
const ASSETS_TO_COPY_MAP: Record<string, string> = Object.fromEntries([
  ["./static-src/fonts/fibberish.ttf", `${STATIC_FOLDER}/fonts/fibberish.ttf`],
])

async function downloadAssets() {
  const limitConcurrency = pLimit(DOWNLOADS_CONCURRENCY)

  const downloadPromises: PipelinePromise<Writable>[] = []
  for (const [url, pathString] of Object.entries(ASSETS_TO_DOWNLOAD_MAP)) {
    const downloadPromiseGenerator = async () => {
      console.log(`Downloading ${url} to ${pathString}`)
      const path = new Path(pathString)
      await path.dirname().mkdir({ recursive: true })
      const response: Response = await fetch(url)
      if (!response.body) {
        throw new Error(`Response body is empty for ${url}`)
      }
      // @ts-ignore
      const readableNodeStream = Readable.fromWeb(response.body) //TODO: fix types here
      const targetFileStream = path.createWriteStream({ encoding: "binary" })
      return pipeline(readableNodeStream, targetFileStream)
    }
    downloadPromises.push(limitConcurrency(downloadPromiseGenerator))
  }
  return Promise.all(downloadPromises)
}

async function copyAssets() {
  for (const [src, target] of Object.entries(ASSETS_TO_COPY_MAP)) {
    console.log(`Copying ${src} to ${target}`)
    await copyFile(src, target)
  }
}

downloadAssets()
  .then(() => console.log("Assets downloaded."))
  .then(() => copyAssets())
  .then(() => console.log("Assets copied."))
  .catch(console.error)
