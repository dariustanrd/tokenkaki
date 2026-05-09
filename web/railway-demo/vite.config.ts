import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const gatewayProxyTarget = process.env.TOKENKAKI_GATEWAY_PROXY_TARGET ?? "http://127.0.0.1:18080";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: "127.0.0.1",
    proxy: {
      "/api": {
        target: gatewayProxyTarget,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, "")
      }
    }
  }
});
