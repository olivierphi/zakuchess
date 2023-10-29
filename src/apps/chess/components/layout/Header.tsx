import { type FC, memo } from "hono/jsx"

export const Header: FC = memo(() => {
  return (
    <header class="text-center md:mx-auto md:max-w-2xl">
      <h1 class="text-slate-50 text-2xl leading-none font-pixel">ZakuChess</h1>
      <h2 class="text-slate-50 text-xl leading-none font-pixel">
        Chess with character(s)
      </h2>
    </header>
  )
})
