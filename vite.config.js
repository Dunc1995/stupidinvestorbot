import { defineConfig } from "rollup"

// vite.config.js
module.exports = defineConfig({
    build: {
        rollupOptions: {
            input: {
                a: 'web/src/app.js'
            },
            output: {
                dir: './web/static',
                entryFileNames: 'bundle.js'
            }
        }
    }
})