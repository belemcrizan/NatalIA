import { authHeaders } from "./api";
import type { JobPublic } from "./types";

function parseSseBlock(block: string): { event: string; data: string } | null {
  let event = "message";
  const data: string[] = [];
  for (const line of block.split("\n")) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    if (line.startsWith("data:")) data.push(line.slice(5).trim());
  }
  if (!data.length) return null;
  return { event, data: data.join("\n") };
}

export async function streamJobEvents(
  jobId: string,
  onJob: (job: JobPublic) => void,
  signal: AbortSignal,
) {
  const response = await fetch(`/api/jobs/${jobId}/events`, {
    headers: authHeaders(),
    signal,
  });
  if (!response.ok || !response.body) {
    throw new Error(`Progress stream failed (${response.status}).`);
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() ?? "";
    for (const part of parts) {
      const parsed = parseSseBlock(part);
      if (!parsed || parsed.event === "error") continue;
      onJob(JSON.parse(parsed.data) as JobPublic);
    }
  }
}
