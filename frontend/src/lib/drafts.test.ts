import { describe, expect, it } from "vitest";

import { loadDraft, saveDraft } from "@/lib/drafts";

describe("browser-local drafts", () => {
  it("round-trips a versioned draft without claiming server storage", () => {
    window.localStorage.clear();
    saveDraft({ mode: "guided", payload: { title: "draft" } });
    const loaded = loadDraft();
    expect(loaded?.schema).toBe("natalia-drafts-v1");
    expect(loaded?.label).toBe("browser-local");
    expect(loaded?.payload).toEqual({ title: "draft" });
  });

  it("migrates a legacy key without deleting it", () => {
    window.localStorage.clear();
    window.localStorage.setItem("natalia.draft", JSON.stringify({ title: "old" }));
    const loaded = loadDraft();
    expect(loaded?.payload).toEqual({ title: "old" });
    expect(window.localStorage.getItem("natalia.draft")).toContain("old");
  });
});
