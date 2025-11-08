const { test, expect } = require("@playwright/test");

test("form submission shows success", async ({ page }) => {
  await page.goto("/contact");
  await page.fill('input[name="name"]', "Test User");
  await page.fill('input[name="email"]', "test@example.com");
  await page.fill('textarea[name="message"]', "Hello!");
  await page.click('button[type="submit"]');
  await expect(page.locator(".success-message")).toBeVisible();
});

test("form submission with missing fields shows error", async ({ page }) => {
  await page.goto("/contact");
  await page.click('button[type="submit"]');
  await expect(page.locator(".error")).toBeVisible();
});
