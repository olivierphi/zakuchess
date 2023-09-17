;(function () {
    const gameUpdateCommandPattern = /^([a-h][1-8]):([pnbrqkx])!\s*$/i

    function init() {
        const adminPreviewUrl = document.getElementById("admin-preview-url-holder").innerText

        const previewIFrame = document.getElementById("preview-iframe")

        const fenInput = document.getElementById("id_fen")
        const botFirstMoveInput = document.getElementById("id_bot_first_move")
        const introTurnSpeechSquareInput = document.getElementById("id_intro_turn_speech_square")

        const gameUpdateInput = document.getElementById("id_update_game")

        function updatePreview(gameUpdate) {
            previewIFrame.src =
                adminPreviewUrl +
                "?" +
                new URLSearchParams({
                    fen: fenInput.value,
                    bot_first_move: botFirstMoveInput.value,
                    intro_turn_speech_square: introTurnSpeechSquareInput.value,
                    game_update: gameUpdate || "",
                }).toString()
        }

        function onChessBoardFieldKeyUp(event) {
            updatePreview(null)
        }

        fenInput.addEventListener("keyup", onChessBoardFieldKeyUp)
        botFirstMoveInput.addEventListener("keyup", onChessBoardFieldKeyUp)
        introTurnSpeechSquareInput.addEventListener("keyup", onChessBoardFieldKeyUp)

        function onGameUpdateInputKeyUp() {
            const match = gameUpdateCommandPattern.exec(gameUpdateInput.value)
            if (!match) {
                return
            }
            const square = match[1]
            const piece = match[2]
            console.log(`Updating ${square} to ${piece}`)
            gameUpdateInput.value = ""
            updatePreview(`${square}:${piece}`)
        }

        gameUpdateInput.addEventListener("keyup", onGameUpdateInputKeyUp)

        setTimeout(updatePreview, 100)
    }

    setTimeout(init, 1000)
})()
