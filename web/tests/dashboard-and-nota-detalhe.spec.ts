import { expect } from "@playwright/test";
import { test, MOCK_TOKEN } from "./fixtures";

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

test("Empty dashboard shows friendly message with extraction link", async ({ browser }) => {
  const context = await browser.newContext();
  const page = await context.newPage();

  await page.route("**/v1/auth/me", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ id_usuario: 1, nome: "Test", email: "test@example.com" }) });
  });
  await page.route("**/v1/dashboard/notas", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify([]) });
  });

  await page.goto("/");
  await page.evaluate((token) => {
    localStorage.setItem("audime_token", token);
  }, MOCK_TOKEN);

  await page.goto("/dashboard");
  await expect(page.locator("h1")).toContainText("Notas Fiscais", { timeout: 10000 });

  // Should show empty state message
  await expect(page.locator("text=Nenhuma nota encontrada")).toBeVisible();
  // Should have a link to /extrair
  const extrairLink = page.locator('a[href="/extrair"]');
  await expect(extrairLink).toBeVisible();
  // Click the link to verify it works
  await extrairLink.click();
  await expect(page).toHaveURL(/\/extrair/);

  await context.close();
});
