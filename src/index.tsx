import { serve } from "@hono/node-server"
import { serveStatic } from "@hono/node-server/serve-static"
import { Hono } from "hono"
import { logger } from "hono/logger"
import { Layout } from "./components/layout/Layout.js"
import { ChessArena } from "components/chess/ChessArena.js"
import { ChessGamePresenter } from "business-logic/ChessGamePresenter.js"

const app = new Hono()
app.use("*", logger())
app.use("/static/*", serveStatic({ root: "./" }))
app.get("/", (c) => {
  const gamePresenter = new ChessGamePresenter({
    fen: "6k1/7p/1Q2P2p/4P3/qb2Nr2/1n3N1P/5PP1/5RK1 w - - 3 27",
  })
  return c.html(
    `<!DOCTYPE html>` +
    (
      <Layout>
        <ChessArena gamePresenter={gamePresenter} />
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
