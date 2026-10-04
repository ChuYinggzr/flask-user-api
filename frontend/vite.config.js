import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      "/auth": "http://127.0.0.1:5000",
      "/users": "http://127.0.0.1:5000",
      "/api": "http://127.0.0.1:5000",
    },
  },
  build: {
    outDir: "dist",
    emptyOutDir: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vue: ["vue", "vue-router", "axios"],
          element: ["element-plus", "@element-plus/icons-vue"],
          charts: ["echarts"],
        },
      },
    },
  },
});
