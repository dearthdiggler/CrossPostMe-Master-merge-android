const { test, expect } = require("@playwright/test");

test.describe("Authentication Lifecycle", () => {
  const username = `testuser_${Date.now()}`;
  const email = `testuser_${Date.now()}@example.com`;
  const password = "password123";

  test("A new user can register, log out, and log back in", async ({
    page,
  }) => {
    await page.goto("/register");

    // Fill in registration form
    await page.locator("#username").fill(username);
    await page.locator("#email").fill(email);
    await page.locator("#password").fill(password);
    await page.getByRole("button", { name: "Register" }).click();

    await expect(page).toHaveURL("/marketplace/dashboard", { timeout: 10000 });

    // Click the logout button using aria-label
    await page.getByRole("button", { name: "Log Out" }).click();

    await expect(page).toHaveURL("/", { timeout: 5000 });

    await page.locator("#username").fill(username);
    await page.locator("#password").fill(password);
    await page.getByRole("button", { name: "Sign In" }).click();

    await expect(page).toHaveURL("/marketplace/dashboard", { timeout: 10000 });
  });

  test("User receives an error for invalid login", async ({ page }) => {
    await page.goto("/login");

    await page.locator("#username").fill("wronguser");
    await page.locator("#password").fill("wrongpassword");
    await page.getByRole("button", { name: "Sign In" }).click();

    const errorMessage = page.locator("text=/Invalid username or password/i");
    await expect(errorMessage).toBeVisible();
    await expect(page).toHaveURL("/login");
  });
});
