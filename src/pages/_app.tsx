import { Roboto } from "@next/font/google"
import type { AppProps } from "next/app"
import Head from "next/head"

import Header from "$lib/components/layout/Header"
import { trpc } from "$lib/utils/trpc"

import "../../styles/globals.css"

const fontRoboto = Roboto({
	weight: "400",
	subsets: ["latin"],
	variable: "--font-roboto",
})

export default trpc.withTRPC(ZakuchessApp)

function ZakuchessApp({ Component, pageProps }: AppProps) {
	return (
		<>
			<Head>
				<title>ZakuChess ♞</title>
				<meta name="description" content="ZakuChess" />
				<meta name="keywords" content="chess roleplay" />
				<meta name="viewport" content="width=device-width, initial-scale=1" />
				<link rel="icon" href="/favicon.ico" />
			</Head>
			<div className="whole-content-container md:mx-auto md:max-w-2xl margin-x-auto">
				<Header />
				<main className={fontRoboto.className}>
					<Component {...pageProps} />
				</main>
			</div>
		</>
	)
}
