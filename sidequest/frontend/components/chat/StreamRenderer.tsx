"use client";

import type { ChatMessage } from "@/lib/reducer";

type AssistantMessage = Extract<ChatMessage, { role: "assistant" }>;

export function StreamRenderer({
  message,
  compact,
}: {
  message: AssistantMessage;
  compact: boolean;
}) {
  return (
    <div className={compact ? "max-w-full" : "max-w-[96%]"}>
      {message.meta && !compact ? (
        // The lab pane header shows the same badges once a lab is active
        // (UX_IMPROVEMENT_PLAN.md W5); skip the duplicate here to cut text.
        <div className="mb-3 flex flex-wrap gap-2">
          <span className="study-badge">{message.meta.intent.domain.replace("_", " ")}</span>
          <span className="study-badge">
            {message.meta.intent.artifact_type.replace(/_/g, " ")}
          </span>
        </div>
      ) : null}
      {!compact ? <p className="study-kicker mb-2">QUICK STUDY NOTE</p> : null}
      <div
        className={
          (compact ? "text-[13px] leading-6 " : "text-[15px] leading-7 ") +
          "whitespace-pre-wrap" +
          (message.streaming ? " caret" : "")
        }
        style={compact ? { color: "var(--ink-dim)" } : undefined}
      >
        {message.content}
      </div>
    </div>
  );
}
