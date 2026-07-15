/**
 * The load-bearing seam.
 *
 * Every event the backend streams to the frontend is defined here, once. The
 * pipeline emits these; the UI renders them; nothing else crosses the wire.
 *
 * Zod schemas (not just TS types) because the model fills some of these
 * payloads and we validate before anything reaches the screen.
 */

import { z } from "zod";

/* ---------------------------------------------------------------- pipeline */

export const PIPELINE_STEPS = [
  "planner",
  "checker",
  "brief",
  "generator",
  "guide",
] as const;
export type PipelineStepName = (typeof PIPELINE_STEPS)[number];

export const STEP_LABELS: Record<PipelineStepName, string> = {
  planner: "Planner",
  checker: "Checker",
  brief: "Brief",
  generator: "Generator",
  guide: "Guide",
};

export const STEP_BLURBS: Record<PipelineStepName, string> = {
  planner: "Choosing the experiment and the tier that can express it",
  checker: "Testing the student's premise against the science",
  brief: "Describing what will be built",
  generator: "Building the interactive",
  guide: "Reading the student's interactions",
};

/** The three tiers of the generation ladder. Lowest tier that fits wins. */
export const TIERS = ["A", "B", "C"] as const;
export type Tier = (typeof TIERS)[number];

export const TIER_LABELS: Record<Tier, string> = {
  A: "Tier A · science component",
  B: "Tier B · composed screen",
  C: "Tier C · generated from scratch",
};

/* ------------------------------------------------------------------ events */

export const PipelineStepEvent = z.object({
  type: z.literal("pipeline_step"),
  step: z.enum(PIPELINE_STEPS),
  status: z.enum(["thinking", "done", "skipped", "failed"]),
  detail: z.string().default(""),
  /** Science-critical values echoed here so a wrong fill is visible, not silent. */
  evidence: z.array(z.string()).default([]),
});

/**
 * A contradiction between what the student said and what is true. Stated
 * plainly before anything is generated — never silently "fixed".
 */
export const Contradiction = z.object({
  student_claim: z.string(),
  correction: z.string(),
});

export const BriefEvent = z.object({
  type: z.literal("brief"),
  title: z.string(),
  description: z.string(),
  /** What the student will be able to manipulate. */
  manipulables: z.array(z.string()).default([]),
  tier: z.enum(TIERS),
  contradiction: Contradiction.nullable().default(null),
  /** False when the prompt explicitly asked to generate — the gate is skipped. */
  requires_confirm: z.boolean().default(true),
});

/** Tier A: a pre-built science component with model-filled slots. */
export const ComponentEvent = z.object({
  type: z.literal("component"),
  pattern: z.string(),
  slots: z.record(z.string(), z.unknown()),
});

/** Tier B: a declarative UI tree. */
export const UISpecEvent = z.object({
  type: z.literal("ui_spec"),
  spec: z.unknown(),
});

/** Tier C: self-contained HTML, streamed in chunks so it reads as "building". */
export const GeneratedCodeEvent = z.object({
  type: z.literal("generated_code"),
  chunk: z.string(),
  done: z.boolean().default(false),
});

export const GuidanceEvent = z.object({
  type: z.literal("guidance"),
  text: z.string(),
});

export const DoneEvent = z.object({
  type: z.literal("done"),
  /** Which tier actually rendered, after any fallback. */
  tier: z.enum(TIERS).nullable().default(null),
  /** Set when we degraded, so the pipeline panel can say so out loud. */
  fell_back_from: z.enum(TIERS).nullable().default(null),
  ms: z.number().default(0),
});

export const ErrorEvent = z.object({
  type: z.literal("error"),
  message: z.string(),
});

export const SynapseEvent = z.discriminatedUnion("type", [
  PipelineStepEvent,
  BriefEvent,
  ComponentEvent,
  UISpecEvent,
  GeneratedCodeEvent,
  GuidanceEvent,
  DoneEvent,
  ErrorEvent,
]);

export type PipelineStepEvent = z.infer<typeof PipelineStepEvent>;
export type BriefEvent = z.infer<typeof BriefEvent>;
export type ComponentEvent = z.infer<typeof ComponentEvent>;
export type UISpecEvent = z.infer<typeof UISpecEvent>;
export type GeneratedCodeEvent = z.infer<typeof GeneratedCodeEvent>;
export type GuidanceEvent = z.infer<typeof GuidanceEvent>;
export type DoneEvent = z.infer<typeof DoneEvent>;
export type ErrorEvent = z.infer<typeof ErrorEvent>;
export type SynapseEvent = z.infer<typeof SynapseEvent>;
export type Contradiction = z.infer<typeof Contradiction>;

/* ------------------------------------------------------- request payloads */

/** One interaction, from any tier. Tier A/B send node ids; Tier C sends "sandbox". */
export const InteractionEvent = z.object({
  source: z.string(),
  action: z.string(),
  values: z.record(z.string(), z.union([z.string(), z.number(), z.boolean()])).default({}),
});
export type InteractionEvent = z.infer<typeof InteractionEvent>;

export const Turn = z.object({
  role: z.enum(["user", "assistant"]),
  content: z.string(),
});
export type Turn = z.infer<typeof Turn>;

export const PipelineRequest = z.object({
  prompt: z.string().min(1),
  history: z.array(Turn).default([]),
  /** Set by "Generate Experiment" — skips straight to the Generator. */
  confirmed: z.boolean().default(false),
  /** Carried from the brief so the Generator builds what was promised. */
  plan: z
    .object({
      tier: z.enum(TIERS),
      pattern: z.string().nullable().default(null),
      title: z.string().default(""),
      description: z.string().default(""),
    })
    .nullable()
    .default(null),
  /** Set on a Guide round-trip. */
  interaction: InteractionEvent.nullable().default(null),
  /**
   * What is actually on the student's screen, for the Guide.
   *
   * The Guide is a separate call and cannot see the lab. Without this it gets
   * bare values and has to guess — the first live run produced a Guide asking
   * "what did you change?" about a slider it had no way to know existed.
   */
  context: z.string().nullable().default(null),
});
export type PipelineRequest = z.infer<typeof PipelineRequest>;
/**
 * What a caller writes, before Zod fills the defaults in. The server sees the
 * parsed shape (every field present); the client should not have to spell out
 * `context: null` just to ask a question.
 */
export type PipelineRequestInput = z.input<typeof PipelineRequest>;

/* ----------------------------------------------------------- SSE encoding */

export function encodeEvent(event: SynapseEvent): string {
  return `data: ${JSON.stringify(event)}\n\n`;
}

/**
 * Split an SSE buffer into complete frames.
 *
 * Normalises CRLF first: some SSE servers emit \r\n, so splitting on \n\n
 * silently swallows the entire stream. v1 lost an afternoon to this.
 * Returns the parsed events plus whatever partial frame is left over.
 */
export function decodeFrames(buffer: string): {
  events: SynapseEvent[];
  rest: string;
} {
  const normalised = buffer.replace(/\r\n/g, "\n");
  const parts = normalised.split("\n\n");
  const rest = parts.pop() ?? "";
  const events: SynapseEvent[] = [];

  for (const part of parts) {
    const line = part.split("\n").find((l) => l.startsWith("data: "));
    if (!line) continue;
    try {
      const parsed = SynapseEvent.safeParse(JSON.parse(line.slice(6)));
      if (parsed.success) events.push(parsed.data);
    } catch {
      // A malformed frame is not worth killing the stream over.
    }
  }

  return { events, rest };
}
