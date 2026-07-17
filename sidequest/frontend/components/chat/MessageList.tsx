"use client";

import { useEffect, useRef } from "react";

import type { ChatMessage, ChatStatus } from "@/lib/reducer";
import { StreamRenderer } from "@/components/chat/StreamRenderer";

export function MessageList({
  messages,
  status,
  onOpenLab,
  compact,
}: {
  messages: ChatMessage[];
  status: ChatStatus;
  onOpenLab: (assistantIndex: number) => void;
  compact: boolean;
}) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ block: "end" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div
        className="flex flex-1 items-center justify-center text-sm"
        style={{ color: "var(--ink-dim)" }}
      >
        <div className="max-w-sm text-center">
          <p className="study-kicker">OPEN NOTEBOOK</p>
          <p className="mt-3 font-serif text-3xl" style={{ color: "var(--ink)" }}>
            What are you trying to understand?
          </p>
          <p className="mt-3 leading-relaxed">
            Ask one clear question. We&apos;ll turn it into a short study note and, when useful,
            an interactive lab.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 space-y-6 overflow-y-auto py-6" aria-live="polite">
      {messages.map((msg, i) =>
        msg.role === "user" ? (
          <div key={i} className="flex justify-end">
            <div
              className={
                (compact ? "text-xs " : "text-sm ") +
                "max-w-[85%] rounded-lg px-4 py-2"
              }
              style={{ background: "var(--bg-raised)", border: "1px solid var(--rule)" }}
            >
              {msg.content}
            </div>
          </div>
        ) : (
          <div key={i} className="study-response">
            <StreamRenderer message={msg} compact={compact} />
            {msg.artifact.status !== "none" ? (
              <button type="button" className="lab-link mt-4" onClick={() => onOpenLab(i)}>
                Open the interactive lab <span aria-hidden>→</span>
              </button>
            ) : null}
          </div>
        )
      )}
      {status === "waiting" ? (
        <p className="text-sm" style={{ color: "var(--ink-dim)" }}>
          thinking…
        </p>
      ) : null}
      <div ref={bottomRef} />
    </div>
  );
}
