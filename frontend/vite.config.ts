import { createHash } from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { defineConfig, type Plugin } from "vitest/config";

const root = fileURLToPath(new URL(".", import.meta.url));
const version = process.env.npm_package_version ?? "0.6.0";
const builtAt = new Date().toISOString();
const buildId = createHash("sha256").update(`${version}:${builtAt}`).digest("hex").slice(0, 16);

function writeBuildManifest(): Plugin {
  let outDir = path.join(root, "..", "natalia", "web");
  return {
    name: "natalia-build-manifest",
    configResolved(config) {
      outDir = path.resolve(config.build.outDir);
    },
    transformIndexHtml(html) {
      return html.replace(
        "<head>",
        `<head>\n    <meta name="natalia-build" content="${buildId}" />`,
      );
    },
    closeBundle() {
      fs.mkdirSync(outDir, { recursive: true });
      fs.writeFileSync(
        path.join(outDir, "build.json"),
        JSON.stringify({ version, builtAt, buildId }, null, 2),
        "utf8",
      );
    },
  };
}

export default defineConfig({
  plugins: [react(), tailwindcss(), writeBuildManifest()],
  resolve: {
    alias: { "@": path.join(root, "src") },
  },
  define: {
    __APP_VERSION__: JSON.stringify(version),
    __BUILD_TIME__: JSON.stringify(builtAt),
    __BUILD_ID__: JSON.stringify(buildId),
  },
  build: {
    outDir: path.join(root, "..", "natalia", "web"),
    emptyOutDir: true,
    sourcemap: false,
    assetsDir: "assets",
  },
  server: {
    host: "127.0.0.1",
    port: 5173,
    proxy: {
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: false },
      "/health": { target: "http://127.0.0.1:8000", changeOrigin: false },
      "/metrics": { target: "http://127.0.0.1:8000", changeOrigin: false },
      "/docs": { target: "http://127.0.0.1:8000", changeOrigin: false },
      "/redoc": { target: "http://127.0.0.1:8000", changeOrigin: false },
      "/openapi.json": { target: "http://127.0.0.1:8000", changeOrigin: false },
    },
  },
  test: {
    environment: "jsdom",
    globals: false,
    setupFiles: ["./src/test/setup.ts"],
    include: ["src/**/*.test.ts", "src/**/*.test.tsx"],
  },
});
