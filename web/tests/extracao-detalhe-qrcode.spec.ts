import { expect, type Page } from "@playwright/test";
import { test } from "./fixtures";

const EXTRACAO_URL =
  "https://www.sefaz.mt.gov.br/nfce/consultanfce?p=51260509477652008413651230002620731725445443|2|1|1|8D8C7A538544E4EF09D4749A4D5E4C70DA94863C";

/**
 * Locate the infoRow div that contains the "URL" label.
 * This is the row where the QR Code (or fallback) and action buttons will be rendered.
 */
function urlRow(page: Page) {
  return page.locator("div").filter({ has: page.getByText("URL", { exact: true }) }).first();
}

test.describe("Extração Detalhe — QR Code", () => {
  // ---------------------------------------------------------------------------
  // CAT-QR-002: QR code is displayed when URL is present
  // ---------------------------------------------------------------------------
  test("CAT-QR-002: QR code is displayed when URL is present", async ({ authenticatedPage }) => {
    await authenticatedPage.goto("/extracao/1");
    await expect(authenticatedPage.locator("h1")).toContainText("Extração #1");

    const row = urlRow(authenticatedPage);

    // An <img> element with a data:image/ src must exist inside the URL row
    const qrImg = row.locator("img");
    await expect(qrImg).toBeVisible({ timeout: 10000 });
    const src = await qrImg.getAttribute("src");
    expect(src).toMatch(/^data:image\//);

    // The raw URL must NOT be visible as text inside the URL row
    await expect(row).not.toContainText(EXTRACAO_URL);
  });

  // ---------------------------------------------------------------------------
  // CAT-QR-003: QR code is absent and fallback shown when URL is null
  // ---------------------------------------------------------------------------
  test("CAT-QR-003: QR code is absent and fallback shown when URL is null", async ({ authenticatedPage }) => {
    await authenticatedPage.goto("/extracao/2");
    await expect(authenticatedPage.locator("h1")).toContainText("Extração #2");

    const row = urlRow(authenticatedPage);

    // No <img> should be rendered inside the URL row
    await expect(row.locator("img")).toHaveCount(0);

    // A textual fallback must be visible ("—" or "Sem URL")
    await expect(row).toContainText("—");
  });

  // ---------------------------------------------------------------------------
  // CAT-QR-004: "Abrir" button opens URL in a new tab
  // ---------------------------------------------------------------------------
  test('CAT-QR-004: "Abrir" button opens URL in a new tab', async ({ authenticatedPage }) => {
    await authenticatedPage.goto("/extracao/1");
    await expect(authenticatedPage.locator("h1")).toContainText("Extração #1");

    // Listen for new page before clicking
    const pagePromise = authenticatedPage.context().waitForEvent("page");

    await urlRow(authenticatedPage).getByText("Abrir").click();

    const newPage = await pagePromise;
    await newPage.waitForLoadState();
    expect(newPage.url()).toBe(EXTRACAO_URL);
    await newPage.close();
  });

  // ---------------------------------------------------------------------------
  // CAT-QR-005: "Copiar" button copies URL to clipboard
  // ---------------------------------------------------------------------------
  test('CAT-QR-005: "Copiar" button copies URL to clipboard', async ({ authenticatedPage }) => {
    // Grant clipboard permissions for this test
    await authenticatedPage.context().grantPermissions(["clipboard-read", "clipboard-write"]);

    await authenticatedPage.goto("/extracao/1");
    await expect(authenticatedPage.locator("h1")).toContainText("Extração #1");

    await urlRow(authenticatedPage).getByText("Copiar").click();

    const clipboardText = await authenticatedPage.evaluate(() =>
      navigator.clipboard.readText(),
    );
    expect(clipboardText).toBe(EXTRACAO_URL);
  });

  // ---------------------------------------------------------------------------
  // CAT-QR-006: No action buttons when URL is null
  // ---------------------------------------------------------------------------
  test("CAT-QR-006: No action buttons when URL is null", async ({ authenticatedPage }) => {
    await authenticatedPage.goto("/extracao/2");
    await expect(authenticatedPage.locator("h1")).toContainText("Extração #2");

    const row = urlRow(authenticatedPage);

    // "Abrir" and "Copiar" must NOT be present when URL is null
    await expect(row.getByText("Abrir")).toHaveCount(0);
    await expect(row.getByText("Copiar")).toHaveCount(0);
  });

  // ---------------------------------------------------------------------------
  // CAT-QR-011: "Abrir" link has rel="noopener noreferrer" when using <a>
  // ---------------------------------------------------------------------------
  test('CAT-QR-011: "Abrir" link has rel="noopener noreferrer"', async ({ authenticatedPage }) => {
    await authenticatedPage.goto("/extracao/1");
    await expect(authenticatedPage.locator("h1")).toContainText("Extração #1");

    const abrirLink = urlRow(authenticatedPage).locator("a").filter({ hasText: "Abrir" });
    await expect(abrirLink).toBeVisible();

    const rel = await abrirLink.getAttribute("rel");
    expect(rel).toContain("noopener");
    expect(rel).toContain("noreferrer");
  });
});
