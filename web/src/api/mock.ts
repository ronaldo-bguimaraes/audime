import { api } from "./client";
import type { PipelineStep, ExtracaoResult } from "./extracoes";
import type {
  DashboardNota,
  DashboardResumo,
  VersaoNota,
  Nota,
} from "../types";

const fakeSteps: PipelineStep[] = [
  {
    etapa: "RAW_IMPORT",
    status: "DONE",
    ordem: 1,
    iniciado_em: "2026-07-28T10:00:00Z",
    concluido_em: "2026-07-28T10:02:30Z",
    mensagem: null,
  },
  {
    etapa: "STAGING",
    status: "DONE",
    ordem: 2,
    iniciado_em: "2026-07-28T10:02:30Z",
    concluido_em: "2026-07-28T10:05:00Z",
    mensagem: null,
  },
  {
    etapa: "ANALYTICS",
    status: "RUNNING",
    ordem: 3,
    iniciado_em: "2026-07-28T10:05:00Z",
    concluido_em: null,
    mensagem: null,
  },
  {
    etapa: "COMPLETE",
    status: "PENDING",
    ordem: 4,
    iniciado_em: null,
    concluido_em: null,
    mensagem: null,
  },
];

let fakeExtracoes: ExtracaoResult[] = [
  {
    id_extracao: 1,
    url: "https://www.sefaz.mt.gov.br/nfce/consultanfce?p=41230812345678901234567890123456789012345678|2|1|1|1|1",
    status: "RUNNING",
    created_at: "2026-07-28T10:00:00Z",
    steps: fakeSteps,
    reprocess_count: 0,
  },
  {
    id_extracao: 2,
    url: "https://www.sefaz.mt.gov.br/nfce/consultanfce?p=41230898765432109876543210987654321098765432|2|1|1|1|1",
    status: "DONE",
    created_at: "2026-07-27T14:30:00Z",
    steps: fakeSteps.map((s) => ({ ...s, status: "DONE" as const })),
    reprocess_count: 0,
  },
  {
    id_extracao: 3,
    url: "https://www.sefaz.mt.gov.br/nfce/consultanfce?p=41230855555555555555555555555555555555555555|2|1|1|1|1",
    status: "ERROR",
    created_at: "2026-07-26T09:15:00Z",
    steps: [
      { etapa: "RAW_IMPORT", status: "ERROR", ordem: 1, iniciado_em: "2026-07-26T09:15:00Z", concluido_em: "2026-07-26T09:15:05Z", mensagem: "URL inválida: formato não reconhecido" },
      { etapa: "STAGING", status: "PENDING", ordem: 2, iniciado_em: null, concluido_em: null, mensagem: null },
      { etapa: "ANALYTICS", status: "PENDING", ordem: 3, iniciado_em: null, concluido_em: null, mensagem: null },
      { etapa: "COMPLETE", status: "PENDING", ordem: 4, iniciado_em: null, concluido_em: null, mensagem: null },
    ],
    reprocess_count: 2,
  },
];

const fakeDashboardNotas: DashboardNota[] = [
  {
    id_nota_analytics: 1,
    id_extracao: 1,
    empresa: "Supermercado Bom Preço Ltda",
    chave_acesso: "41230812345678901234567890123456789012345678",
    numero: "123456",
    serie: "1",
    emissao: "2026-07-28",
    valor_total: 157.9,
    qtd_total_itens: 12,
    valid_from: "2026-07-28T10:05:00Z",
    items: [],
    is_active: true,
  },
  {
    id_nota_analytics: 2,
    id_extracao: 2,
    empresa: "Farmácia Saúde Ltda",
    chave_acesso: "41230898765432109876543210987654321098765432",
    numero: "654321",
    serie: "1",
    emissao: "2026-07-27",
    valor_total: 89.5,
    qtd_total_itens: 3,
    valid_from: "2026-07-27T14:35:00Z",
    items: [],
    is_active: true,
  },
];

const fakeResumo: DashboardResumo = {
  total_notas: 42,
  valor_total: 5230.8,
  media_por_nota: 124.54,
  ultima_extracao: "2026-07-28T10:00:00Z",
  por_mes: [
    { mes: 7, ano: 2026, valor: 5230.8, quantidade: 38 },
    { mes: 6, ano: 2026, valor: 3100.0, quantidade: 25 },
  ],
  por_empresa: [
    { empresa: "Supermercado Bom Preço Ltda", valor: 2150.0, quantidade: 15 },
    { empresa: "Farmácia Saúde Ltda", valor: 890.5, quantidade: 8 },
  ],
};

