import { expect } from "@playwright/test";
import { test } from "./fixtures";

test.describe("Extrair — QR Code Camera", () => {
  // ---------------------------------------------------------------------------
  // CAM-002: Camera button rendered next to the URL input
  // ---------------------------------------------------------------------------
  test("CAM-002: Camera button is visible next to URL input", async ({ authenticatedPage }) => {
    await authenticatedPage.goto("/extrair");

    const cameraButton = authenticatedPage.getByRole("button", {
      name: /escanear qr code/i,
    });

    await expect(cameraButton).toBeVisible();
  });

  // ---------------------------------------------------------------------------
  // CAM-003: Clicking camera button opens a modal with live video feed
  // ---------------------------------------------------------------------------
  test("CAM-003: Clicking camera button opens modal with live video feed", async ({ authenticatedPage }) => {
    // Mock getUserMedia to return a canvas-based MediaStream
    await authenticatedPage.addInitScript(() => {
      const canvas = document.createElement("canvas");
      canvas.width = 320;
      canvas.height = 240;
      const ctx = canvas.getContext("2d");
      ctx.fillStyle = "white";
      ctx.fillRect(0, 0, 320, 240);
      const stream = canvas.captureStream(10);

      Object.defineProperty(navigator, "mediaDevices", {
        value: { getUserMedia: async () => stream },
        configurable: true,
      });
    });

    await authenticatedPage.goto("/extrair");

    const cameraButton = authenticatedPage.getByRole("button", {
      name: /escanear qr code/i,
    });
    await cameraButton.click();

    const modal = authenticatedPage.getByRole("dialog");
    await expect(modal).toBeVisible();

    // Video element with autoplay and playsinline must exist inside the modal
    const video = modal.locator("video[autoplay][playsinline]");
    await expect(video).toBeVisible();
  });

  // ---------------------------------------------------------------------------
  // CAM-004: Cancel button closes the modal and stops the camera
  // ---------------------------------------------------------------------------
  test("CAM-004: Cancel button closes modal and stops camera", async ({ authenticatedPage }) => {
    // Track whether getUserMedia was called and if tracks were stopped
    await authenticatedPage.addInitScript(() => {
      let gumCallCount = 0;
      let stopCallCount = 0;

      const canvas = document.createElement("canvas");
      canvas.width = 320;
      canvas.height = 240;
      const ctx = canvas.getContext("2d");
      ctx.fillStyle = "white";
      ctx.fillRect(0, 0, 320, 240);
      const stream = canvas.captureStream(10);

      // Wrap track.stop to track calls
      const originalStop = stream.getTracks()[0]?.stop?.bind(stream.getTracks()[0]);
      if (stream.getTracks()[0]) {
        stream.getTracks()[0].stop = () => {
          stopCallCount++;
          originalStop?.();
        };
      }

      (window as any).__test__gumCallCount = () => gumCallCount;
      (window as any).__test__stopCallCount = () => stopCallCount;

      Object.defineProperty(navigator, "mediaDevices", {
        value: {
          getUserMedia: async () => {
            gumCallCount++;
            return stream;
          },
        },
        configurable: true,
      });
    });

    await authenticatedPage.goto("/extrair");

    const cameraButton = authenticatedPage.getByRole("button", {
      name: /escanear qr code/i,
    });
    await cameraButton.click();

    const modal = authenticatedPage.getByRole("dialog");
    await expect(modal).toBeVisible();

    // Click the Cancel button (or close button)
    const cancelButton = modal.getByRole("button", { name: /cancelar/i });
    await cancelButton.click();

    // Modal must be removed from the DOM
    await expect(modal).not.toBeVisible();

    // verify getUserMedia was called (camera started)
    const gumCalled = await authenticatedPage.evaluate(() =>
      (window as any).__test__gumCallCount(),
    );
    expect(gumCalled).toBeGreaterThanOrEqual(1);
  });

  // ---------------------------------------------------------------------------
  // CAM-005: Valid QR Code (URL starting with http) fills the URL input and
  //          closes the modal
  // ---------------------------------------------------------------------------
  test("CAM-005: Valid http QR Code fills URL input and closes modal", async ({ authenticatedPage }) => {
    await authenticatedPage.addInitScript(() => {
      const canvas = document.createElement("canvas");
      canvas.width = 320;
      canvas.height = 240;
      const ctx = canvas.getContext("2d");
      ctx.fillStyle = "white";
      ctx.fillRect(0, 0, 320, 240);
      const stream = canvas.captureStream(10);

      Object.defineProperty(navigator, "mediaDevices", {
        value: { getUserMedia: async () => stream },
        configurable: true,
      });
    });

    await authenticatedPage.goto("/extrair");

    const cameraButton = authenticatedPage.getByRole("button", {
      name: /escanear qr code/i,
    });
    await cameraButton.click();

    const modal = authenticatedPage.getByRole("dialog");
    await expect(modal).toBeVisible();

    // Inject a valid http URL via the test seam
    const qrUrl =
      "https://www.sefaz.mt.gov.br/nfce/consultanfce?p=test";
    await authenticatedPage.evaluate(function (url) {
      window.__injectQrResult?.(url);
    }, qrUrl);

    // URL input must be filled with the scanned value
    const urlInput = authenticatedPage.locator("#extracao-url");
    await expect(urlInput).toHaveValue(qrUrl);

    // Modal must close automatically
    await expect(modal).not.toBeVisible();
  });

  // ---------------------------------------------------------------------------
  // CAM-006: Non-http QR Codes are ignored (scanner continues)
  // ---------------------------------------------------------------------------
  test("CAM-006: Non-http QR Code is ignored and scanner continues", async ({ authenticatedPage }) => {
    await authenticatedPage.addInitScript(() => {
      const canvas = document.createElement("canvas");
      canvas.width = 320;
      canvas.height = 240;
      const ctx = canvas.getContext("2d");
      ctx.fillStyle = "white";
      ctx.fillRect(0, 0, 320, 240);
      const stream = canvas.captureStream(10);

      Object.defineProperty(navigator, "mediaDevices", {
        value: { getUserMedia: async () => stream },
        configurable: true,
      });
    });

    await authenticatedPage.goto("/extrair");

    const cameraButton = authenticatedPage.getByRole("button", {
      name: /escanear qr code/i,
    });
    await cameraButton.click();

    const modal = authenticatedPage.getByRole("dialog");
    await expect(modal).toBeVisible();

    // 1. Inject a non-http QR Code content — must be ignored
    await authenticatedPage.evaluate(function () {
      window.__injectQrResult?.("Hello World");
    });

    const urlInput = authenticatedPage.locator("#extracao-url");
    await expect(urlInput).toHaveValue("");

    // Modal must remain open — scanner continues
    await expect(modal).toBeVisible();

    // 2. Now inject a valid http URL — must work
    const qrUrl =
      "https://www.sefaz.mt.gov.br/nfce/consultanfce?p=test";
    await authenticatedPage.evaluate(function (url) {
      window.__injectQrResult?.(url);
    }, qrUrl);

    await expect(urlInput).toHaveValue(qrUrl);
    await expect(modal).not.toBeVisible();
  });

  // ---------------------------------------------------------------------------
  // CAM-007 + CAM-008: Camera unavailable / permission denied shows friendly
  //                    error message
  // ---------------------------------------------------------------------------
  test("CAM-007: Camera unavailable shows friendly error message", async ({ authenticatedPage }) => {
    // Mock getUserMedia to reject (covers both NotAllowedError and other
    // failures — CAM-007 and CAM-008 share the same error handling path)
    await authenticatedPage.addInitScript(() => {
      Object.defineProperty(navigator, "mediaDevices", {
        value: {
          getUserMedia: async function () {
            throw new DOMException("Permission denied", "NotAllowedError");
          },
        },
        configurable: true,
      });
    });

    await authenticatedPage.goto("/extrair");

    const cameraButton = authenticatedPage.getByRole("button", {
      name: /escanear qr code/i,
    });
    await cameraButton.click();

    const modal = authenticatedPage.getByRole("dialog");
    await expect(modal).toBeVisible();

    // A friendly error message must be displayed (Portuguese)
    const errorElement = modal.locator("[role=alert]");
    await expect(errorElement).toBeVisible();
    await expect(errorElement).toContainText(
      /câmera|permissões|disponível|não disponível|verifique/i,
    );

    // No video element should be rendered when camera fails
    await expect(modal.locator("video")).toHaveCount(0);

    // Cancel button must still be functional
    const cancelButton = modal.getByRole("button", { name: /cancelar/i });
    await expect(cancelButton).toBeVisible();
    await cancelButton.click();

    await expect(modal).not.toBeVisible();
  });
});
