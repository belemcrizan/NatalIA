import type { ApiError } from "./types";

let memoryApiKey: string | null = null;
let generation = 0;

export function identityGeneration() {
  return generation;
}

export function setSessionApiKey(value: string | null) {
  memoryApiKey = value && value.trim() ? value.trim() : null;
  generation += 1;
}

export function sessionApiKey() {
  return memoryApiKey;
}

export function authHeaders(): Record<string, string> {
  if (!memoryApiKey) return {};
  return { "X-API-Key": memoryApiKey, Authorization: `Bearer ${memoryApiKey}` };
}

function detailMessage(body: unknown, fallback: string) {
  if (typeof body === "string" && body) return body;
  if (body && typeof body === "object") {
    const rec = body as { detail?: unknown };
    if (typeof rec.detail === "string") return rec.detail;
    if (Array.isArray(rec.detail)) {
      return rec.detail
        .map((item) => {
          if (item && typeof item === "object" && "msg" in item) {
            const loc = "loc" in item ? String((item as { loc: unknown }).loc) : "";
            return `${loc} ${(item as { msg: string }).msg}`.trim();
          }
          return JSON.stringify(item);
        })
        .join("; ");
    }
    if (rec.detail && typeof rec.detail === "object") return JSON.stringify(rec.detail);
  }
  return fallback;
}

export async function api<T>(path: string, init: RequestInit = {}, signal?: AbortSignal): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  const auth = authHeaders();
  for (const [key, value] of Object.entries(auth)) {
    if (!headers.has(key)) headers.set(key, value);
  }
  let response: Response;
  try {
    response = await fetch(path, { ...init, headers, signal });
  } catch (err) {
    const error: ApiError = {
      status: 0,
      message: signal?.aborted ? "Request cancelled." : "Network interruption. Check that the API is running.",
    };
    throw Object.assign(error, { cause: err });
  }
  const requestId = response.headers.get("X-Request-ID") ?? undefined;
  const retryAfter = response.headers.get("Retry-After") ?? undefined;
  if (response.status === 204) return undefined as T;
  const text = await response.text();
  let body: unknown = null;
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = text;
    }
  }
  if (!response.ok) {
    const error: ApiError = {
      status: response.status,
      message: detailMessage(body, response.statusText || "Request failed"),
      requestId,
      retryAfter,
      details: body,
    };
    throw error;
  }
  return body as T;
}
