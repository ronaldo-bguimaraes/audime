import { test, expect } from "@playwright/test";
import { MOCK_TOKEN } from "./fixtures";

const MOCK_USER = { id_usuario: 1, nome: "Usuário Teste", email: "test@example.com" };
const MOCK_NOTAS = [
  { id: 1, empresa: "SDB COMERCIO DE ALIMENTOS LTDA", chave: "51260509477652008413651230002620731725445443", numero: "262073", serie: "1", emissao: "2025-01-15", valor_total: 157.80, items: [] },
  { id: 2, empresa: "MERCADINHO DO POVO LTDA", chave: "51260509477652008413651230002620731725445444", numero: "262074", serie: "1", emissao: "2025-01-16", valor_total: 89.50, items: [] },
  { id: 3, empresa: "PADARIA DO BAIRRO LTDA", chave: "51260509477652008413651230002620731725445445", numero: "262075", serie: "1", emissao: "2025-01-17", valor_total: 45.00, items: [] },
];

test("Login flow with valid credentials", async ({ page }) => {
  await page.route("**/v1/auth/code", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ status: "ok" }) });
  });
  await page.route("**/v1/auth/verify", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ status: "ok", access_token: MOCK_TOKEN, id_usuario: 1 }) });
  });
  await page.route("**/v1/auth/me", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(MOCK_USER) });
  });
  await page.route("**/v1/notas", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(MOCK_NOTAS) });
  });

  await page.goto("/login");
  await expect(page.locator("h1")).toContainText("audime");

  await page.fill("#login-email", "test@example.com");
  await page.click('button:has-text("Enviar código")');

  await page.waitForSelector("#login-code");
  await page.fill("#login-code", "123456");
  await page.click('button:has-text("Verificar")');

  await expect(page).toHaveURL(/\/dashboard/, { timeout: 10000 });
  await expect(page.locator("h1")).toContainText("Notas Fiscais");
});

test("Auth required to access dashboard", async ({ page }) => {
  await page.goto("/dashboard");
  await expect(page).toHaveURL(/\/login/);
});

test("Spam hint visible after sending code", async ({ page }) => {
  await page.route("**/v1/auth/code", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ status: "ok" }) });
  });

  await page.goto("/login");
  await page.fill("#login-email", "test@example.com");
  await page.click('button:has-text("Enviar código")');

  // Should show the spam hint
  await expect(page.locator("text=Não recebeu?")).toBeVisible();
  await expect(page.locator("text=Verifique a caixa de spam")).toBeVisible();
  // The word "spam" should be inside <strong>
  await expect(page.locator("strong:has-text('spam')")).toBeVisible();
});

test("Spam hint not visible on initial login screen", async ({ page }) => {
  await page.goto("/login");
  // Before sending code, spam hint should not be present
  await expect(page.locator("text=Não recebeu?")).not.toBeVisible();
});

test("Refresh on code screen restores state and shows code input", async ({ page }) => {
  await page.route("**/v1/auth/code", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ status: "ok" }) });
  });

  await page.goto("/login");
  await page.fill("#login-email", "test@refresh.com");
  await page.click('button:has-text("Enviar código")');

  // Wait for code input to appear
  await page.waitForSelector("#login-code");
  await expect(page.locator("#login-code")).toBeVisible();

  // Reload the page
  await page.reload();

  // After reload, code input should still be visible (restored from localStorage)
  await page.waitForSelector("#login-code");
  await expect(page.locator("#login-code")).toBeVisible();
  // Should show the email that was entered
  await expect(page.locator("text=test@refresh.com")).toBeVisible();
});
