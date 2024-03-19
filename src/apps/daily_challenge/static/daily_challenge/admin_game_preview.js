;(function () {
    /**
     * This file is pretty messy, but it's only used in the admin interface and
     * this is a side project after all, so it's not a big deal.
     * It works with the `admin.py` from the same Django app.
     * Contrary to the rest of the JS code of this project, this one is not written in
     * TypeScript because it's just much easier to use it as in with the Django Admin.
     * HERE BE DRAGONS! 😅
     */

    const gameUpdateCommandPatterns = [
        /^[a-h][1-8]:add:[pnbrqkx]!\s*$/i, // "add" command
        /^[a-h][1-8]:rm!\s*$/i, // "remove" command
        /^[a-h][1-8]:mv:[a-h][1-8]!\s*$/i, // "move" command
        /^mirror!\s*$/i, // "mirror" command
        /^s(?:olve)?!\s*$/i, // "solve" command
    ]

    const gameUpdateCommandResetPattern = /^.*!\s*$/i

    window.startSolution = startSolution
    setTimeout(init, 100)

    function init() {
        const adminPreviewUrlHolder = document.getElementById("admin-preview-url-holder")
        if (!adminPreviewUrlHolder) {
            return
        }
        const adminPreviewUrl = adminPreviewUrlHolder.innerText

        const previewIFrame = document.getElementById("preview-iframe")

        const fenInput = document.getElementById("id_fen")
        const botFirstMoveInput = document.getElementById("id_bot_first_move")
        const introTurnSpeechSquareInput = document.getElementById("id_intro_turn_speech_square")
        const botDepthInput = document.getElementById("id_bot_depth")
        const playerSimulatedDepthInput = document.getElementById("id_player_simulated_depth")

        const gameUpdateInput = document.getElementById("id_update_game")

        function updatePreview(gameUpdate) {
            const fen = fenInput.value
            if (!fen) {
                return
            }
            const queryString = new URLSearchParams({
                fen,
                bot_first_move: botFirstMoveInput.value,
                intro_turn_speech_square: introTurnSpeechSquareInput.value,
                bot_depth: botDepthInput.value,
                player_simulated_depth: playerSimulatedDepthInput.value,
                game_update: gameUpdate || "",
            }).toString()
            previewIFrame.src = adminPreviewUrl + "?" + queryString
        }

        function onChessBoardFieldKeyUp(event) {
            if (document.getElementById("id_bot_first_move")?.value.length !== 4) {
                return
            }
            updatePreview(null)
        }

        fenInput.addEventListener("keyup", onChessBoardFieldKeyUp)
        botFirstMoveInput.addEventListener("keyup", onChessBoardFieldKeyUp)
        introTurnSpeechSquareInput.addEventListener("keyup", onChessBoardFieldKeyUp)

        function onGameUpdateInputKeyUp() {
            const inputValue = gameUpdateInput.value
            for (const pattern of gameUpdateCommandPatterns) {
                const match = pattern.exec(inputValue)
                if (!match) {
                    continue
                }
                updatePreview(inputValue)
                gameUpdateInput.value = ""
                gameUpdateInput.focus()
                return
            }
            if (gameUpdateCommandResetPattern.exec(inputValue)) {
                gameUpdateInput.value = ""
                gameUpdateInput.focus()
            }
        }

        gameUpdateInput.addEventListener("keyup", onGameUpdateInputKeyUp)

        setTimeout(updatePreview, 100)
    }

    const SOLUTION_CHESS_JS_PACKAGE_URL = "https://cdnjs.cloudflare.com/ajax/libs/chess.js/0.13.4/chess.min.js"
    const SOLUTION_BOT_ASSETS_DATA_HOLDER_ELEMENT_ID = "chess-bot-data-admin"
    const SOLUTION_TURNS_COUNT_MAX = 15 // we want the daily challenges to be short enough

    function startSolution({ botTurnDepth, playerTurnDepth }) {
        const previewIFrame = document.getElementById("preview-iframe")
        const solutionInput = document.getElementById("id_solution")
        const solutionInputHelpText = document.getElementById("id_solution_helptext")

        solutionInput.value = ""
        solutionInputHelpText.innerText = "Loading chess.js and spawning our own chess engine worker..."

        setTimeout(function initSolutionRequirements() {
            // We have to spawn our own chess engine worker for the human player, because it turns out that
            // some engines are not completely stateless, and the moves we ask it to make with a lower depth for the bot
            // can be influenced by the calculations it made to simulate the human player, with a higher depth.
            // Which leads to the bot making different moves than what it would make if it was only calculating for itself.
            const chessBotDataHolder = previewIFrame.contentWindow.document.getElementById(
                SOLUTION_BOT_ASSETS_DATA_HOLDER_ELEMENT_ID,
            )
            if (!chessBotDataHolder) {
                window.alert(
                    `The chess bot data holder is missing in the preview iframe (ID: ${SOLUTION_BOT_ASSETS_DATA_HOLDER_ELEMENT_ID}).`,
                )
                return
            }

            const chessEngineWorkerForHumanPlayerInitPromise =
                previewIFrame.contentWindow.__admin__getChessEngineWorker(chessBotDataHolder)
            const chessJsInitPromise = import(SOLUTION_CHESS_JS_PACKAGE_URL)
            Promise.all([chessEngineWorkerForHumanPlayerInitPromise, chessJsInitPromise]).then(
                ([chessEngineWorkerForHumanPlayer, chessjs]) => {
                    const fen = document.getElementById("id_fen").value
                    const chessBoard = chessjs.Chess(fen)
                    const solutionState = {
                        solutionInput,
                        previewIFrame,
                        chessEngineWorkerForHumanPlayer,
                        solutionInputHelpText,
                        fen,
                        chessBoard,
                        botTurnDepth,
                        playerTurnDepth,
                        turnsCount: 0,
                    }
                    solutionInputHelpText.innerText = "Starting solution in a bit..."
                    setTimeout(solutionNextMove.bind(null, solutionState), 100)
                },
            )
        }, 1000)
    }

    function solutionNextMove(solutionState) {
        const { fen, chessBoard, previewIFrame, solutionInput, solutionInputHelpText } = solutionState
        const isHumanPlayerTurn = chessBoard.turn() === "w"
        const depth = isHumanPlayerTurn ? solutionState.playerTurnDepth : solutionState.botTurnDepth
        const chessEngineWorkerToUse = isHumanPlayerTurn ? solutionState.chessEngineWorkerForHumanPlayer : null
        previewIFrame.contentWindow.__admin__playFromFEN(fen, depth, "", chessEngineWorkerToUse).then((move) => {
            const moveStr = `${move[0]}${move[1]}`
            solutionInput.value += `${moveStr},`
            // @link https://github.com/jhlywa/chess.js/tree/v0.13.4?tab=readme-ov-file#movemove--options-
            const moveResult = chessBoard.move(moveStr, { sloppy: true })
            if (!moveResult) {
                window.alert(`Invalid move: ${moveStr}`)
                return
            }
            if (isHumanPlayerTurn) {
                solutionState.turnsCount++
                solutionInputHelpText.innerText = `Turns: ${solutionState.turnsCount}`
            }
            if (solutionState.turnsCount > SOLUTION_TURNS_COUNT_MAX) {
                window.alert("Game won't work: too many turns.")
                return
            }
            if (chessBoard.in_checkmate()) {
                window.alert(`'${chessBoard.turn()}' player is checkmate in ${solutionState.turnsCount} turns.`)
                // Remove the last comma:
                solutionInput.value = solutionInput.value.replace(/,$/, "")
                return
            }
            if (chessBoard.in_draw() || chessBoard.in_stalemate()) {
                window.alert("Game finished: draw.")
                return
            }
            solutionState.fen = chessBoard.fen()

            setTimeout(solutionNextMove.bind(null, solutionState), 100)
        })
    }
})()
