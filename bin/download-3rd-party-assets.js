#!/usr/bin/env zx
import { createWriteStream } from "node:fs"
import * as fs from "node:fs/promises"
import { join } from "node:path"
import { pipeline } from "node:stream"
import { promisify } from "node:util"

import "zx/globals"

const streamPipeline = promisify(pipeline)

const CHESS_STATIC = join(__dirname, "../public/chess/")

const ASSETS_MAP = {
	// Wesnoth assets:
	"https://github.com/wesnoth/wesnoth/raw/master/data/core/images/units/human-loyalists/bowman.png": join(
		CHESS_STATIC,
		"units",
		"default",
		"bowman.png",
	),
	"https://github.com/wesnoth/wesnoth/raw/master/data/core/images/units/human-loyalists/fencer.png": join(
		CHESS_STATIC,
		"units",
		"default",
		"fencer.png",
	),
	"https://github.com/wesnoth/wesnoth/raw/master/data/core/images/units/human-loyalists/general.png": join(
		CHESS_STATIC,
		"units",
		"default",
		"general.png",
	),
	"https://github.com/wesnoth/wesnoth/raw/master/data/core/images/units/human-loyalists/horseman/horseman.png": join(
		CHESS_STATIC,
		"units",
		"default",
		"horseman.png",
	),
	"https://github.com/wesnoth/wesnoth/raw/master/data/core/images/units/human-magi/red-mage+female.png": join(
		CHESS_STATIC,
		"units",
		"default",
		"red-mage+female.png",
	),
	"https://github.com/wesnoth/wesnoth/raw/master/data/core/images/units/human-loyalists/shocktrooper.png": join(
		CHESS_STATIC,
		"units",
		"default",
		"shocktrooper.png",
	),
	"https://github.com/wesnoth/wesnoth/raw/master/data/core/images/units/human-loyalists/swordsman.png": join(
		CHESS_STATIC,
		"units",
		"default",
		"swordsman.png",
	),
}

async function downloadAssets() {
	for (const [url, path] of Object.entries(ASSETS_MAP)) {
		try {
			const fileExists = (await fs.stat(path)).isFile
			console.log(`"${path}" already exists, skipping.`)
			continue
		} catch (err) {}
		const response = await fetch(url)
		if (!response.ok) throw new Error(`unexpected response ${response.statusText}`)
		await streamPipeline(response.body, createWriteStream(path))
	}
}

downloadAssets()
	.then(() => console.log("Finished."))
	.catch((err) => console.error(err))
