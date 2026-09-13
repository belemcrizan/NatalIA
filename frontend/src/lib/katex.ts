import katex from "katex";

export function renderKatex(source: string, display = true): { html: string | null; error: string | null } {
  const trimmed = source.trim();
  if (!trimmed) return { html: null, error: null };
  try {
    const html = katex.renderToString(trimmed, {
      displayMode: display,
      throwOnError: true,
      trust: false,
      strict: "ignore",
      output: "html",
      maxExpand: 200,
    });
    return { html, error: null };
  } catch (err) {
    return {
      html: null,
      error: err instanceof Error ? err.message : "Invalid mathematical notation.",
    };
  }
}
