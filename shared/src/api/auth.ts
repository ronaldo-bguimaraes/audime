import type { ApiClient } from "./client";
import type { CodeResponse, MeResponse, VerifyResponse } from "../types";

export function createAuthApi(api: ApiClient) {
  return {
    requestCode: (email: string): Promise<CodeResponse> =>
      api.post<CodeResponse>("/v1/auth/code", { email }),

    verifyCode: (email: string, code: string): Promise<VerifyResponse> =>
      api.post<VerifyResponse>("/v1/auth/verify", { email, code }),

    fetchMe: (): Promise<MeResponse> => api.get<MeResponse>("/v1/auth/me"),
  };
}

export type AuthApi = ReturnType<typeof createAuthApi>;
