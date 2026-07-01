import { test as setup, expect } from "@playwright/test";
import type { Page } from "@playwright/test";

// Auth fixture that creates an authenticated state
const authFixture = setup.extend<{ authenticatedPage: Page }>({
  async setupAsync({ browser }) {
    const context = await browser.newContext();
    const page = await context.newPage();
    
    // Navigate to login page
    await page.goto("/login");
    
    // Perform login with test credentials
    await page.fill('[data-testid="email-input"]', "test@example.com");
    await page.fill('[data-testid="code-input"]', "123456");
    await page.click('[data-testid="submit-button"]');
    
    // Wait for successful navigation to dashboard
    await expect(page.locator('[data-testid="dashboard-title"]')).toBeVisible({ timeout: 10000 });
    
    // Save authentication state for reuse
    await context.storageState({ path: "test-auth-state.json" });
    
    // Close the context (will be recreated per test)
    await context.close();
  },
  // Also provide a page for the test if needed
  async setup({ authenticatedPage }) {
    // This fixture returns the authenticated page for use in tests
    return { authenticatedPage };
  }
});

// NFC data fixture
const nfcDataFixture = setup.extend<{ nfcPage: Page }>({
  async setupAsync({ browser }) {
    // Load saved auth state to create authenticated context
    const context = await browser.newContext({
      storageState: "test-auth-state.json"
    });
    const page = await context.newPage();
    
    // Navigate to NFC upload page
    await page.goto("/nfce-upload");
    
    // Wait for upload form to be visible
    await expect(page.locator('[data-testid="upload-form"]')).toBeVisible();
    
    // Save auth state for subsequent tests that need it
    await context.storageState({ path: "test-nfce-auth-state.json" });
    
    await context.close();
  },
});

export { authFixture, nfcDataFixture };
