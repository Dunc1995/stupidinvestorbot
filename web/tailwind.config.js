/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{svelte,html,js,ts}"],
  theme: {
    container: {
      center: true,
    },
  },
  plugins: [
    require("@tailwindcss/typography"),
    require('daisyui'),
  ],
  daisyui: {
    themes: ["nord"],
  },
}

