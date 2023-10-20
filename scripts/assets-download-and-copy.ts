import { copyFile } from "node:fs/promises"
import { argv } from "node:process"
import { Readable } from "node:stream"
import type { PipelinePromise, Writable } from "node:stream"
import { pipeline } from "node:stream/promises"
import Path from "@mojojs/path"
import pLimit from "p-limit"
import { sprintf } from "sprintf-js"

const downloadEvenIfExists = argv.includes("--download-even-if-exists")

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

// @link https://meta.wikimedia.org/wiki/User-Agent_policy
// Without this User-Agent we can get "HTTP 429 Too Many Requests" errors from Wikimedia servers.
const USER_AGENT = [
  "AssetsDownloaderBot/0.0",
  "(https://zakuchess.fly.dev/; zakuchess@dunsap.com)",
  "node-fetch",
].join(" ")

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
  [sprintf(ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"], {path:"human-loyalists/fencer.png"}), `${STATIC_FOLDER}/img/chess/units/humans/pawn.png`],
  [sprintf(ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"], {path:"human-loyalists/horseman/horseman.png"}), `${STATIC_FOLDER}/img/chess/units/humans/knight.png`],
  [sprintf(ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"], {path:"human-outlaws/ranger.png"}), `${STATIC_FOLDER}/img/chess/units/humans/bishop.png`],
  [sprintf(ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"], {path:"dwarves/gryphon-rider.png"}), `${STATIC_FOLDER}/img/chess/units/humans/rook.png`],
  [sprintf(ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"], {path:"human-magi/red-mage+female.png"}), `${STATIC_FOLDER}/img/chess/units/humans/queen.png`],
  [sprintf(ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"], {path:"human-loyalists/shocktrooper.png"}), `${STATIC_FOLDER}/img/chess/units/humans/king.png`],
  // "The bad folks" units:
  [sprintf(ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"], {path:"undead-skeletal/deathblade.png"}), `${STATIC_FOLDER}/img/chess/units/undeads/pawn.png`],
  [sprintf(ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"], {path:"undead-skeletal/chocobone.png"}), `${STATIC_FOLDER}/img/chess/units/undeads/knight.png`],
  [sprintf(ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"], {path:"undead-skeletal/banebow.png"}), `${STATIC_FOLDER}/img/chess/units/undeads/bishop.png`],
  [sprintf(ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"], {path:"monsters/skeletal-dragon/skeletal-dragon.png"}), `${STATIC_FOLDER}/img/chess/units/undeads/rook.png`],
  [sprintf(ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"], {path:"undead-necromancers/necromancer+female.png"}), `${STATIC_FOLDER}/img/chess/units/undeads/queen.png`],
  [sprintf(ASSETS_PATTERNS["WESNOTH_UNITS_GITHUB"], {path:"undead-skeletal/draug.png"}), `${STATIC_FOLDER}/img/chess/units/undeads/king.png`],
  // Chess pieces symbols:
  // white pieces:
  [sprintf(ASSETS_PATTERNS["WIKIMEDIA_CHESS_SVG_LIGHT"], {folder:"4/45", piece:"p"}), `${STATIC_FOLDER}/img/chess/symbols/w-pawn.svg`],
  [sprintf(ASSETS_PATTERNS["WIKIMEDIA_CHESS_SVG_LIGHT"], {folder:"7/70", piece:"n"}), `${STATIC_FOLDER}/img/chess/symbols/w-knight.svg`],
  [sprintf(ASSETS_PATTERNS["WIKIMEDIA_CHESS_SVG_LIGHT"], {folder:"b/b1", piece:"b"}), `${STATIC_FOLDER}/img/chess/symbols/w-bishop.svg`],
  [sprintf(ASSETS_PATTERNS["WIKIMEDIA_CHESS_SVG_LIGHT"], {folder:"7/72", piece:"r"}), `${STATIC_FOLDER}/img/chess/symbols/w-rook.svg`],
  [sprintf(ASSETS_PATTERNS["WIKIMEDIA_CHESS_SVG_LIGHT"], {folder:"1/15", piece:"q"}), `${STATIC_FOLDER}/img/chess/symbols/w-queen.svg`],
  [sprintf(ASSETS_PATTERNS["WIKIMEDIA_CHESS_SVG_LIGHT"], {folder:"4/42", piece:"k"}), `${STATIC_FOLDER}/img/chess/symbols/w-king.svg`],
  // black pieces:
  [sprintf(ASSETS_PATTERNS["WIKIMEDIA_CHESS_SVG_DARK"], {folder:"c/c7", piece:"p"}), `${STATIC_FOLDER}/img/chess/symbols/b-pawn.svg`],
  [sprintf(ASSETS_PATTERNS["WIKIMEDIA_CHESS_SVG_DARK"], {folder:"e/ef", piece:"n"}), `${STATIC_FOLDER}/img/chess/symbols/b-knight.svg`],
  [sprintf(ASSETS_PATTERNS["WIKIMEDIA_CHESS_SVG_DARK"], {folder:"9/98", piece:"b"}), `${STATIC_FOLDER}/img/chess/symbols/b-bishop.svg`],
  [sprintf(ASSETS_PATTERNS["WIKIMEDIA_CHESS_SVG_DARK"], {folder:"f/ff", piece:"r"}), `${STATIC_FOLDER}/img/chess/symbols/b-rook.svg`],
  [sprintf(ASSETS_PATTERNS["WIKIMEDIA_CHESS_SVG_DARK"], {folder:"4/47", piece:"q"}), `${STATIC_FOLDER}/img/chess/symbols/b-queen.svg`],
  [sprintf(ASSETS_PATTERNS["WIKIMEDIA_CHESS_SVG_DARK"], {folder:"f/f0", piece:"k"}), `${STATIC_FOLDER}/img/chess/symbols/b-king.svg`],
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
      const path = new Path(pathString)
      await path.dirname().mkdir({ recursive: true })

      if (!downloadEvenIfExists) {
        const exists = await path.exists()
        if (exists) {
          console.log(`Skipping ${url} because ${pathString} already exists.`)
          return
        }
      }

      console.log(`Downloading ${url} to ${pathString}`)
      const response: Response = await fetch(url, {
        headers: { "User-Agent": USER_AGENT },
      })
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
