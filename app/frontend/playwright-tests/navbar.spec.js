const { test, expect } = require("@playwright/test");

const username = `testuser_${Date.now()}`;
const userEmail = `testuser_${Date.now()}@example.com`;
const userPassword = "password123";

test.beforeAll(async ({ browser }) => {
  const page = await browser.newPage();
  await page.goto("/register");
  await page.locator("#username").fill(username);
  await page.locator("#email").fill(userEmail);
  await page.locator("#password").fill(userPassword);
  await page.getByRole("button", { name: "Register" }).click();
  await page.waitForURL("/marketplace/dashboard");
  await page.close();
});

test.describe("Navbar Functionality for Authenticated User", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/login");
    await page.locator("#username").fill(username);
    await page.locator("#password").fill(userPassword);
    await page.getByRole("button", { name: "Sign In" }).click();
    await expect(page).toHaveURL("/marketplace/dashboard");
  });

  test("should navigate to Dashboard", async ({ page }) => {
    await page.click("nav >> text=Dashboard");
    await expect(page).toHaveURL("/marketplace/dashboard");
    await expect(page.locator('h1:has-text("Dashboard")')).toBeVisible();
  });

  test("should navigate to My Ads", async ({ page }) => {
    await page.click("nav >> text=My Ads");
    await expect(page).toHaveURL("/marketplace/my-ads");
    await expect(page.locator('h1:has-text("My Ads")')).toBeVisible();
  });

  test("should navigate to Create Ad", async ({ page }) => {
    await page.click("nav >> text=Create Ad");
    await expect(page).toHaveURL("/marketplace/create-ad");
    await expect(page.locator('h1:has-text("Create a New Ad")')).toBeVisible();
  });

  test("should navigate to Platforms", async ({ page }) => {
    await page.click("nav >> text=Platforms");
    await expect(page).toHaveURL("/marketplace/platforms");
    await expect(page.locator('h1:has-text("Manage Platforms")')).toBeVisible();
  });

  test("should navigate to Analytics", async ({ page }) => {
    await page.click("nav >> text=Analytics");
    await expect(page).toHaveURL("/marketplace/analytics");
    await expect(page.locator('h1:has-text("Analytics")')).toBeVisible();
  });
});
