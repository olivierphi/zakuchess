/** @type {import('tailwindcss').Config} */
module.exports = {
    content: ["./src/apps/*/jinja2/**/*.html"],
    theme: {
        fontFamily: {
            sans: ["OpenSans", "sans-serif"],
            pixel: ["PixelFont", "monospace"],
        },
        extend: {},
    },
    plugins: [],
}
