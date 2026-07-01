import { expect } from "@playwright/test";
import { test } from "./fixtures";

test("Dashboard shows list of notes", async ({ authenticatedPage }) => {
  await expect(authenticatedPage.locator("h1")).toContainText("Notas Fiscais");
  await expect(authenticatedPage.locator('a:has-text("Ver detalhes")')).toHaveCount(3);
  await expect(authenticatedPage.locator("h2")).toHaveCount(3);
});

test("Dashboard navigation to note details", async ({ authenticatedPage }) => {
  await authenticatedPage.locator('a:has-text("Ver detalhes")').first().click();
  await expect(authenticatedPage).toHaveURL(/\/notas\/\d+/);
  await expect(authenticatedPage.locator("h1")).toContainText("SDB COMERCIO DE ALIMENTOS LTDA");
  await expect(authenticatedPage.locator("table")).toBeVisible();
});

test("Note detail shows items correctly", async ({ authenticatedPage }) => {
  await authenticatedPage.goto("/notas/123");
  await expect(authenticatedPage.locator("h1")).toContainText("SDB COMERCIO DE ALIMENTOS LTDA");

  await authenticatedPage.waitForSelector("table tbody tr");
  const rows = await authenticatedPage.locator("table tbody tr").count();
  expect(rows).toBeGreaterThanOrEqual(5);

  const firstRow = authenticatedPage.locator("table tbody tr").first();
  await expect(firstRow.locator("td").first()).toContainText("MOLHO TOM FUGINI 300G");
});

test("Responsive behavior on mobile", async ({ authenticatedPage }) => {
  await authenticatedPage.setViewportSize({ width: 375, height: 667 });
  await expect(authenticatedPage.locator("h1")).toContainText("Notas Fiscais");
  await expect(authenticatedPage.locator('a:has-text("Ver detalhes")')).toHaveCount(3);

  await authenticatedPage.locator('a:has-text("Ver detalhes")').first().click();
  await expect(authenticatedPage).toHaveURL(/\/notas\/\d+/);
  await expect(authenticatedPage.locator("table")).toBeVisible();
});
