/**
 * Bridge contract (API_SPEC.md section 3): inbound only, iframe -> parent.
 * The parent never posts into the iframe. Values are untrusted display data:
 * never interpolate into HTML, never eval, never treat as URLs.
 */
import { z } from "zod";

export const BridgeMessage = z.discriminatedUnion("type", [
  z.object({ type: z.literal("axiom_ready") }),
  z.object({
    type: z.literal("axiom_event"),
    control: z.string().max(64),
    value: z.union([z.string().max(256), z.number(), z.boolean()]),
  }),
  z.object({ type: z.literal("axiom_error"), message: z.string().max(512) }),
]);

export type BridgeMessageType = z.infer<typeof BridgeMessage>;

/** Validate a raw postMessage payload; null means silently drop (and count). */
export function parseBridgeMessage(data: unknown): BridgeMessageType | null {
  const result = BridgeMessage.safeParse(data);
  return result.success ? result.data : null;
}
