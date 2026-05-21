import path from "node:path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
// Backend FastAPI: domyślnie http://127.0.0.1:8770 (CONCIERGE_PORT).
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: { "@": path.resolve(__dirname, "./src") },
    },
    server: {
        port: 5173,
        proxy: {
            "/api": "http://127.0.0.1:8770",
            "/health": "http://127.0.0.1:8770",
        },
    },
});
