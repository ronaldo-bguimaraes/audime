import { expect } from "@playwright/test";
import { test } from "./fixtures";

test("NFC upload form is accessible", async ({ authenticatedPage }) => {
  await authenticatedPage.goto("/extrair");
  await expect(authenticatedPage.locator("h1")).toContainText("Nova Extração");
  await expect(authenticatedPage.locator("#extracao-url")).toBeVisible();
  await expect(authenticatedPage.locator('button:has-text("Extrair")')).toBeVisible();
});

test("Upload form validates URL input", async ({ authenticatedPage }) => {
  await authenticatedPage.goto("/extrair");
  const urlInput = authenticatedPage.locator("#extracao-url");
  const submitButton = authenticatedPage.locator('button:has-text("Extrair")');

  await expect(urlInput).toBeVisible();
  await expect(submitButton).toBeVisible();
  await expect(submitButton).toBeDisabled();

  await urlInput.fill("https://www.sefaz.mt.gov.br/nfce/consultanfce?p=test");
  await expect(submitButton).toBeEnabled();
});

test("NFC upload with valid URL shows success", async ({ authenticatedPage }) => {
  await authenticatedPage.goto("/extrair");
  const urlInput = authenticatedPage.locator("#extracao-url");

  await urlInput.fill("https://www.sefaz.mt.gov.br/nfce/consultanfce?p=51260509477652008413651230002620731725445443|2|1|1|8D8C7A538544E4EF09D4749A4D5E4C70DA94863C");
  await authenticatedPage.locator('button:has-text("Extrair")').click();

  await expect(authenticatedPage.locator('[role="status"]')).toContainText("Extração iniciada com sucesso!", { timeout: 10000 });
});

test("Show error for invalid URL", async ({ authenticatedPage }) => {
  await authenticatedPage.route("**/v1/extracoes", async (route) => {
    await route.fulfill({ status: 400, contentType: "application/json", body: JSON.stringify({ detail: "URL inválida" }) });
  });

  await authenticatedPage.goto("/extrair");
  const urlInput = authenticatedPage.locator("#extracao-url");

  await urlInput.fill("https://invalid.url");
  await authenticatedPage.locator('button:has-text("Extrair")').click();

  await expect(authenticatedPage.locator('[role="alert"]')).toBeVisible({ timeout: 10000 });
  await expect(authenticatedPage.locator('[role="alert"]')).not.toBeEmpty();
});
