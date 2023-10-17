import { serve } from "@hono/node-server"
import { app } from "./app.js"

// Quick sanity check:
if (parseInt(process.versions.node.split(".")[0], 10) < 18) {
  console.error(`Node.js version 18 or higher is required, got ${process.version}.`)
  process.exit(1)
}

const serverOptions = {
  fetch: app.fetch,
  hostname: process.env.SERVER_HOST || "localhost",
  port: parseInt(process.env.SERVER_PORT || "3000", 10),
}
console.info(`Starting server on http://${serverOptions.hostname}:${serverOptions.port}`)

serve(serverOptions)
