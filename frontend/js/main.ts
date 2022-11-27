import 'vite/modulepreload-polyfill';

function updateChessBoardsSize():void {
  const chessBoards = document.querySelectorAll<HTMLElement>(".chess-board")
  const availableHeight = window.innerHeight
  for (const board of Array.from(chessBoards)) {
    board.style.maxWidth = `${Math.round(availableHeight * 0.8)}px`
    const boardFirstCell = board.querySelector(".square")!
    const boardCellsWidth = boardFirstCell.getBoundingClientRect().width
    for (const square of Array.from(board.querySelectorAll<HTMLElement>(".square"))) {
      square.style.height = `${boardCellsWidth}px`
    }
  }
}

window.updateChessBoardsSize = updateChessBoardsSize


window.addEventListener("load", updateChessBoardsSize)
window.addEventListener("resize", updateChessBoardsSize)
