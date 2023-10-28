import { Hono } from "hono"
import { logger as honoLogger } from "hono/logger"
import { secureHeaders } from "hono/secure-headers"
import { serveStatic } from "@hono/node-server/serve-static"
import { logger } from "./logging.js"
import { dailyChallengeApp } from "./routes/daily-challenge.js"

export const app = new Hono()

const loggingFunc = (str: string, ...rest: string[]): void => {
  logger.info(rest.length ? { msg: str, rest: rest } : str)
}

app.use("*", secureHeaders())
app.use("*", honoLogger(loggingFunc))
app.use("/static/*", serveStatic({ root: "./" }))

app.route("", dailyChallengeApp)
