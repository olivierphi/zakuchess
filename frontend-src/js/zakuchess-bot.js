// Let's code JavaScript like it's 2010! 🤘
(function () {
    
  if (!window.zakuchess) {
    window.zakuchess = {}
  }
  window.zakuchess.bot = {
    playFromFEN: playFromFEN,
  }  
  
  const BEST_MOVE_STOCKFISH_ANSWER = /^bestmove ([a-h][1-8])([a-h][1-8])/
  const wasmSupported = typeof WebAssembly === 'object' && WebAssembly.validate(Uint8Array.of(0x0, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00));
  
  let botInitializationDone = false
  let stockfish = null
  
  function initBot() {
      if (botInitializationDone) {
        return Promise.resolve()
      }  
      
      const chessBotDataHolder = document.getElementById("chess-bot-data")
      if (!chessBotDataHolder) {
        throw "no #chess-bot-data found!"
      }
      const chessBotData = JSON.parse(chessBotDataHolder.dataset.stockfishUrls)
      stockfish = new Worker(wasmSupported ? chessBotData["wasm"] : chessBotData["js"]);
      
      return new Promise((resolve, reject) => {
      function onStockFishMessage(e) {
        console.log(e.data);
        if (e.data !== "uciok") {
          return
        }
            botInitializationDone = true
            console.debug("resolve initBot()")
            stockfish.removeEventListener('message', onStockFishMessage);
            resolve()
          }
        stockfish.addEventListener('message', onStockFishMessage);
        stockfish.postMessage('uci');
        })
      }
  
  
  function playFromFEN (fen, depth, nextBotActionHtmlElementId) {
    initBot().then(function onBotInitialized() {
      console.log("onBotInitialized ; initialize with fen: ", fen)
      stockfish.postMessage("position fen " + fen)

      function onStockFishMessage(e) {
        console.log(e.data);
        const bestMoveAnswerMatch = BEST_MOVE_STOCKFISH_ANSWER.exec(e.data)
        if (!bestMoveAnswerMatch) {
          return
        }
        stockfish.removeEventListener('message', onStockFishMessage);
        console.log("bestMoveAnswerMatch: ", bestMoveAnswerMatch[2])
        const nextBotActionHtmlElement = document.getElementById(nextBotActionHtmlElementId)
        if (!nextBotActionHtmlElement) {
          throw "no #" + nextBotActionHtmlElementId + " found!"
        }
        const hxPostUrl = nextBotActionHtmlElement.dataset.hxPost.replace("${fromSquare}", bestMoveAnswerMatch[1]).replace("${toSquare}", bestMoveAnswerMatch[2])
        nextBotActionHtmlElement.dataset.hxPost = hxPostUrl
        htmx.process(nextBotActionHtmlElement)
        htmx.trigger(nextBotActionHtmlElement, "click")
      }

      stockfish.addEventListener('message', onStockFishMessage);
      stockfish.postMessage("go depth " + depth)
    })
  }
})();
