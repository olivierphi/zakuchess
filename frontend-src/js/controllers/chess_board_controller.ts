import { Controller } from "@hotwired/stimulus"

import type { GamePhase, PlayerSide, FEN, Square } from "../chess-domain"
import { getPieceAvailableTargets } from "../chess-helpers"
import { playFromFEN } from "../chess-bot"

export default class extends Controller {
    static targets = ["piecesContainer", "piece", "availableTargetsContainer", "submitMoveForm"]
    static values = {
        isVersusBot: Boolean,
        gamePhase: String,
        activePlayerSide: String,
    }

    declare readonly pieceTargets: HTMLElement[]
    declare readonly piecesContainerTarget: HTMLElement
    declare readonly availableTargetsContainerTarget: HTMLElement
    declare readonly submitMoveFormTarget: HTMLFormElement
    declare isVersusBotValue: boolean
    declare activePlayerSideValue: PlayerSide
    declare gamePhaseValue: GamePhase

    connect(): void {
        console.log("isVersusBot=", this.isVersusBotValue)
        // Just a quick test :-)
        if (this.isVersusBotValue) {
            playFromFEN(this.getCurrentFEN(), 2).then(
                ([from, to]) => {
                    this.movePiece(from, to)
                },
                (e) => {
                    throw e
                },
            )
        }
    }

    piecesContainerTargetConnected(target: HTMLElement): void {
        console.log("piecesContainerTargetConnected", this.getCurrentFEN())
    }

    selectPiece(event): void {
        const square = event.params.square as Square
        const pieceAvailableTargets = getPieceAvailableTargets(this.getCurrentFEN(), square)
        console.log("selectPiece() :: pieceAvailableTargets=", pieceAvailableTargets)
        this.gamePhaseValue = "waiting_for_selected_piece_target"
        this.displayPieceAvailableTargets(square, pieceAvailableTargets)
    }

    moveSelectedPiece(event): void {
        const from = event.params.from as Square
        const to = event.params.to as Square
        console.log("this.submitMoveFormTarget=", this.submitMoveFormTarget)
        this.movePiece(from, to)
    }

    private movePiece(from: Square, to: Square): void {
        this.submitMoveFormTarget.querySelector<HTMLInputElement>("[name='from']").value = from
        this.submitMoveFormTarget.querySelector<HTMLInputElement>("[name='to']").value = to
        window.htmx.trigger(this.submitMoveFormTarget, "submit")
    }

    private displayPieceAvailableTargets(from: Square, availableTargets: Square[]): void {
        this.availableTargetsContainerTarget.innerHTML = availableTargets
            .map((square) => this.getPieceAvailableTargetElement(from, square))
            .join("")
    }

    private getPieceAvailableTargetElement(from: Square, to: Square): string {
        return `<div class="target square square-${to}" 
            data-action="click->chess-board#moveSelectedPiece"
            data-chess-board-from-param="${from}"
            data-chess-board-to-param="${to}"
        ></div>`
    }

    private getCurrentFEN(): FEN {
        return this.element.querySelector<HTMLElement>("[data-fen]").dataset.fen as FEN
    }

    private clearPieceAvailableTargets(): void {
        this.availableTargetsContainerTarget.innerHTML = ""
    }
}
