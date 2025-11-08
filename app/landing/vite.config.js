import { resolve } from "path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      input: {
        main: resolve(__dirname, "index.html"),
        linkedin: resolve(__dirname, "variant-linkedin/index.html"),
        social: resolve(__dirname, "variant-social/index.html"),
      },
    },
  },
});
