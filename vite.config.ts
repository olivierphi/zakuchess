import { reactRouter } from "@react-router/dev/vite"
import { defineConfig } from "vite"
import tsconfigPaths from "vite-tsconfig-paths"

declare module "@react-router/node" {
    interface Future {
        v3_singleFetch: true
    }
}

// https://remix.run/docs/en/main/guides/vite#plugin-usage-with-other-vite-based-tools-eg-vitest-storybook
const isVitest = process.env.VITEST
const useRemix = !isVitest

export default defineConfig({
    plugins: [useRemix ? reactRouter() : undefined, tsconfigPaths()],
})
