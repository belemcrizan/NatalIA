const KEY = "natalia.drafts.v1";
const LEGACY_KEYS = ["natalia.draft", "natalia-draft", "natalia.builder.draft"];

export type DraftRecord = {
  schema: "natalia-drafts-v1";
  updatedAt: string;
  mode: "guided" | "advanced";
  payload: unknown;
  label: "browser-local";
};

function parse(raw: string | null): DraftRecord | null {
  if (!raw) return null;
  try {
    const value = JSON.parse(raw) as DraftRecord;
    if (value?.schema === "natalia-drafts-v1" && value.payload) return value;
  } catch {
    return null;
  }
  return null;
}

function migrateLegacy(): DraftRecord | null {
  for (const key of LEGACY_KEYS) {
    const raw = window.localStorage.getItem(key);
    if (!raw) continue;
    try {
      const payload = JSON.parse(raw);
      return {
        schema: "natalia-drafts-v1",
        updatedAt: new Date(0).toISOString(),
        mode: "guided",
        payload,
        label: "browser-local",
      };
    } catch {
      return {
        schema: "natalia-drafts-v1",
        updatedAt: new Date(0).toISOString(),
        mode: "advanced",
        payload: raw,
        label: "browser-local",
      };
    }
  }
  return null;
}

export function loadDraft(): DraftRecord | null {
  if (typeof window === "undefined") return null;
  const current = parse(window.localStorage.getItem(KEY));
  if (current) return current;
  const legacy = migrateLegacy();
  if (!legacy) return null;
  // Keep legacy keys; do not overwrite a newer v1 draft.
  window.localStorage.setItem(KEY, JSON.stringify(legacy));
  return legacy;
}

export function saveDraft(record: Omit<DraftRecord, "schema" | "label" | "updatedAt">): void {
  if (typeof window === "undefined") return;
  const next: DraftRecord = {
    schema: "natalia-drafts-v1",
    label: "browser-local",
    updatedAt: new Date().toISOString(),
    ...record,
  };
  window.localStorage.setItem(KEY, JSON.stringify(next));
}
