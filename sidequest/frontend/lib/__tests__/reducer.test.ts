import { describe, expect, it } from "vitest";

import { chatReducer, initialChatState, type ChatState } from "@/lib/reducer";
import { parseEvent, type AxiomEvent } from "@/types/events";

function event(name: string, data: unknown): AxiomEvent {
  const parsed = parseEvent(name, data);
  if (!parsed) throw new Error(`invalid test event: ${name}`);
  return parsed;
}

const META = {
  intent: { artifact_type: "text_only", domain: "physics", complexity: 1 },
  canonical_concept: "ice_water_density_buoyancy",
  cache: "miss",
};

function runStream(events: AxiomEvent[]): ChatState {
  let state = chatReducer(initialChatState, { type: "user_sent", message: "why does ice float?" });
  for (const e of events) {
    state = chatReducer(state, { type: "stream_event", event: e });
  }
  return state;
}

describe("chatReducer", () => {
  it("appends user message and streaming assistant placeholder", () => {
    const state = chatReducer(initialChatState, { type: "user_sent", message: "hi" });
    expect(state.messages).toHaveLength(2);
    expect(state.messages[1]).toMatchObject({ role: "assistant", content: "", streaming: true });
    expect(state.status).toBe("waiting");
  });

  it("accumulates text deltas into the assistant message", () => {
    const state = runStream([
      event("meta", META),
      event("text_delta", { chunk: "Ice " }),
      event("text_delta", { chunk: "floats." }),
      event("text_done", {}),
      event("done", {
        usage: { tokens_in: 1, tokens_out: 2, cost_usd: 0 },
        timings_ms: { first_token: 100, artifact_total: 0 },
      }),
    ]);
    const assistant = state.messages[1];
    expect(assistant).toMatchObject({
      role: "assistant",
      content: "Ice floats.",
      streaming: false,
    });
    expect(state.status).toBe("idle");
  });

  it("stores meta on the assistant message and flips status to streaming", () => {
    const state = runStream([event("meta", META)]);
    expect(state.status).toBe("streaming");
    const assistant = state.messages[1];
    if (assistant?.role !== "assistant") throw new Error("expected assistant");
    expect(assistant.meta?.canonical_concept).toBe("ice_water_density_buoyancy");
  });

  it("tracks artifact build stages on the assistant message", () => {
    const state = runStream([
      event("meta", META),
      event("artifact_status", { stage: "planning" }),
      event("text_delta", { chunk: "hello" }),
      event("artifact_status", { stage: "generating" }),
    ]);
    expect(state.messages[1]).toMatchObject({
      content: "hello",
      artifact: { status: "building", stage: "generating" },
    });
  });

  it("artifact_done flips the card to ready with the html payload", () => {
    const state = runStream([
      event("meta", META),
      event("artifact_status", { stage: "postprocessing" }),
      event("artifact_done", {
        artifact_id: "art_1234",
        title: "Projectile Motion Lab",
        html: "<!doctype html><html></html>",
      }),
    ]);
    expect(state.messages[1]).toMatchObject({
      artifact: { status: "ready", artifactId: "art_1234", title: "Projectile Motion Lab" },
    });
  });

  it("artifact_failed flips the card to failed with honest copy", () => {
    const state = runStream([
      event("meta", META),
      event("artifact_failed", {
        reason: "timeout",
        detail_user: "I couldn't build a stable interactive piece for this one.",
        retryable: true,
      }),
    ]);
    expect(state.messages[1]).toMatchObject({
      artifact: { status: "failed", reason: "timeout", retryable: true },
    });
  });

  it("artifact_crashed marks a ready artifact as crashed by index", () => {
    let state = runStream([
      event("meta", META),
      event("artifact_done", { artifact_id: "a", title: "T", html: "<html></html>" }),
    ]);
    state = chatReducer(state, { type: "artifact_crashed", index: 1, message: "boom" });
    expect(state.messages[1]).toMatchObject({
      artifact: { status: "crashed", message: "boom" },
    });
  });

  it("marks error state and stops streaming on stream_error", () => {
    let state = chatReducer(initialChatState, { type: "user_sent", message: "q" });
    state = chatReducer(state, { type: "stream_error", message: "connection lost" });
    expect(state.status).toBe("error");
    expect(state.error).toBe("connection lost");
    expect(state.messages[1]).toMatchObject({ streaming: false });
  });

  it("stream_closed after abort settles a dangling stream back to idle", () => {
    let state = chatReducer(initialChatState, { type: "user_sent", message: "q" });
    state = chatReducer(state, { type: "stream_event", event: event("meta", META) });
    state = chatReducer(state, { type: "stream_closed" });
    expect(state.status).toBe("idle");
    expect(state.messages[1]).toMatchObject({ streaming: false });
  });
});

describe("parseEvent", () => {
  it("rejects unknown event names", () => {
    expect(parseEvent("mystery", {})).toBeNull();
  });

  it("rejects malformed payloads", () => {
    expect(parseEvent("text_delta", { nope: 1 })).toBeNull();
  });
});
