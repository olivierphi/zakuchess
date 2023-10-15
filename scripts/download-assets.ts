import { Readable } from "node:stream"
import type { PipelinePromise, Writable } from "node:stream"
import { pipeline } from "node:stream/promises"
import { copyFile } from "node:fs/promises"
import pLimit from "p-limit"
import { sprintf } from "sprintf-js"
import Path from "@mojojs/path"

type URL = string

const STATIC_FOLDER = "./static"

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

const ASSETS_TO_DOWNLOAD_MAP: Record<URL, string> = {
  // Fonts:
  // prettier-ignore
  [sprintf(ASSETS_PATTERNS["GOOGLE_FONTS"], {fontName: "opensans",fileId: "mem8YaGs126MiZpBA-UFVZ0b",v: "v35"})]: `${STATIC_FOLDER}/fonts/OpenSans.woff2`,
  // Stockfish:
  // prettier-ignore
  [sprintf(ASSETS_PATTERNS["STOCKFISH_CDN"], {file: "stockfish.min.js"})]: `${STATIC_FOLDER}/js/bot/stockfish.js`,
  // prettier-ignore
  [sprintf(ASSETS_PATTERNS["STOCKFISH_CDN"], {file: "stockfish.wasm"})]: `${STATIC_FOLDER}/js/bot/stockfish.wasm`,
  // prettier-ignore
  [sprintf(ASSETS_PATTERNS["STOCKFISH_CDN"], {file: "stockfish.wasm.min.js"})]: `${STATIC_FOLDER}/js/bot/stockfish.wasm.js`,
}
const ASSETS_TO_COPY_MAP: Record<string, string> = {
  "./static-src/fonts/fibberish.ttf": `${STATIC_FOLDER}/fonts/fibberish.ttf`,
}

async function downloadAssets() {
  const promisesLimiter = pLimit(3) // we'll run 3 downloads in parallel

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
    downloadPromises.push(promisesLimiter(downloadPromiseGenerator))
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
  .then(() => copyAssets())
  .then(() => console.log("Done"))
  .catch(console.error)
