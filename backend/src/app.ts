import { Hono } from "hono";
import { logger as honoLogger } from "hono/logger";
import { secureHeaders } from "hono/secure-headers";
import { serveStatic } from "@hono/node-server/serve-static";
import { logger } from "./logging.ts";
import { getAstroPage } from "./http/astro-bridge.ts";
import { getSettings } from "./settings.ts";

export function getApp(): Hono {
  const app = new Hono();

  const loggingFunc = (str: string, ...rest: string[]): void => {
    logger.info(rest.length ? { msg: str, rest: rest } : str);
  };

  app.use("*", secureHeaders());
  app.use("*", honoLogger(loggingFunc));
  app.use("/assets/*", serveStatic({ root: getSettings().ASTRO_ASSETS_PATH }));

  app.get("/", async (c) => {
    return c.html(await getAstroPage("/"));
  });

  // app.route("", dailyChallengeApp);

  return app;
}
