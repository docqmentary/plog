const DEFAULT_BASE_URL = "http://localhost:8000";

export interface ApiOptions extends RequestInit {
  apiKey?: string;
  parseJson?: boolean;
}

function resolveBaseUrl(): string {
  const envBase = import.meta.env.VITE_API_BASE_URL as string | undefined;
  return envBase && envBase.length > 0 ? envBase.replace(/\/$/, "") : DEFAULT_BASE_URL;
}

export const API_BASE_URL = resolveBaseUrl();

export async function apiFetch<T>(path: string, options: ApiOptions = {}): Promise<T> {
  const { apiKey, parseJson = true, headers, body, ...rest } = options;
  const requestHeaders = new Headers(headers);

  if (apiKey) {
    requestHeaders.set("X-API-Key", apiKey);
  }

  let requestBody = body;
  if (body && typeof body === "object" && !(body instanceof FormData)) {
    requestHeaders.set("Content-Type", "application/json");
    requestBody = JSON.stringify(body);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...rest,
    headers: requestHeaders,
    body: requestBody,
  });

  if (!response.ok) {
    let detail = response.statusText;
    try {
      const payload = await response.json();
      if (typeof payload?.detail === "string") {
        detail = payload.detail;
      }
    } catch {
      // ignore JSON parse errors
    }
    throw new Error(detail || `Request failed with status ${response.status}`);
  }

  if (!parseJson) {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return undefined as any;
  }

  return (await response.json()) as T;
}
