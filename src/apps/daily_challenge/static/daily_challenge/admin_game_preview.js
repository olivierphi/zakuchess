;(function () {
    const gameUpdateCommandPatterns = [
        /^[a-h][1-8]:add:[pnbrqkx]!\s*$/i, // "add" command
        /^[a-h][1-8]:rm!\s*$/i, // "remove" command
        /^[a-h][1-8]:mv:[a-h][1-8]!\s*$/i, // "move" command
        /^mirror!\s*$/i, // "mirror" command
        /^solve!\s*$/i, // "solve" command
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

    const SOLUTION_BOT_ASSETS_DATA_HOLDER_ELEMENT_ID = "chess-bot-data-admin"
    const SOLUTION_PLAYER_TURN_DEPTH = 10
    const SOLUTION_BOT_TURN_DEPTH = 1 // that's the level it really plays at against players :-)

    function startSolution() {
        import("https://cdnjs.cloudflare.com/ajax/libs/chess.js/0.13.4/chess.js").then((chessjs) => {
            const fen = document.getElementById("id_fen").value
            const chessBoard = chessjs.Chess(fen)
            const solutionState = {
                previewIFrame: document.getElementById("preview-iframe"),
                solutionInput: document.getElementById("id_solution"),
                solutionInputHelpText: document.getElementById("id_solution_helptext"),
                fen,
                chessBoard,
                turnsCount: 0,
            }
            solutionState.solutionInput.value = ""
            setTimeout(solutionNextMove.bind(null, solutionState), 1000)
        })
    }

    function solutionNextMove(solutionState) {
        const { fen, chessBoard, previewIFrame, solutionInput, solutionInputHelpText } = solutionState
        const isHumanPlayerTurn = chessBoard.turn() === "w"
        const depth = isHumanPlayerTurn ? SOLUTION_PLAYER_TURN_DEPTH : SOLUTION_BOT_TURN_DEPTH
        // @link https://github.com/jhlywa/chess.js/tree/v0.13.4?tab=readme-ov-file#movemove--options-
        previewIFrame.contentWindow
            .__admin__playFromFEN(fen, depth, SOLUTION_BOT_ASSETS_DATA_HOLDER_ELEMENT_ID)
            .then((move) => {
                const moveStr = `${move[0]}${move[1]}`
                solutionInput.value += `${moveStr},`
                const moveResult = chessBoard.move(moveStr, { sloppy: true })
                if (!moveResult) {
                    window.alert(`Invalid move: ${moveStr}`)
                    return
                }
                if (isHumanPlayerTurn) {
                    solutionState.turnsCount++
                    solutionInputHelpText.innerText = `Turns: ${solutionState.turnsCount}`
                }
                if (chessBoard.in_checkmate()) {
                    window.alert(`'${chessBoard.turn()}' player is checkmate in ${solutionState.turnsCount} turns.`)
                    return
                }
                solutionState.fen = chessBoard.fen()

                setTimeout(solutionNextMove.bind(null, solutionState), 100)
            })
    }
})()
