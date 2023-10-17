import { serveStatic } from "@hono/node-server/serve-static"
import { Hono } from "hono"
import { logger } from "hono/logger"
import { secureHeaders } from "hono/secure-headers"
import { dailyChallengeApp } from "routes/daily-challenge.js"

export const app = new Hono()

app.use("*", secureHeaders())
app.use("*", logger())
app.use("/static/*", serveStatic({ root: "./" }))

app.route("", dailyChallengeApp)
