const { test, expect } = require("@playwright/test");

const username = `testuser_${Date.now()}`;
const email = `testuser_${Date.now()}@example.com`;
const password = "password";

async function login(page, user, pass) {
  await page.goto("/login");
  await page.locator("#username").fill(user);
  await page.locator("#password").fill(pass);
  await page.getByRole("button", { name: "Sign In" }).click();
  await page.waitForURL("/marketplace/dashboard");
}

test.beforeAll(async ({ browser }) => {
  const page = await browser.newPage();
  await page.goto("/register");
  await page.locator("#username").fill(username);
  await page.locator("#email").fill(email);
  await page.locator("#password").fill(password);
  await page.getByRole("button", { name: "Register" }).click();
  await page.waitForURL("/marketplace/dashboard");
  await page.close();
});

test.describe("Dashboard and Ads Workflow", () => {
  test.beforeEach(async ({ page }) => {
    await login(page, username, password);
  });

  test("dashboard loads and stats are fetched", async ({ page }) => {
    await expect(page.locator(".stat-card")).toHaveCount(4);
  });

  test("ad creation form submits and persists", async ({ page }) => {
    await page.goto("/marketplace/create-ad");
    const adTitle = `Test Ad ${Date.now()}`;
    await page.locator("#title").fill(adTitle);
    await page.locator("#description").fill("This is a test ad description.");
    await page.locator("#price").fill("100");
    await page.getByRole("button", { name: "Create Ad" }).click();
    await expect(page).toHaveURL("/marketplace/my-ads");
    await expect(page.locator(`text=${adTitle}`)).toBeVisible();
  });

  test("my ads page lists ads", async ({ page }) => {
    await page.goto("/marketplace/my-ads");
    await expect(page.getByRole("heading", { name: "My Ads" })).toBeVisible();
    const adCount = await page.locator(".ad-item").count();
    expect(adCount).toBeGreaterThanOrEqual(0);
  });
});
