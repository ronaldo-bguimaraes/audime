import { test as base, expect } from "@playwright/test";
import type { Page } from "@playwright/test";

export const MOCK_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.test";

const MOCK_USER = { id_usuario: 1, nome: "Usuário Teste", email: "test@example.com" };

const mockNotas = [
  {
    id: 1,
    empresa: "SDB COMERCIO DE ALIMENTOS LTDA",
    chave: "51260509477652008413651230002620731725445443",
    numero: "262073",
    serie: "1",
    emissao: "2025-01-15",
    valor_total: 157.80,
    qtd_total_itens: 5,
    extra: {
      emitente: {
        cnpj: "09.477.652/0084-13",
        logradouro: "Rodovia Rod Emanuel Pinheiro",
        numero: "5150",
        complemento: "",
        bairro: "Jardim Florianopolis",
        cidade: "CUIABA",
        uf: "MT",
      },
      protocolo_autorizacao: {
        numero: "151260384423214",
        data_hora: "25/06/2026 19:13:19",
      },
      formas_pagamento: [
        { tipo: "Cartão de Crédito", valor: 134.50 },
        { tipo: "Cartão de Crédito", valor: 134.50 },
      ],
      consumidor: "Consumidor não identificado",
      ambiente: "Produção",
      informacoes_interesse: {
        tributos_federal: 37.04,
        tributos_estadual: 41.86,
        tributos_municipal: 0.0,
        coo: 581585,
        pdv: 121,
      },
      troco: null,
    },
    items: [
      { id: 1, item_codigo: "7897517206086", item_descricao: "MOLHO TOM FUGINI 300G", item_quantidade: 2, item_tipo_unidade: "UN", item_valor_unidade: 4.50, item_valor_total: 9.00, nota_id: 1, extra: {} },
      { id: 2, item_codigo: "7891234567890", item_descricao: "ARROZ TIO JOÃO 5KG", item_quantidade: 1, item_tipo_unidade: "UN", item_valor_unidade: 25.90, item_valor_total: 25.90, nota_id: 1, extra: {} },
      { id: 3, item_codigo: "7890987654321", item_descricao: "FEIJÃO CARIOCA 1KG", item_quantidade: 3, item_tipo_unidade: "UN", item_valor_unidade: 8.50, item_valor_total: 25.50, nota_id: 1, extra: {} },
      { id: 4, item_codigo: "7891112223334", item_descricao: "LEITE INTEGRAL 1L", item_quantidade: 6, item_tipo_unidade: "UN", item_valor_unidade: 6.90, item_valor_total: 41.40, nota_id: 1, extra: {} },
      { id: 5, item_codigo: "7894445556667", item_descricao: "CAFÉ PILÃO 500G", item_quantidade: 2, item_tipo_unidade: "UN", item_valor_unidade: 15.50, item_valor_total: 31.00, nota_id: 1, extra: {} },
    ],
  },
  {
    id: 2,
    empresa: "MERCADINHO DO POVO LTDA",
    chave: "51260509477652008413651230002620731725445444",
    numero: "262074",
    serie: "1",
    emissao: "2025-01-16",
    valor_total: 89.50,
    qtd_total_itens: 1,
    extra: {
      emitente: { cnpj: null, logradouro: "", numero: "", complemento: "", bairro: "", cidade: "", uf: "" },
      protocolo_autorizacao: null,
      formas_pagamento: [],
      consumidor: null,
      ambiente: null,
      informacoes_interesse: {},
      troco: null,
    },
    items: [
      { id: 6, item_codigo: "7896667778889", item_descricao: "AÇÚCAR REFINADO 1KG", item_quantidade: 2, item_tipo_unidade: "UN", item_valor_unidade: 4.30, item_valor_total: 8.60, nota_id: 2, extra: {} },
    ],
  },
  {
    id: 3,
    empresa: "PADARIA DO BAIRRO LTDA",
    chave: "51260509477652008413651230002620731725445445",
    numero: "262075",
    serie: "1",
    emissao: "2025-01-17",
    valor_total: 45.00,
    qtd_total_itens: 1,
    extra: {
      emitente: { cnpj: null, logradouro: "", numero: "", complemento: "", bairro: "", cidade: "", uf: "" },
      protocolo_autorizacao: null,
      formas_pagamento: [],
      consumidor: null,
      ambiente: null,
      informacoes_interesse: {},
      troco: null,
    },
    items: [
      { id: 7, item_codigo: "7899998887776", item_descricao: "PÃO FRANCÊS", item_quantidade: 10, item_tipo_unidade: "UN", item_valor_unidade: 1.50, item_valor_total: 15.00, nota_id: 3, extra: {} },
    ],
  },
];

async function setupApiMocks(page: Page) {
  await page.route("**/v1/auth/**", async (route) => {
    const url = route.request().url();
    if (url.includes("/auth/me")) {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(MOCK_USER) });
    } else if (url.includes("/auth/code")) {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ status: "ok" }) });
    } else if (url.includes("/auth/verify")) {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ status: "ok", access_token: MOCK_TOKEN, id_usuario: 1 }) });
    } else {
      await route.fulfill({ status: 404, contentType: "application/json", body: JSON.stringify({ detail: "Not found" }) });
    }
  });

  await page.route("**/v1/notas", async (route) => {
    if (route.request().method() === "GET") {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(mockNotas) });
    }
  });

  await page.route("**/v1/notas/*", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(mockNotas[0]) });
  });

  await page.route("**/v1/extracoes", async (route) => {
    const body = route.request().postDataJSON();
    if (body?.url?.startsWith("http")) {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ id_extracao: 42, status: "concluido", created_at: "2025-01-15T10:00:00" }) });
    } else {
      await route.fulfill({ status: 400, contentType: "application/json", body: JSON.stringify({ detail: "URL inválida" }) });
    }
  });
}

export const test = base.extend<{ authenticatedPage: Page }>({
  authenticatedPage: async ({ browser }, use) => {
    const context = await browser.newContext();
    const page = await context.newPage();

    await setupApiMocks(page);

    await page.goto("/");
    await page.evaluate((token) => {
      localStorage.setItem("audime_token", token);
    }, MOCK_TOKEN);

    await page.goto("/dashboard");
    await expect(page.locator("h1")).toContainText("Notas Fiscais", { timeout: 10000 });

    await use(page);
    await context.close();
  },
});
