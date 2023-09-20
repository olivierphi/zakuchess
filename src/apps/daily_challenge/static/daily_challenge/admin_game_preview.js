;(function () {
    const gameUpdateCommandPatterns = [
        /^[a-h][1-8]:add:[pnbrqkx]!\s*$/i, // "add" command
        /^[a-h][1-8]:rm!\s*$/i, // "remove" command
        /^[a-h][1-8]:mv:[a-h][1-8]!\s*$/i, // "move" command
    ]

    const gameUpdateCommandResetPattern = /^.*!\s*$/i

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

    setTimeout(init, 100)
})()
