/**
 * The one endpoint. Streams the pipeline as SSE.
 *
 * Three modes, decided by the request:
 *   interaction present  -> Guide only (the round-trip)
 *   confirmed + plan     -> Generator only (the student pressed the button)
 *   otherwise            -> fast pass (plan/check/brief), then stop at the gate
 *                           unless the student explicitly asked to generate.
 */

import { NextResponse } from "next/server";
import {
  PipelineRequest,
  encodeEvent,
  type SynapseEvent,
  type Tier,
} from "@/lib/contract";
import { runFastPass, runGenerator, runGuide } from "@/lib/pipeline";
import { callLog, hasAnyProvider } from "@/lib/router";

// Tier C can legitimately take ~60s on a big lab.
export const maxDuration = 300;

export async function POST(req: Request) {
  if (!hasAnyProvider()) {
    return NextResponse.json(
      {
        error:
          "No provider configured. Copy .env.local.example to .env.local and set ANTHROPIC_API_KEY.",
      },
      { status: 500 },
    );
  }

  const parsed = PipelineRequest.safeParse(await req.json().catch(() => null));
  if (!parsed.success) {
    return NextResponse.json(
      { error: `Bad request: ${parsed.error.issues.map((i) => i.message).join("; ")}` },
      { status: 400 },
    );
  }
  const body = parsed.data;

  const started = Date.now();
  callLog.length = 0;

  const stream = new ReadableStream<Uint8Array>({
    async start(controller) {
      const encoder = new TextEncoder();
      let closed = false;

      const emit = (event: SynapseEvent) => {
        if (closed) return;
        try {
          controller.enqueue(encoder.encode(encodeEvent(event)));
        } catch {
          closed = true;
        }
      };

      try {
        // --- Guide round-trip ---------------------------------------------
        if (body.interaction) {
          await runGuide(body.interaction, body.prompt, body.history, emit, body.context);
          emit({ type: "done", tier: null, fell_back_from: null, ms: Date.now() - started });
          return;
        }

        // --- Confirmed: build what was briefed -----------------------------
        if (body.confirmed && body.plan) {
          const result = await runGenerator(
            { tier: body.plan.tier, pattern: body.plan.pattern },
            body.prompt,
            body.history,
            emit,
          );
          emit({
            type: "done",
            tier: result.tier,
            fell_back_from: result.fellBackFrom,
            ms: Date.now() - started,
          });
          return;
        }

        // --- Fast pass: plan, check, brief ---------------------------------
        const plan = await runFastPass(body.prompt, body.history, emit);

        // The gate. Unless they explicitly asked us to build it, we stop here
        // and let them read the brief (and any contradiction) first.
        if (plan.explicit_generate_request) {
          const result = await runGenerator(
            { tier: plan.tier as Tier, pattern: plan.pattern },
            body.prompt,
            body.history,
            emit,
          );
          emit({
            type: "done",
            tier: result.tier,
            fell_back_from: result.fellBackFrom,
            ms: Date.now() - started,
          });
          return;
        }

        emit({ type: "done", tier: null, fell_back_from: null, ms: Date.now() - started });
      } catch (err) {
        emit({
          type: "error",
          message: err instanceof Error ? err.message : "Unknown pipeline error",
        });
      } finally {
        closed = true;
        try {
          controller.close();
        } catch {
          // Already closed by a disconnect.
        }
      }
    },
  });

  return new Response(stream, {
    headers: {
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
      // Nginx/proxies buffer SSE by default, which stalls the visible pipeline.
      "X-Accel-Buffering": "no",
    },
  });
}
