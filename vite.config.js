/** @type {import('vite').UserConfig} */
export default {
  outdir: "./dist/assets",
  build: {
    rollupOptions: {
      // overwrite default .html entry
      input: {
        "js/main": "./src/frontend/js/main.ts",
        "css/tailwind": "./static-src/css/tailwind.css",
        "fonts/fibberish": "./static-src/fonts/fibberish.ttf",
      },
    },
    // generate manifest.json in outDir
    manifest: true,
  },
}
