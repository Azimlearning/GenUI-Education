/**
 * Typed SSE client for POST /api/ask.
 * Parses the event-stream by hand (EventSource cannot POST), validates every
 * payload with zod, and silently drops invalid frames (logging a count).
 */
import { parseEvent, type AxiomEvent } from "@/types/events";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

interface Frame {
  event: string;
  data: string;
}

function parseFrame(block: string): Frame | null {
  let event = "";
  let data = "";
  for (const line of block.split("\n")) {
    if (line.startsWith("event: ")) event = line.slice(7);
    else if (line.startsWith("data: ")) data += line.slice(6);
  }
  return event && data ? { event, data } : null;
}

export async function streamAsk(opts: {
  sessionId: string;
  message: string;
  onEvent: (event: AxiomEvent) => void;
  signal?: AbortSignal;
}): Promise<void> {
  const res = await fetch(`${API_BASE}/api/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ session_id: opts.sessionId, message: opts.message }),
    signal: opts.signal,
  });

  if (!res.ok) {
    let message = `request failed (${res.status})`;
    try {
      const body = (await res.json()) as { error?: { message?: string } };
      if (body.error?.message) message = body.error.message;
    } catch {
      // non-JSON error body; keep the status message
    }
    throw new Error(message);
  }
  if (!res.body) throw new Error("response has no body");

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let dropped = 0;

  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });

    let boundary: number;
    while ((boundary = buffer.indexOf("\n\n")) !== -1) {
      const block = buffer.slice(0, boundary);
      buffer = buffer.slice(boundary + 2);

      const frame = parseFrame(block);
      if (!frame) continue;

      let payload: unknown;
      try {
        payload = JSON.parse(frame.data);
      } catch {
        dropped++;
        continue;
      }
      const event = parseEvent(frame.event, payload);
      if (event) {
        opts.onEvent(event);
      } else {
        dropped++;
      }
    }
  }

  if (dropped > 0) {
    console.warn(`sse: dropped ${dropped} invalid frame(s)`);
  }
}
