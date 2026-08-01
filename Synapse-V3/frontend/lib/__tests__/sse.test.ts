import { afterEach, describe, expect, it, vi } from "vitest";

import { streamAsk } from "@/lib/sse";

const ORIGINAL_FETCH = globalThis.fetch;

afterEach(() => {
  globalThis.fetch = ORIGINAL_FETCH;
  vi.restoreAllMocks();
});

function sseResponse(body: string): Response {
  return new Response(body, {
    status: 200,
    headers: { "Content-Type": "text/event-stream" },
  });
}

describe("streamAsk", () => {
  it("reports a stream that closes before the terminal done event", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      sseResponse(
        'event: meta\ndata: {"intent":{"artifact_type":"text_only","domain":"chemistry","complexity":1},"canonical_concept":"fermentation","cache":"miss"}\n\n'
      )
    );

    await expect(
      streamAsk({ sessionId: "sess_test", message: "products of fermentation", onEvent: vi.fn() })
    ).rejects.toThrow("response stream ended before completion");
  });

  it("accepts a complete stream", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue(
      sseResponse(
        'event: text_delta\ndata: {"chunk":"Fermentation makes ethanol."}\n\n' +
          'event: done\ndata: {"usage":{"tokens_in":1,"tokens_out":1,"cost_usd":0},"timings_ms":{"first_token":1,"artifact_total":0}}\n\n'
      )
    );
    const onEvent = vi.fn();

    await streamAsk({ sessionId: "sess_test", message: "products of fermentation", onEvent });

    expect(onEvent).toHaveBeenCalledTimes(2);
  });
});
