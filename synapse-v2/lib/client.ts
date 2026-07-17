/**
 * SSE client.
 *
 * Hand-rolled over fetch rather than EventSource, because EventSource is GET-only
 * and the pipeline takes a POST body.
 */

import { decodeFrames, type PipelineRequestInput, type SynapseEvent } from "./contract";

export async function streamPipeline(
  body: PipelineRequestInput,
  onEvent: (event: SynapseEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  const res = await fetch("/api/pipeline", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });

  if (!res.ok || !res.body) {
    const detail = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(detail.error ?? `Request failed (${res.status})`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const { events, rest } = decodeFrames(buffer);
    buffer = rest;
    for (const event of events) onEvent(event);
  }
}
