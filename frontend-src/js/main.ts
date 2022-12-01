import { Application } from "@hotwired/stimulus"
import "htmx.org"

import ChessBoardController from "./controllers/chess_board_controller"

const stimulusApp = Application.start()

// Controllers Registration:
stimulusApp.register("chess-board", ChessBoardController)

// @ts-ignore
window.Stimulus = stimulusApp
// @ts-ignore
window.htmx = htmx
