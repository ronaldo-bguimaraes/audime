import { api } from "./client";
import type {
  CodeResponse,
  MeResponse,
  VerifyResponse,
} from "../types";

export async function requestCode(email: string): Promise<CodeResponse> {
  return api.post<CodeResponse>("/v1/auth/code", { email });
}

export async function verifyCode(
  email: string,
  code: string,
): Promise<VerifyResponse> {
  return api.post<VerifyResponse>("/v1/auth/verify", { email, code });
}

export async function fetchMe(): Promise<MeResponse> {
  return api.get<MeResponse>("/v1/auth/me");
}
