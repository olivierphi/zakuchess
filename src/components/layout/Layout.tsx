import type { FC } from "hono/jsx"
import {
  getStaticAssetsViteDevServerURL,
  staticAssetPath,
} from "../../helpers/assets-helpers.js"
import { getSettings } from "../../settings.js"
import { Footer } from "./Footer.js"
import { Header } from "./Header.js"

export type LayoutProps = {
  title?: string
}

const _FONTS_CSS = `
@font-face {
  font-family: 'OpenSans';
  src: url('/static/fonts/OpenSans.woff2') format('woff2');
}
@font-face {
  font-family: 'PixelFont';
  src: url('/static/fonts/fibberish.ttf') format('truetype');
}
`

export const Layout: FC<LayoutProps> = (props) => {
  return (
    <html>
      <Head title={props.title} />
      <body class="bg-slate-900">
        <Header />
        <section class="w-full md:max-w-lg mx-auto">{props.children}</section>
        <Footer />
      </body>
    </html>
  )
}

type HeadProps = {
  title?: string
}

const Head: FC<HeadProps> = (props) => {
  const isDevelopmentMode = getSettings().DEVELOPMENT_MODE
  const jsTypeAttributes = isDevelopmentMode ? { type: "module" } : {}

  return (
    <head>
      <meta charset="utf-8" />
      <title>{props.title || "ZakuChess ♞"}</title>
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <meta name="description" content="ZakuChess" />
      <meta name="keywords" content="chess roleplay pixel-art" />
      <style dangerouslySetInnerHTML={{ __html: _FONTS_CSS }} />
      {isDevelopmentMode ? (
        <script type="module" src={`${getStaticAssetsViteDevServerURL()}/@vite/client`} />
      ) : null}
      <link rel="stylesheet" href={staticAssetPath("static-src/css/tailwind.css")} />
      <script src={staticAssetPath("src/frontend/js/main.ts")} {...jsTypeAttributes} />
    </head>
  )
}
