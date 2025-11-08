// playwright.config.js
const { defineConfig, devices } = require("@playwright/test");
const path = require("path");

// Read from .env file if dotenv is available
try {
  require("dotenv").config({ path: path.resolve(__dirname, ".env") });
} catch (e) {
  // dotenv not required for Playwright
}

module.exports = defineConfig({
  testDir: "./playwright-tests",

  // Configure projects for major browsers
  projects: [
    {
      name: "chromium",
      use: {
        browserName: "chromium",
        // The base URL is automatically passed to all tests
        baseURL: `http://localhost:${process.env.VITE_PORT || 3000}`,
      },
    },
  ],

  // Reporter to use
  reporter: "html",

  // Shared settings for all the projects
  use: {
    // Base URL to use in actions like `await page.goto('/')`
    baseURL: `http://localhost:${process.env.VITE_PORT || 3000}`,

    // Collect trace when retrying the failed test
    trace: "on-first-retry",
  },

  // Opt out of parallel tests to simplify debugging.
  workers: 1,

  // Configure a web server to start automatically.
  // In CI, we start it. Locally, start it manually in another terminal.
  webServer: process.env.CI ? {
    command: "yarn start",
    url: `http://localhost:${process.env.VITE_PORT || 3000}`,
    reuseExistingServer: false,
    timeout: 120 * 1000,
  } : undefined,
});
