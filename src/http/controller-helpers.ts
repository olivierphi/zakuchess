import type { HonoRequest } from "hono"
import type { DailyChallenge } from "../apps/daily-challenge/business-logic/models.js"

export const getCurrentDailyChallengeOrAdminPreview = async (
  request: HonoRequest, // eslint-disable-line @typescript-eslint/no-unused-vars
): Promise<[challenge: DailyChallenge, isPreview: boolean]> => {
  // hard-coded game for now
  return [HARD_CODED_TMP_DAILY_CHALLENGE, false]
}

const HARD_CODED_TMP_DAILY_CHALLENGE: DailyChallenge = {
  lookupKey: "fallback",
  fen: "6k1/7p/1Q2P2p/4P3/qb2Nr2/1n3N1P/5PP1/5RK1 w - - 3 27",
  pieceStateBySquare: {
    g8: "k",
    h7: "p1",
    h6: "p2",
    e6: "P1",
    b6: "Q",
    e5: "P2",
    f4: "r1",
    e4: "N1",
    b4: "b1",
    a4: "q",
    h3: "P3",
    f3: "N2",
    b3: "n1",
    g2: "P4",
    f2: "P5",
    g1: "K",
    f1: "R1",
  },
  teams: {
    w: [
      { id: "P1", faction: "humans", name: ["Abdul", "Philippon"] },
      { id: "Q", faction: "humans", name: ["Tetsuo", "Lebowsky"] },
      { id: "P2", faction: "humans", name: ["John", "Devi"] },
      { id: "N1", faction: "humans", name: ["Rae", "Kitano"] },
      { id: "P3", faction: "humans", name: ["Joachim", "Nguyen"] },
      { id: "N2", faction: "humans", name: ["Sydney", "Lion"] },
      { id: "P4", faction: "humans", name: ["Kelly", "Wang"] },
      { id: "P5", faction: "humans", name: ["Luis", "Hermosa"] },
      { id: "K", faction: "humans", name: ["Roger", "Stevens"] },
      { id: "R1", faction: "humans", name: ["Fab", "Force"] },
    ],
    b: [
      { id: "k", faction: "undeads" },
      { id: "p1", faction: "undeads" },
      { id: "p2", faction: "undeads" },
      { id: "r1", faction: "undeads" },
      { id: "b1", faction: "undeads" },
      { id: "q", faction: "undeads" },
      { id: "n1", faction: "undeads" },
    ],
  },
  mySide: "w",
  botSide: "b",
}
