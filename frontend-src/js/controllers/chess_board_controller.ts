import { Controller } from "@hotwired/stimulus"

import type { GamePhase, PlayerSide, FEN, Square } from "../chess-domain"
import { getPieceAvailableTargets } from "../chess-helpers"
import { playFromFEN } from "../chess-bot"
import { ActionEvent } from "@hotwired/stimulus/dist/types/core/action_event"
import { DEFAULT_POSITION } from "chess.js/src/chess"

const PIECES_MOVE_TRANSITION_DURATION = 300 // we've set 0.3s in the SCSS file

type ChessBoardControllerState = {
    fen: FEN
    activePlayerSide: PlayerSide
    botSide: PlayerSide | null
    gamePhase: GamePhase
}

const INITIAL_STATE: Readonly<ChessBoardControllerState> = {
    fen: DEFAULT_POSITION as FEN,
    activePlayerSide: "w",
    botSide: null,
    gamePhase: "waiting_for_piece_selection",
}

export default class extends Controller {
    static targets = ["piecesContainer", "piece", "availableTargetsContainer", "submitMoveForm"]
    static values = {
        botSide: String,
    }

    state: ChessBoardControllerState = INITIAL_STATE

    declare readonly pieceTargets: HTMLElement[]
    declare readonly piecesContainerTarget: HTMLElement
    declare readonly availableTargetsContainerTarget: HTMLElement
    declare readonly submitMoveFormTarget: HTMLFormElement
    declare botSideValue: string

    piecesContainerTargetConnected(target: HTMLElement): void {
        console.log("piecesContainerTargetConnected")
        this.updateStateFromDOM()
    }

    selectPiece(event: ActionEvent): void {
        const square = event.params.square as Square
        const pieceAvailableTargets = getPieceAvailableTargets(this.getCurrentFEN(), square)
        console.log("selectPiece() :: pieceAvailableTargets=", pieceAvailableTargets)
        this.state.gamePhase = "waiting_for_selected_piece_target"
        this.displayPieceAvailableTargets(square, pieceAvailableTargets)
    }

    moveSelectedPiece(event: ActionEvent): void {
        const from = event.params.from as Square
        const to = event.params.to as Square
        console.log("this.submitMoveFormTarget=", this.submitMoveFormTarget)
        this.movePiece(from, to)
    }

    private updateStateFromDOM(): void {
        this.state = {
            ...this.state,
            fen: this.getCurrentFEN(),
            activePlayerSide: this.getActivePlayerSide(),
            botSide: this.botSideValue === "" ? null : (this.botSideValue as PlayerSide),
        }
        console.log("updateStateFromDOM() :: this.state=", this.state)
        if (this.isBotsTurn()) {
            this.playBotAfterPieceMoved()
        }
    }

    private movePiece(from: Square, to: Square): void {
        this.submitMoveFormTarget.querySelector<HTMLInputElement>("[name='from']")!.value = from
        this.submitMoveFormTarget.querySelector<HTMLInputElement>("[name='to']")!.value = to
        window.htmx.trigger(this.submitMoveFormTarget, "submit", {})
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
        return this.element.querySelector<HTMLElement>("[data-fen]")!.dataset.fen as FEN
    }

    private getActivePlayerSide(): PlayerSide {
        return this.element.querySelector<HTMLElement>("[data-active-player-side]")!.dataset
            .activePlayerSide as PlayerSide
    }

    private isBotsTurn(): boolean {
        return this.state.botSide === this.state.activePlayerSide
    }

    private playBot(): void {
        playFromFEN(this.getCurrentFEN(), 2).then(
            ([from, to]) => {
                this.movePiece(from, to)
            },
            (e) => {
                console.error("error while trying to play bot's turn!")
                throw e
            },
        )
    }
    private playBotAfterPieceMoved(): void {
        setTimeout(this.playBot.bind(this), PIECES_MOVE_TRANSITION_DURATION)
    }

    private clearPieceAvailableTargets(): void {
        this.availableTargetsContainerTarget.innerHTML = ""
    }
}
