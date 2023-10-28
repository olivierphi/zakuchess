import { readFileSync } from "node:fs"
import { serve } from "@hono/node-server"
import { serveStatic } from "@hono/node-server/serve-static"
import { app } from "./app.js"
import {
  type StaticAssetsMapping,
  setStaticAssetsMapping,
  setStaticAssetsViteDevServerURL,
} from "./helpers/assets-helpers.js"
import { type Settings, setSettings } from "./settings.js"

// Quick sanity check:
if (parseInt(process.versions.node.split(".")[0], 10) < 18) {
  console.error(`Node.js version 18 or higher is required, got ${process.version}.`)
  process.exit(1)
}

const isProduction = process.env.NODE_ENV === "production"

// Settings management
const settings: Settings = {
  DEVELOPMENT_MODE: !isProduction,
  ZAKUCHESS_VERSION: process.env.ZAKUCHESS_VERSION || "dev",
  COOKIES_SIGNING_SECRET: process.env.COOKIES_SIGNING_SECRET || "",
}
setSettings(settings)

// Assets management, via Vite
if (isProduction) {
  const staticAssetsManifestPath =
    process.env.STATIC_ASSETS_MANIFEST_PATH || "dist/manifest.json"

  // N.B. It's fine to read the file synchronously here, because the server
  // hasn't started yet so we don't need concurrency at this point.
  const staticAssetsManifestFileContent = readFileSync(staticAssetsManifestPath, "utf-8")
  const staticAssetsManifestRaw = JSON.parse(staticAssetsManifestFileContent) as Record<
    string,
    { file: string; isEntry?: boolean; src: string }
  >

  const staticAssetsManifest: StaticAssetsMapping = Object.fromEntries(
    Object.entries(staticAssetsManifestRaw)
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      .filter(([id, { isEntry }]) => isEntry)
      .map(([id, { file }]) => [id, file]),
  )
  setStaticAssetsMapping(staticAssetsManifest)
} else {
  const viteDevServerURL = process.env.VITE_DEV_SERVER_URL || "http://localhost:5173"
  setStaticAssetsViteDevServerURL(viteDevServerURL)
}

app.use("/assets/*", serveStatic({ root: "./dist" }))

const serverOptions = {
  fetch: app.fetch,
  hostname: process.env.SERVER_HOST || "localhost",
  port: parseInt(process.env.SERVER_PORT || "3000", 10),
}
console.info(`Starting server on http://${serverOptions.hostname}:${serverOptions.port}`)

serve(serverOptions)
