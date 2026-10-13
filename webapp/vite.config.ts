import path from "node:path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    allowedHosts: ["goliath"],
    port: 11240,
    strictPort: true,
    host: "127.0.0.1",
    proxy: {
      "/api": { target: "http://127.0.0.1:11239", changeOrigin: true },
      "/library": { target: "http://127.0.0.1:11239", changeOrigin: true },
      "/telemetry": { target: "http://127.0.0.1:11239", changeOrigin: true },
      "/health": { target: "http://127.0.0.1:11239", changeOrigin: true },
      "/chat": { target: "http://127.0.0.1:11239", changeOrigin: true },
      "/launch": { target: "http://127.0.0.1:11239", changeOrigin: true },
    },
  },
});
