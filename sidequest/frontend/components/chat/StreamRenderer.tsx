"use client";

import type { ChatMessage } from "@/lib/reducer";

type AssistantMessage = Extract<ChatMessage, { role: "assistant" }>;

/** Axiom talking, not a chat bubble (design/FLOW.md section 3a). Set for reading:
 *  a comfortable measure, the teal caret while it streams. */
export function StreamRenderer({ message }: { message: AssistantMessage }) {
  return (
    <div className="max-w-[68ch]">
      {message.meta ? (
        <p className="mb-2 font-mono text-[11px] uppercase tracking-[0.09em] text-ink-faint">
          {message.meta.intent.domain.replace("_", " ")} ·{" "}
          {message.meta.intent.artifact_type.replace(/_/g, " ")}
        </p>
      ) : null}
      <div
        className={`whitespace-pre-wrap text-[16.5px] leading-relaxed text-ink${
          message.streaming ? " caret" : ""
        }`}
      >
        {message.content}
      </div>
    </div>
  );
}
