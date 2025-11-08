const { test, expect } = require("@playwright/test");

test("login page loads and shows form", async ({ page }) => {
  await page.goto("/login");
  await expect(page.locator("form")).toBeVisible();
  await expect(page.locator("#username")).toBeVisible();
  await expect(page.locator("#password")).toBeVisible();
});

test("login with invalid credentials shows error", async ({ page }) => {
  await page.goto("/login");
  await page.locator("#username").fill("invaliduser");
  await page.locator("#password").fill("wrongpassword");
  await page.getByRole("button", { name: "Sign In" }).click();
  await expect(page.locator(".error")).toBeVisible();
});
