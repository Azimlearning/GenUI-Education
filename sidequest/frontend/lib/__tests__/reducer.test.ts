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

  it("ignores artifact events in Phase 0 without corrupting state", () => {
    const state = runStream([
      event("meta", META),
      event("artifact_status", { stage: "planning" }),
      event("text_delta", { chunk: "hello" }),
    ]);
    expect(state.messages[1]).toMatchObject({ content: "hello" });
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
