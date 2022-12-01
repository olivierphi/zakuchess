import * as Turbo from "@hotwired/turbo"
import { Application } from "@hotwired/stimulus"
// We need this polyfill for Safari, as calling `submit()` on Turbo-ed forms doesn't submit them via Turbo
// --> we have to call "requestSubmit()" instead.
// @link https://discuss.hotwired.dev/t/triggering-turbo-frame-with-js/1622/37?page=2
import "form-request-submit-polyfill"

import ChessBoardController from "./controllers/chess_board_controller"

Turbo.start()

window.Stimulus = Application.start()
Stimulus.register("chess-board", ChessBoardController)
