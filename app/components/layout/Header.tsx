import { memo } from "react"

export const Header = memo(function Header() {
    return (
        <header className="text-center md:mx-auto md:max-w-2xl">
            <h1 className="text-slate-50 text-2xl leading-none font-pixel">ZakuChess</h1>
            <h2 className="text-slate-50 text-xl leading-none font-pixel">
                Chess with character(s)
            </h2>
        </header>
    )
})
