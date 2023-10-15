import { serve } from "@hono/node-server"
import { serveStatic } from "@hono/node-server/serve-static"
import { Hono } from "hono"
import { logger } from "hono/logger"
import { Layout } from "./components/layout/Layout.js"
import { ChessArena } from "components/chess/ChessArena.js"

const app = new Hono()
app.use("*", logger())
app.use("/static/*", serveStatic({ root: "./" }))
app.get("/", (c) => {
  return c.html(
    `<!DOCTYPE html>` +
    (
      <Layout>
        <ChessArena />
      </Layout>
    ),
  )
})

const serverOptions = {
  fetch: app.fetch,
  hostname: process.env.SERVER_HOST || "localhost",
  port: parseInt(process.env.SERVER_PORT || "3000", 10),
}
console.info(`Starting server on ${serverOptions.hostname}:${serverOptions.port}`)

serve(serverOptions)
