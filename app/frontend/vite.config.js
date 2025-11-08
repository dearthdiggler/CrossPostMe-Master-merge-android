import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { fileURLToPath, URL } from "node:url";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  // Load env file based on the mode
  const env = loadEnv(mode, process.cwd(), "");

  return {
    plugins: [react()],
    resolve: {
      alias: {
        "@": fileURLToPath(new URL("./src", import.meta.url)),
      },
    },
    // This 'define' block is the critical fix.
    // It makes 'process.env' available in your browser code.
    define: {
      "process.env": env,
    },
    server: {
      port: parseInt(env.VITE_PORT) || 3000,
      host: "0.0.0.0",
      strictPort: true,
      proxy: {
        "/api": {
          target: env.VITE_BACKEND_URL || "http://localhost:8000",
          changeOrigin: true,
        },
      },
    },
    build: {
      outDir: "build",
      sourcemap: true,
    },
  };
});
