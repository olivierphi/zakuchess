import { Press_Start_2P } from "@next/font/google"

const fontPressStart2P = Press_Start_2P({
	weight: "400",
	subsets: ["latin"],
	variable: "--font-pixel",
})

export default function Header() {
	return (
		<div className={`text-center ${fontPressStart2P.className}`}>
			<h1 className="text-slate-50 text-2xl font-pixel">Zakuchess</h1>
			<h2 className="text-slate-50 text-xl font-pixel">Chess with character(s)</h2>
		</div>
	)
}
