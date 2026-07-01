import { test } from "@playwright/test";
import { authFixture } from "./fixtures";

test.use(authFixture);

test("Dashboard shows list of notes", async ({ authenticatedPage }) => {
  // Verify dashboard is loaded
  await expect(authenticatedPage.locator("[data-testid=dashboard-title]")).toBeVisible();
  
  // Check for note cards/items
  await expect(authenticatedPage.locator("[data-testid=nota-card]")).toHaveCount(3);
  
  // Check for summary information
  await expect(authenticatedPage.locator("[data-testid=total-notas]")).toContainText("3");
});

test("Dashboard navigation to note details", async ({ authenticatedPage }) => {
  // Click on first note card
  await authenticatedPage.locator("[data-testid=nota-card]").first().click();
  
  // Wait for note details page to load
  await expect(authenticatedPage).toHaveURL(/\/nota\/\d+/);
  
  // Verify note details are displayed
  await expect(authenticatedPage.locator("[data-testid=nota-detalhe-titulo]")).toBeVisible();
  await expect(authenticatedPage.locator("[data-testid=nota-itens-table]")).toBeVisible();
});

test("Note detail shows items correctly", async ({ authenticatedPage }) => {
  // Navigate to note details page
  await authenticatedPage.goto("/nota/123");
  
  // Verify items are displayed
  await expect(authenticatedPage.locator("[data-testid=nota-item-row]")).toHaveCount(5);
  
  // Check for specific item data
  await expect(authenticatedPage.locator("[data-testid=item-codigo-1]")).toContainText("7897517206086");
  await expect(authenticatedPage.locator("[data-testid=item-descricao-1]")).toContainText("MOLHO TOM FUGINI 300G");
});

test("Responsive behavior on mobile", async ({ authenticatedPage }) => {
  // Set viewport to mobile size
  await authenticatedPage.setViewportSize({ width: 375, height: 667 });
  
  // Check dashboard layout is responsive
  await expect(authenticatedPage.locator("[data-testid=nota-card]")).toHaveCount(3);
  
  // Navigate to note details
  await authenticatedPage.locator("[data-testid=nota-card]").first().click();
  
  // Check if note details adapt to mobile
  await expect(authenticatedPage).toHaveURL(/\/nota\/\d+/);
});
