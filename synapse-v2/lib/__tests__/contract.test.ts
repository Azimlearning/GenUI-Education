import { describe, expect, test } from "bun:test";
import { decodeFrames, encodeEvent, PipelineRequest } from "../contract";

describe("SSE framing", () => {
  test("round-trips an event", () => {
    const frame = encodeEvent({ type: "guidance", text: "hello" });
    const { events, rest } = decodeFrames(frame);
    expect(events).toEqual([{ type: "guidance", text: "hello" }]);
    expect(rest).toBe("");
  });

  test("normalises CRLF frames", () => {
    // The bug that cost v1 an afternoon: an SSE server emitting \r\n means
    // splitting on \n\n never matches and the whole stream vanishes silently.
    const crlf = `data: ${JSON.stringify({ type: "guidance", text: "hi" })}\r\n\r\n`;
    const { events } = decodeFrames(crlf);
    expect(events).toHaveLength(1);
  });

  test("holds a partial frame back until it completes", () => {
    const full = encodeEvent({ type: "guidance", text: "complete" });
    const split = full.slice(0, 20);
    const first = decodeFrames(split);
    expect(first.events).toHaveLength(0);
    expect(first.rest).toBe(split);

    const second = decodeFrames(first.rest + full.slice(20));
    expect(second.events).toHaveLength(1);
  });

  test("drops a malformed frame without killing the stream", () => {
    const buffer = `data: {not json\n\n${encodeEvent({ type: "guidance", text: "survived" })}`;
    const { events } = decodeFrames(buffer);
    expect(events).toEqual([{ type: "guidance", text: "survived" }]);
  });

  test("drops an event that fails schema validation", () => {
    const buffer = `data: ${JSON.stringify({ type: "not_a_real_event" })}\n\n`;
    expect(decodeFrames(buffer).events).toHaveLength(0);
  });
});

describe("PipelineRequest", () => {
  test("applies defaults to a bare prompt", () => {
    const parsed = PipelineRequest.parse({ prompt: "why is the sky blue" });
    expect(parsed.confirmed).toBe(false);
    expect(parsed.history).toEqual([]);
    expect(parsed.interaction).toBeNull();
  });

  test("rejects an empty prompt", () => {
    expect(PipelineRequest.safeParse({ prompt: "" }).success).toBe(false);
  });
});
