/**
 * Typed SSE event schemas. Mirrors backend/schemas/events.py exactly
 * (API_SPEC.md section 2). If you change one side, change the other in
 * the same commit; the backend snapshot tests guard the wire shapes.
 */
import { z } from "zod";

export const IntentSchema = z.object({
  artifact_type: z.enum([
    "simulation",
    "explorable_diagram",
    "virtual_experiment",
    "data_visualization",
    "text_only",
  ]),
  domain: z.enum(["physics", "chemistry", "biology", "earth_space", "math_adjacent"]),
  complexity: z.union([z.literal(1), z.literal(2), z.literal(3)]),
});

export const MetaSchema = z.object({
  intent: IntentSchema,
  canonical_concept: z.string(),
  cache: z.enum(["hit", "miss"]),
});

export const TextDeltaSchema = z.object({ chunk: z.string() });
export const TextDoneSchema = z.object({});

export const ArtifactStatusSchema = z.object({
  stage: z.enum(["planning", "generating", "verifying", "revising", "postprocessing"]),
});
export const ArtifactDeltaSchema = z.object({ chunk: z.string() });
export const ArtifactDoneSchema = z.object({
  artifact_id: z.string(),
  title: z.string(),
  html: z.string(),
});
export const ArtifactFailedSchema = z.object({
  reason: z.string(),
  detail_user: z.string(),
  retryable: z.boolean(),
});

export const TutorMsgSchema = z.object({ text: z.string() });

export const DoneSchema = z.object({
  usage: z.object({
    tokens_in: z.number(),
    tokens_out: z.number(),
    cost_usd: z.number(),
  }),
  timings_ms: z.object({
    first_token: z.number(),
    artifact_total: z.number(),
  }),
});

export const eventSchemas = {
  meta: MetaSchema,
  text_delta: TextDeltaSchema,
  text_done: TextDoneSchema,
  artifact_status: ArtifactStatusSchema,
  artifact_delta: ArtifactDeltaSchema,
  artifact_done: ArtifactDoneSchema,
  artifact_failed: ArtifactFailedSchema,
  tutor_msg: TutorMsgSchema,
  done: DoneSchema,
} as const;

export type EventName = keyof typeof eventSchemas;

export type Meta = z.infer<typeof MetaSchema>;
export type Intent = z.infer<typeof IntentSchema>;

export type AxiomEvent = {
  [K in EventName]: { type: K; data: z.infer<(typeof eventSchemas)[K]> };
}[EventName];

/** Validate one wire event. Unknown names and invalid payloads return null
 *  (callers drop them silently and count, per API_SPEC bridge/listener rules). */
export function parseEvent(name: string, data: unknown): AxiomEvent | null {
  const schema = (eventSchemas as Record<string, z.ZodTypeAny>)[name];
  if (!schema) return null;
  const result = schema.safeParse(data);
  if (!result.success) return null;
  return { type: name, data: result.data } as AxiomEvent;
}
