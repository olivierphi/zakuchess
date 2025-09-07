/// <reference types="node" />
import { serve } from "@hono/node-server";
// import { serveStatic } from "@hono/node-server/serve-static";
import { getApp } from "./app.ts";
import { type Settings, setSettings } from "./settings.ts";
import path from "node:path";
import { serveStatic } from "@hono/node-server/serve-static";

// Quick sanity check:
if (parseInt(process.versions.node.split(".")[0], 10) < 24) {
  console.error(
    `Node.js version 24 or higher is required, got ${process.version}.`,
  );
  process.exit(1);
}

const isProduction = process.env.NODE_ENV === "production";

const frontendPath = path.join(import.meta.dirname, "..", "..", "frontend");

// Settings management
const settings: Settings = {
  DEVELOPMENT_MODE: !isProduction,
  ZAKUCHESS_VERSION: process.env.ZAKUCHESS_VERSION || "dev",
  COOKIES_SIGNING_SECRET: process.env.COOKIES_SIGNING_SECRET || "",
  ASTRO_DEV_URL: "http://localhost:4321",
  ASTRO_PROD_BUILD_PATH: path.join(frontendPath, "dist"),
  ASTRO_ASSETS_PATH: path.join(frontendPath, "public"),
};
setSettings(settings);

const app = getApp();

if (!settings.DEVELOPMENT_MODE) {
  app.use("/_astro/*", serveStatic({ root: settings.ASTRO_PROD_BUILD_PATH }));
}

const serverOptions = {
  fetch: app.fetch,
  hostname: process.env.SERVER_HOST || "localhost",
  port: parseInt(process.env.SERVER_PORT || "3000", 10),
};
console.info(
  `Starting server on http://${serverOptions.hostname}:${serverOptions.port}`,
);

serve(serverOptions);
