import { Application } from "@hotwired/stimulus"
import "htmx.org"

import ChessBoardController from "./controllers/chess_board_controller"
import TeamMembersController from "./controllers/team_members_controller"

const stimulusApp = Application.start()

// Controllers Registration:
stimulusApp.register("chess-board", ChessBoardController)
stimulusApp.register("team-members", TeamMembersController)

// @ts-ignore
window.Stimulus = stimulusApp
// @ts-ignore
window.htmx = htmx
