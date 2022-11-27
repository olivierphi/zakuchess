import { defineConfig } from 'vite'

export default defineConfig({
  root: "frontend/",
  base: "/static/", // must be the same than our Django's STATIC_URL
  outDir: "frontend-out", // must be the same than our Django's DJANGO_VITE_ASSETS_PATH
  manifest: true,
  rollupOptions: {
      input: {
        "js/main.ts": "js/main.ts",
        "css/chess-board.scss": "css/chess-board.scss",
      }
    }
})
