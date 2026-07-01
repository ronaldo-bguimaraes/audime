import { test } from "@playwright/test";
import { authFixture, nfcDataFixture } from "./fixtures";

test.use(authFixture);
test.use(nfcDataFixture);

test("NFC upload form is accessible", async ({ nfcPage }) => {
  // Authenticated via authFixture, NFC data fixture ensures we have the page
  await expect(nfcPage.locator("[data-testid=upload-form]")).toBeVisible();
});

test("Upload form validates URL input", async ({ nfcPage }) => {
  const urlInput = nfcPage.locator("[data-testid=url-input]");
  const submitButton = nfcPage.locator("[data-testid=submit-url-button]");
  
  await expect(urlInput).toBeVisible();
  await expect(submitButton).toBeEnabled();
});

test("NFC upload with valid URL shows preview", async ({ nfcPage }) => {
  const urlInput = nfcPage.locator("[data-testid=url-input]");
  const submitButton = nfcPage.locator("[data-testid=submit-url-button]");
  const previewPanel = nfcPage.locator("[data-testid=preview-panel]");
  
  // Fill the URL input
  await urlInput.fill("http://www.sefaz.mt.gov.br/nfce/consultanfce?p=51260509477652008413651230002620731725445443|2|1|1|8D8C7A538544E4EF09D4749A4D5E4C70DA94863C");
  
  // Submit the form
  await submitButton.click();
  
  // Wait for preview to appear
  await expect(previewPanel).toBeVisible({ timeout: 10000 });
  await expect(previewPanel.locator("[data-testid=preview-content]")).toContainText("SDB COMERCIO DE ALIMENTOS LTDA");
});

test("Show error for invalid URL", async ({ nfcPage }) => {
  const urlInput = nfcPage.locator("[data-testid=url-input]");
  const submitButton = nfcPage.locator("[data-testid=submit-url-button]");
  const errorMessage = nfcPage.locator("[data-testid=error-message]");
  
  await urlInput.fill("invalid-url");
  await submitButton.click();
  
  await expect(errorMessage).toBeVisible();
  await expect(errorMessage).toContainText("URL inválida");
});
