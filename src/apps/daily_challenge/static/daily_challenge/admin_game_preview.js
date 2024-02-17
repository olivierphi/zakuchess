;(function () {
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
        const adminPreviewUrl = document.getElementById("admin-preview-url-holder").innerText

        const previewIFrame = document.getElementById("preview-iframe")

        const fenInput = document.getElementById("id_fen")
        const botFirstMoveInput = document.getElementById("id_bot_first_move")
        const introTurnSpeechSquareInput = document.getElementById("id_intro_turn_speech_square")

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

    // The following value is the depth we want the bot to calculate its moves with when we
    // simulate the human player's turn:
    const SOLUTION_PLAYER_TURN_DEPTH = 10
    // For such solutions to work, the value of `SOLUTION_BOT_TURN_DEPTH` *must* be the same
    // as the `_BOT_DEPTH` const defined in the Python code - if it's not, the bot will make
    // different moves than what the solution expects, making the solution irrelevant.
    const SOLUTION_BOT_TURN_DEPTH = 3

    function startSolution() {
        const previewIFrame = document.getElementById("preview-iframe")
        const solutionInputHelpText = document.getElementById("id_solution_helptext")
        solutionInputHelpText.innerText = "Loading chess.js and spawning our own chess engine worker..."
        setTimeout(function initSolutionRequirements() {
            // We have to spawn our own chess engine worker for the human player, because it turns out that
            // some engines are not completely stateless, and the moves we ask it to make with depth 1 for the bot
            // can be influenced by the calculations it made for the human player - leading to the bot making different
            // moves than what it would make if it was only calculating for itself.
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
                        solutionInput: document.getElementById("id_solution"),
                        previewIFrame,
                        chessEngineWorkerForHumanPlayer,
                        solutionInputHelpText,
                        fen,
                        chessBoard,
                        turnsCount: 0,
                    }
                    solutionState.solutionInput.value = ""
                    solutionInputHelpText.innerText = "Starting solution in a bit..."
                    setTimeout(solutionNextMove.bind(null, solutionState), 100)
                },
            )
        }, 1000)
    }

    function solutionNextMove(solutionState) {
        const { fen, chessBoard, previewIFrame, solutionInput, solutionInputHelpText } = solutionState
        const isHumanPlayerTurn = chessBoard.turn() === "w"
        const depth = isHumanPlayerTurn ? SOLUTION_PLAYER_TURN_DEPTH : SOLUTION_BOT_TURN_DEPTH
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
