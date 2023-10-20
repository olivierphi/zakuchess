import * as htmx from "htmx.org"

// @ts-ignore
window.htmx = htmx

// We have to wait for the htmx core to be loaded *and* set as a global var
// before we can load the extensions:
// @ts-ignore
import("htmx.org/dist/ext/class-tools.js").catch((e) => console.error(e))
