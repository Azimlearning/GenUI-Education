/**
 * Provider router.
 *
 * Every LLM call in the app goes through here. No pipeline step names a vendor:
 * it names a ROLE ("fast", "strong"), and the config below decides who answers.
 * Reordering providers, or dropping one entirely, is a config edit.
 *
 * Two call shapes:
 *   runStructured() — forced tool call in, validated Zod object out.
 *   runStreaming()  — raw text out, token by token (Tier C).
 *
 * Keys are server-side only. Never NEXT_PUBLIC_.
 */

import Anthropic from "@anthropic-ai/sdk";
import OpenAI from "openai";
import type { z } from "zod";

export type Role = "fast" | "strong";

interface ProviderConfig {
  vendor: "anthropic" | "openai";
  model: string;
  max_tokens: number;
}

/**
 * Ordered chains. First entry is primary; the rest are tried in order on
 * failure. Claude is the verified path (GenUITestV2 live tests, 2026-07-06).
 */
const CHAINS: Record<Role, ProviderConfig[]> = {
  // Planner/Checker/Brief run as one call and must feel instant.
  fast: [
    { vendor: "anthropic", model: "claude-haiku-4-5-20251001", max_tokens: 2000 },
    { vendor: "openai", model: "gpt-4o-mini", max_tokens: 2000 },
  ],
  // Generation. Worth the strongest model available.
  strong: [
    { vendor: "anthropic", model: "claude-sonnet-5", max_tokens: 16000 },
    { vendor: "openai", model: "gpt-4o", max_tokens: 8000 },
  ],
};

export interface CallLog {
  role: Role;
  vendor: string;
  model: string;
  ms: number;
  ok: boolean;
  error?: string;
}

/** Per-request call log. Feeds the debug panel and the responsible-AI story. */
export const callLog: CallLog[] = [];

function anthropic(): Anthropic | null {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  return apiKey ? new Anthropic({ apiKey }) : null;
}

function openai(): OpenAI | null {
  const apiKey = process.env.OPENAI_API_KEY;
  return apiKey ? new OpenAI({ apiKey }) : null;
}

export function hasAnyProvider(): boolean {
  return Boolean(process.env.ANTHROPIC_API_KEY || process.env.OPENAI_API_KEY);
}

export interface Message {
  role: "user" | "assistant";
  content: string;
}

/* -------------------------------------------------------- structured call */

interface StructuredArgs<T extends z.ZodType> {
  role: Role;
  system: string;
  messages: Message[];
  /** The tool the model is forced to call. */
  tool: { name: string; description: string; schema: Record<string, unknown> };
  /** Validates the tool input. The model's output is not trusted. */
  output: T;
}

/**
 * Force a tool call and validate its input.
 *
 * The forced call is what makes the output parseable — no prose-wrapped code
 * blocks to scrape. Validation is what makes it trustworthy.
 */
export async function runStructured<T extends z.ZodType>(
  args: StructuredArgs<T>,
): Promise<z.infer<T>> {
  const chain = CHAINS[args.role];
  let lastError = "no providers configured";

  for (const cfg of chain) {
    const started = Date.now();
    try {
      const raw =
        cfg.vendor === "anthropic"
          ? await callAnthropicTool(cfg, args)
          : await callOpenAITool(cfg, args);

      const parsed = args.output.safeParse(raw);
      if (!parsed.success) {
        throw new Error(
          `output failed validation: ${parsed.error.issues
            .map((i) => `${i.path.join(".")}: ${i.message}`)
            .join("; ")}`,
        );
      }

      callLog.push({
        role: args.role,
        vendor: cfg.vendor,
        model: cfg.model,
        ms: Date.now() - started,
        ok: true,
      });
      return parsed.data;
    } catch (err) {
      lastError = err instanceof Error ? err.message : String(err);
      callLog.push({
        role: args.role,
        vendor: cfg.vendor,
        model: cfg.model,
        ms: Date.now() - started,
        ok: false,
        error: lastError,
      });
      // Fall through to the next provider in the chain.
    }
  }

  throw new Error(`All providers failed for role "${args.role}": ${lastError}`);
}

