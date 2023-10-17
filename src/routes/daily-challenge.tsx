import { BaseChessGamePresenter } from "business-logic/BaseChessGamePresenter.js"
import { ChessArena } from "components/chess/ChessArena.js"
import { Layout } from "components/layout/Layout.js"
import { Hono } from "hono"

export const dailyChallengeApp = new Hono()

dailyChallengeApp.get("/", (c) => {
  // Temporarily hard-coding a GamePresenter here:
  const gamePresenter = new BaseChessGamePresenter({
    fen: "6k1/7p/1Q2P2p/4P3/qb2Nr2/1n3N1P/5PP1/5RK1 w - - 3 27",
  })

  return c.html(
    `<!DOCTYPE html>` +
    (
      <Layout>
        <ChessArena gamePresenter={gamePresenter} />
      </Layout>
    ),
  )
})
