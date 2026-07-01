const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";

export class FetchError extends Error {
  status: number;
  body: unknown;

  constructor(message: string, status: number, body?: unknown) {
    super(message);
    this.name = "FetchError";
    this.status = status;
    this.body = body;
  }
}

function getToken(): string | null {
  return localStorage.getItem("audime_token");
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (res.status === 401) {
    // Remove token mas NÃO redireciona — o ProtectedRoute detecta
    // a ausência do token e redireciona no próximo render.
    // Isso permite que chamadas de autenticação (POST /v1/auth/verify)
    // exibam o erro ao invés de redirecionar abruptamente.
    localStorage.removeItem("audime_token");
    localStorage.removeItem("audime_user_id");
    throw new FetchError("Não autenticado", 401);
  }

  if (res.status === 429) {
    const body = await res.json().catch(() => ({}));
    throw new FetchError(
      (body as { detail?: string }).detail ?? "Muitas requisições",
      429,
      body,
    );
  }

  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const message =
      (body as { detail?: string }).detail ?? `Erro ${res.status}`;
    throw new FetchError(message, res.status, body);
  }

  // 204 No Content
  if (res.status === 204) {
    return undefined as T;
  }

  return res.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "PATCH",
      body: body ? JSON.stringify(body) : undefined,
    }),
};
