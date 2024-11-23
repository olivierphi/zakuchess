import { vitePlugin as remix } from "@remix-run/dev"
import { defineConfig } from "vite"
import tsconfigPaths from "vite-tsconfig-paths"

import { routesDefinition } from "./app/routes.ts"

declare module "@remix-run/node" {
    interface Future {
        v3_singleFetch: true
    }
}

// https://remix.run/docs/en/main/guides/vite#plugin-usage-with-other-vite-based-tools-eg-vitest-storybook
const isVitest = process.env.VITEST
const useRemix = !isVitest

export default defineConfig({
    plugins: [
        useRemix
            ? remix({
                  routes: function createRoutes(defineRoutes) {
                      return defineRoutes(routesDefinition)
                  },
                  future: {
                      v3_fetcherPersist: true,
                      v3_relativeSplatPath: true,
                      v3_throwAbortReason: true,
                      v3_singleFetch: true,
                      v3_lazyRouteDiscovery: true,
                  },
              })
            : undefined,
        tsconfigPaths(),
    ],
})
