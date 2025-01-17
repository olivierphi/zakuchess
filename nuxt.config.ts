// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
    compatibilityDate: "2024-11-01",
    devtools: { enabled: true },
    imports: {
        // https://nuxt.com/docs/guide/concepts/auto-imports#disabling-auto-imports
        scan: false,
    },
    modules: [
        // https://nuxt.com/modules/tailwindcss
        "@nuxtjs/tailwindcss",
        // https://nuxt.com/modules/pinia
        "@pinia/nuxt",
    ],
    app: {
        head: {
            title: "ZakuChess ♞ - A daily chess challenge with pixel art units",
            charset: "utf-8",
            viewport: "width=device-width, initial-scale=1",
            bodyAttrs: {
                class: "bg-body-background",
            },
        },
    },
})
