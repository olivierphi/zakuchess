import 'vite/modulepreload-polyfill';

function updateChessBoardsSize():void {
  const availableHeight = window.innerHeight
  const chessBoardContainers = document.querySelectorAll<HTMLElement>(".chess-board-container")
  for (const boardContainer of Array.from(chessBoardContainers)) {
    boardContainer.style.maxWidth = `${Math.round(availableHeight * 0.8)}px`
    const boardContainerWidth = boardContainer.getBoundingClientRect().width
    boardContainer.style.height = boardContainerWidth
  }
}

function startAiPiloting():void {
  setInterval(triggerAiMoveIfNeeded, 1000)
}

let lastTriggerTime = 0
function triggerAiMoveIfNeeded():void {
  const chessBoardContainer = document.querySelector<HTMLElement>(".chess-board-container")
  if (!chessBoardContainer) {
    return
  }
  const now = (new Date()).getTime()
  if (now - lastTriggerTime < 2000) {
    return
  }
  const activePlayer = chessBoardContainer.dataset.activePlayer
  if (activePlayer === "b") {
    Unicorn.call("chess.chess-board", "let_ai_play_next_move")
    lastTriggerTime = now
  }
  
}

window.updateChessBoardsSize = updateChessBoardsSize


window.addEventListener("load", updateChessBoardsSize)
window.addEventListener("load", startAiPiloting)
window.addEventListener("resize", updateChessBoardsSize)
