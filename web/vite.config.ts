import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": "http://127.0.0.1:8000",
      "/health": "http://127.0.0.1:8000",
      "/analyze": "http://127.0.0.1:8000",
      "/generic": "http://127.0.0.1:8000",
      "/twin": "http://127.0.0.1:8000",
      "/graph": "http://127.0.0.1:8000",
      "/cases": "http://127.0.0.1:8000",
    },
  },
});
