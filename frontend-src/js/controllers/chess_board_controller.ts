import { Controller } from "@hotwired/stimulus"

import type { GamePhase, PlayerSide, FEN, Square } from "../chess-domain"
import { getPieceAvailableTargets } from "../chess-helpers"

export default class extends Controller {
    static targets = ["piece", "availableTargetsContainer", "submitMoveForm"]
    static values = {
        fen: String,
        gamePhase: String,
        activePlayerSide: String,
    }

    declare readonly pieceTargets: HTMLInputElement[]
    declare readonly availableTargetsContainerTarget: HTMLInputElement
    declare readonly submitMoveFormTarget: HTMLFormElement
    declare fenValue: FEN
    declare activePlayerSideValue: PlayerSide
    declare gamePhaseValue: GamePhase

    selectPiece(event) {
        const square = event.params.square as Square
        const pieceAvailableTargets = getPieceAvailableTargets(this.fenValue, square)
        this.gamePhaseValue = "waiting_for_selected_piece_target"
        this.displayPieceAvailableTargets(square, pieceAvailableTargets)
    }

    moveSelectedPiece(event) {
        const from = event.params.from as Square
        const to = event.params.to as Square
        console.log("this.submitMoveFormTarget=", this.submitMoveFormTarget)
        this.submitMoveFormTarget.querySelector<HTMLInputElement>("[name='from']").value = from
        this.submitMoveFormTarget.querySelector<HTMLInputElement>("[name='to']").value = to
        this.submitMoveFormTarget.requestSubmit()
    }

    private displayPieceAvailableTargets(from: Square, availableTargets: Square[]) {
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

    private clearPieceAvailableTargets() {
        this.availableTargetsContainerTarget.innerHTML = ""
    }
}
