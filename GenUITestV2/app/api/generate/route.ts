import Anthropic from "@anthropic-ai/sdk";
import { NextResponse } from "next/server";
import { SYSTEM_PROMPT, RENDER_UI_TOOL } from "@/lib/uispec";

export const maxDuration = 120;

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export async function POST(req: Request) {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) {
    return NextResponse.json(
      {
        error:
          "ANTHROPIC_API_KEY is not set. Copy .env.local.example to .env.local and add your key.",
      },
      { status: 500 },
    );
  }

  let messages: ChatMessage[];
  try {
    const body = await req.json();
    messages = body.messages;
    if (!Array.isArray(messages) || messages.length === 0) throw new Error();
  } catch {
    return NextResponse.json(
      { error: "Body must be { messages: [{role, content}, ...] }" },
      { status: 400 },
    );
  }

  const client = new Anthropic({ apiKey });

  try {
    const response = await client.messages.create({
      model: process.env.GENUI_MODEL ?? "claude-sonnet-5",
      max_tokens: 8000,
      system: SYSTEM_PROMPT,
      tools: [RENDER_UI_TOOL],
      tool_choice: { type: "tool", name: "render_ui" },
      messages,
    });

    const toolUse = response.content.find((b) => b.type === "tool_use");
    if (!toolUse || toolUse.type !== "tool_use") {
      return NextResponse.json(
        { error: "Model did not return a UI spec." },
        { status: 502 },
      );
    }

    return NextResponse.json({ spec: toolUse.input, model: response.model });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown provider error";
    return NextResponse.json({ error: message }, { status: 502 });
  }
}
