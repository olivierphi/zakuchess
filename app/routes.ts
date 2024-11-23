import type { DefineRouteFunction } from "@remix-run/dev/dist/config/routes"

// https://remix.run/docs/en/main/discussion/routes#manual-route-configuration

export const routesDefinition = (route: DefineRouteFunction) => {
    route("/", "pages/Homepage.tsx", { index: true })
}
