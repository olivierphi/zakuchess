import * as htmx from "htmx.org/dist/htmx.js"

// @ts-ignore
window.htmx = htmx

// import "htmx.org/dist/ext/remove-me.js"
import("htmx.org/dist/ext/class-tools.js").catch(console.error)

// We want the page to be refreshed when the user comes back to it after a long time.
// This is to make sure that if they come back the day after they won, they see the
// new challenge right away without having to interact with the game first.

const DOCUMENT_WAS_INVISIBLE_TRIGGERS_PAGE_REFRESH_THRESHOLD = 60 * 60 * 1_000 // 1 hour

let lastTimeDocumentWasVisible = Date.now()

document.addEventListener("visibilitychange", onDocumentVisibilityChange)

function onDocumentVisibilityChange() {
    if (document.hidden) {
        // We're only interested in the "visible" state here
        return
    }

    const now = Date.now()
    const timeSinceLastVisibility = now - lastTimeDocumentWasVisible
    if (timeSinceLastVisibility > DOCUMENT_WAS_INVISIBLE_TRIGGERS_PAGE_REFRESH_THRESHOLD) {
        // Let's refresh the page to make sure the user sees the new challenge!
        // (even though we're not sure if there's a new challenge yet - that could be
        // achieved by sending that data as a HTML attribute in the response of the server,
        // but we haven't implemented such a thing yet)
        console.info("Reloading the page to make sure the user sees the new challenge, if there's one")
        location.reload()
    } else {
        // Right, let's just reset the last time the document was visible
        lastTimeDocumentWasVisible = Date.now()
    }
}
