"use client";

import type { ChatMessage } from "@/lib/reducer";

type AssistantMessage = Extract<ChatMessage, { role: "assistant" }>;

export function StreamRenderer({ message }: { message: AssistantMessage }) {
  return (
    <div className="max-w-[85%]">
      {message.meta ? (
        <p className="mb-1 text-xs uppercase tracking-wider" style={{ color: "var(--ink-dim)" }}>
          {message.meta.intent.domain.replace("_", " ")} ·{" "}
          {message.meta.intent.artifact_type.replace(/_/g, " ")}
        </p>
      ) : null}
      <div
        className={`whitespace-pre-wrap text-[15px] leading-relaxed${
          message.streaming ? " caret" : ""
        }`}
      >
        {message.content}
      </div>
    </div>
  );
}
