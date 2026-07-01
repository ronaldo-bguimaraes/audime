import { test } from "@playwright/test";
import { authFixture } from "./fixtures";

test.use(authFixture);

test("Login flow with valid credentials", async ({ authenticatedPage }) => {
  // Authenticated via fixture, verify dashboard
  await expect(authenticatedPage.locator("[data-testid=dashboard-title]")).toBeVisible();
  await expect(authenticatedPage).toHaveURL(/\/dashboard/);
});

test("Auth required to access dashboard", async ({ page }) => {
  // Should redirect to login without auth
  await page.goto("/dashboard");
  await expect(page).toHaveURL(/\/login/);
});
