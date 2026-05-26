import path from "node:path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Backend FastAPI: domyslnie http://127.0.0.1:8766 (config.web_port).
// Vite proxy przekierowuje /api/* i /health do backendu w trybie dev.
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 5173,
    proxy: {
      "/api": "http://127.0.0.1:8766",
      "/health": "http://127.0.0.1:8766",
    },
  },
});