const fakeNotas: Nota[] = [
  {
    id: 101,
    empresa: "Supermercado Bom Preço Ltda",
    chave: "41230812345678901234567890123456789012345678",
    numero: "123456",
    serie: "1",
    emissao: "2026-07-28",
    valor_total: 157.9,
    qtd_total_itens: 12,
    extra: null,
    items: [],
  },
  {
    id: 102,
    empresa: "Farmácia Saúde Ltda",
    chave: "41230898765432109876543210987654321098765432",
    numero: "654321",
    serie: "1",
    emissao: "2026-07-27",
    valor_total: 89.5,
    qtd_total_itens: 3,
    extra: null,
    items: [],
  },
];

function matchPath(pattern: string, path: string): boolean {
  const patParts = pattern.split("/");
  const pathParts = path.split("?")[0].split("/");
  if (patParts.length !== pathParts.length) return false;
  return patParts.every((p, i) => p === "*" || p === pathParts[i]);
}

function findHandler(
  method: string,
  path: string,
): ((body?: unknown) => unknown) | null {
  const url = new URL(path, "http://localhost");
  const pathname = url.pathname;

  const routes: [string, string, (body?: unknown) => unknown][] = [
    ["GET", "/v1/auth/me", () => ({ nome: "Usuário Dev", email: "dev@audime.com.br", id_usuario: 1 })],
    ["POST", "/v1/auth/code", () => ({ status: "ok" })],
    ["POST", "/v1/auth/verify", () => ({ status: "ok", access_token: "mock-token-dev", id_usuario: 1 })],

    ["GET", "/v1/extracoes", () => {
      const limit = Number(url.searchParams.get("limit")) || 10;
      return fakeExtracoes.slice(0, limit);
    }],
    ["POST", "/v1/extracoes", (body) => {
      const b = body as { url?: string } | undefined;
      const nova: ExtracaoResult = {
        id_extracao: fakeExtracoes.length + 1,
        url: b?.url ?? "",
        status: "PENDING",
        created_at: new Date().toISOString(),
        steps: [
          { etapa: "RAW_IMPORT", status: "PENDING", ordem: 1, iniciado_em: null, concluido_em: null, mensagem: null },
          { etapa: "STAGING", status: "PENDING", ordem: 2, iniciado_em: null, concluido_em: null, mensagem: null },
          { etapa: "ANALYTICS", status: "PENDING", ordem: 3, iniciado_em: null, concluido_em: null, mensagem: null },
          { etapa: "COMPLETE", status: "PENDING", ordem: 4, iniciado_em: null, concluido_em: null, mensagem: null },
        ],
        reprocess_count: 0,
      };
      fakeExtracoes.unshift(nova);
      return { id_extracao: nova.id_extracao, status: nova.status, job_id: null };
    }],
    ["POST", "/v1/extracoes/*/reprocessar", () => ({ id_extracao: 1, status: "RUNNING", job_id: "mock-job" })],

    ["GET", "/v1/dashboard/notas", () => fakeDashboardNotas],
    ["GET", "/v1/dashboard/notas/*", () => fakeDashboardNotas[0]],
    ["GET", "/v1/dashboard/resumo", () => fakeResumo],

    ["GET", "/v1/dashboard/notas/*/historico", () => [
      { valid_from: "2026-07-28T10:05:00Z", valid_to: null, is_current: true, empresa: "Supermercado Bom Preço Ltda", valor_total: 157.9 },
    ] as VersaoNota[]],
    ["PATCH", "/v1/dashboard/notas/*", () => ({ status: "ok" })],

    ["GET", "/v1/notas", () => fakeNotas],
  ];

  for (const [m, pattern, handler] of routes) {
    if (m === method && matchPath(pattern, pathname)) {
      return handler;
    }
  }
  return null;
}

export function setupMockApi() {
  if (localStorage.getItem("audime_token") !== "mock-token-dev") {
    localStorage.setItem("audime_token", "mock-token-dev");
    localStorage.setItem("audime_user_id", "1");
  }

  const origGet = api.get.bind(api);
  const origPost = api.post.bind(api);
  const origPatch = api.patch.bind(api);

  api.get = <T>(path: string): Promise<T> => {
    const handler = findHandler("GET", path);
    if (handler) return Promise.resolve(handler() as T);
    return origGet(path);
  };

  api.post = <T>(path: string, body?: unknown): Promise<T> => {
    const handler = findHandler("POST", path);
    if (handler) return Promise.resolve(handler(body) as T);
    return origPost(path, body);
  };

  api.patch = <T>(path: string, body?: unknown): Promise<T> => {
    const handler = findHandler("PATCH", path);
    if (handler) return Promise.resolve(handler(body) as T);
    return origPatch(path, body);
  };
}
