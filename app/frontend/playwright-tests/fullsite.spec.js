const { test, expect } = require("@playwright/test");

test.describe("Master Diagnostic Test", () => {
  test("captures all startup errors on the login page", async ({ page }) => {
    // Listen for uncaught exceptions
    page.on("pageerror", (exception) => {
      console.log(`\n--- BROWSER EXCEPTION ---`);
      console.log(`Uncaught exception: "${exception}"`);
      console.log(`-------------------------\n`);
    });

    // Listen for console error messages
    page.on("console", (msg) => {
      if (msg.type() === "error") {
        console.log(`\n--- BROWSER CONSOLE ERROR ---`);
        console.log(`Error text: "${msg.text()}"`);
        console.log(`-----------------------------\n`);
      }
    });

    // Navigate and wait for the test to fail.
    // This gives the listeners time to capture any errors.
    try {
      await page.goto("/login");
      // The test will fail here, which is expected.
      await expect(page.locator("form")).toBeVisible({ timeout: 10000 });
    } catch (error) {
      console.log("\nTest failed as expected. See browser error output above.");
      console.log("\n--- FULL PAGE HTML ---");
      console.log(await page.content());
      console.log("----------------------\n");
      throw error;
    }
  });
});