async function callAnthropicTool<T extends z.ZodType>(
  cfg: ProviderConfig,
  args: StructuredArgs<T>,
): Promise<unknown> {
  const client = anthropic();
  if (!client) throw new Error("ANTHROPIC_API_KEY not set");

  const res = await client.messages.create({
    model: cfg.model,
    max_tokens: cfg.max_tokens,
    system: args.system,
    tools: [
      {
        name: args.tool.name,
        description: args.tool.description,
        input_schema: args.tool.schema as never,
      },
    ],
    tool_choice: { type: "tool", name: args.tool.name },
    messages: args.messages,
  });

  const block = res.content.find((b) => b.type === "tool_use");
  if (!block || block.type !== "tool_use") throw new Error("model returned no tool call");
  return block.input;
}

async function callOpenAITool<T extends z.ZodType>(
  cfg: ProviderConfig,
  args: StructuredArgs<T>,
): Promise<unknown> {
  const client = openai();
  if (!client) throw new Error("OPENAI_API_KEY not set");

  const res = await client.chat.completions.create({
    model: cfg.model,
    max_tokens: cfg.max_tokens,
    messages: [{ role: "system", content: args.system }, ...args.messages],
    tools: [
      {
        type: "function",
        function: {
          name: args.tool.name,
          description: args.tool.description,
          parameters: args.tool.schema,
        },
      },
    ],
    tool_choice: { type: "function", function: { name: args.tool.name } },
  });

  const call = res.choices[0]?.message?.tool_calls?.[0];
  if (!call || call.type !== "function") throw new Error("model returned no tool call");
  return JSON.parse(call.function.arguments);
}

/* --------------------------------------------------------- streaming call */

/**
 * Stream raw text. Used by Tier C so generated HTML can paint as it arrives
 * rather than landing after a 40 second hang.
 */
export async function* runStreaming(args: {
  role: Role;
  system: string;
  messages: Message[];
}): AsyncGenerator<string> {
  const chain = CHAINS[args.role];
  let lastError = "no providers configured";

  for (const cfg of chain) {
    const started = Date.now();
    try {
      if (cfg.vendor === "anthropic") {
        const client = anthropic();
        if (!client) throw new Error("ANTHROPIC_API_KEY not set");
        const stream = client.messages.stream({
          model: cfg.model,
          max_tokens: cfg.max_tokens,
          system: args.system,
          messages: args.messages,
        });
        for await (const chunk of stream) {
          if (
            chunk.type === "content_block_delta" &&
            chunk.delta.type === "text_delta"
          ) {
            yield chunk.delta.text;
          }
        }
      } else {
        const client = openai();
        if (!client) throw new Error("OPENAI_API_KEY not set");
        const stream = await client.chat.completions.create({
          model: cfg.model,
          max_tokens: cfg.max_tokens,
          stream: true,
          messages: [{ role: "system", content: args.system }, ...args.messages],
        });
        for await (const chunk of stream) {
          const text = chunk.choices[0]?.delta?.content;
          if (text) yield text;
        }
      }

      callLog.push({
        role: args.role,
        vendor: cfg.vendor,
        model: cfg.model,
        ms: Date.now() - started,
        ok: true,
      });
      return;
    } catch (err) {
      lastError = err instanceof Error ? err.message : String(err);
      callLog.push({
        role: args.role,
        vendor: cfg.vendor,
        model: cfg.model,
        ms: Date.now() - started,
        ok: false,
        error: lastError,
      });
      // Next provider. Note: if the first provider already yielded tokens the
      // consumer has seen a partial answer; Tier C discards partials on error.
    }
  }

  throw new Error(`All providers failed for role "${args.role}": ${lastError}`);
}
