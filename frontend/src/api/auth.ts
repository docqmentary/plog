import { apiFetch } from "./client";
import type { SessionPayload } from "../types/api";

export interface LoginPayload {
  dev_user?: string;
  id_token?: string;
}

export async function login(payload: LoginPayload): Promise<SessionPayload> {
  return apiFetch<SessionPayload>("/auth/google/callback", {
    method: "POST",
    body: payload,
  });
}
