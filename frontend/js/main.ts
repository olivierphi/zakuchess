import 'vite/modulepreload-polyfill';

function updateChessBoardsSize():void {
  const availableHeight = window.innerHeight
  const chessBoardContainers = document.querySelectorAll<HTMLElement>(".chess-board-container")
  for (const boardContainer of Array.from(chessBoardContainers)) {
    boardContainer.style.maxWidth = `${Math.round(availableHeight * 0.8)}px`
    const boardContainerWidth = boardContainer.getBoundingClientRect().width
    boardContainer.style.height = boardContainerWidth
    // const boardFirstCell = boardContainer.querySelector(".square")!
    // const boardCellsWidth = boardFirstCell.getBoundingClientRect().width
    // for (const square of Array.from(boardContainer.querySelectorAll<HTMLElement>(".square"))) {
    //   square.style.height = `${boardCellsWidth}px`
    // }
  }
}

window.updateChessBoardsSize = updateChessBoardsSize


window.addEventListener("load", updateChessBoardsSize)
window.addEventListener("resize", updateChessBoardsSize)
