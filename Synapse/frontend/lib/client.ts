// SSE client for POST /api/ask.
//
// The browser's native EventSource only does GET, but our endpoint is a POST (it carries the
// question in the body). So we use fetch + a ReadableStream reader and parse the SSE frames
// ourselves. Each `data:` line is one JSON-encoded SSEEvent.

import type { SSEEvent } from "./types";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

// ── Learner profile (P3) ──────────────────────────────────────────────────
export interface LearnerProfile {
  student_id: string;
  mastery: Record<string, number>;
  misconceptions: { misconception_id: string; topic: string; resolved: boolean; review_due: string | null }[];
  due_now: string[];
}

export interface Interaction {
  student_id: string;
  topic: string;
  correct: boolean;
  misconception_id: string | null;
  pattern: string | null;
}

export async function postInteraction(ev: Interaction): Promise<LearnerProfile | null> {
  try {
    const res = await fetch(`${API_BASE}/api/interaction`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(ev),
    });
    return res.ok ? ((await res.json()) as LearnerProfile) : null;
  } catch {
    return null;
  }
}

export async function fetchProfile(studentId: string): Promise<LearnerProfile | null> {
  try {
    const res = await fetch(`${API_BASE}/api/profile/${encodeURIComponent(studentId)}`);
    return res.ok ? ((await res.json()) as LearnerProfile) : null;
  } catch {
    return null;
  }
}

export async function fetchTeacher(): Promise<LearnerProfile[]> {
  try {
    const res = await fetch(`${API_BASE}/api/teacher`);
    if (!res.ok) return [];
    const data = (await res.json()) as { students: LearnerProfile[] };
    return data.students ?? [];
  } catch {
    return [];
  }
}

export interface AskCallbacks {
  onEvent: (event: SSEEvent) => void;
  onError?: (err: Error) => void;
  onClose?: () => void;
}

export async function ask(
  question: string,
  studentId: string | null,
  cb: AskCallbacks,
  signal?: AbortSignal,
): Promise<void> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}/api/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
      body: JSON.stringify({ question, student_id: studentId }),
      signal,
    });
  } catch (err) {
    cb.onError?.(err instanceof Error ? err : new Error(String(err)));
    return;
  }

  if (!res.ok || !res.body) {
    cb.onError?.(new Error(`Backend returned ${res.status}`));
    return;
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });

      // SSE frames are separated by a blank line.
      let sep: number;
      while ((sep = buffer.indexOf("\n\n")) !== -1) {
        const frame = buffer.slice(0, sep);
        buffer = buffer.slice(sep + 2);
        const dataLine = frame
          .split("\n")
          .find((l) => l.startsWith("data:"));
        if (!dataLine) continue;
        const json = dataLine.slice("data:".length).trim();
        if (!json) continue;
        try {
          cb.onEvent(JSON.parse(json) as SSEEvent);
        } catch {
          // ignore malformed frame
        }
      }
    }
    cb.onClose?.();
  } catch (err) {
    if ((err as Error).name !== "AbortError") {
      cb.onError?.(err instanceof Error ? err : new Error(String(err)));
    }
  }
}
