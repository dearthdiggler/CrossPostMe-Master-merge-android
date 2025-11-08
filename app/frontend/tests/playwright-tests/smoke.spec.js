import { test, expect } from "@playwright/test";

test("homepage loads and shows login", async ({ page }) => {
  await page.goto("http://localhost:3000");
  await expect(page.locator("text=Login")).toBeVisible();
});

test("can navigate to signup", async ({ page }) => {
  await page.goto("http://localhost:3000");
  await page.click("text=Sign Up");
  await expect(page.locator("text=Create Account")).toBeVisible();
});
