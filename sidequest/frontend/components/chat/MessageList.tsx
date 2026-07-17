"use client";

import { useEffect, useRef } from "react";

import type { ChatMessage, ChatStatus } from "@/lib/reducer";
import { ArtifactCard } from "@/components/artifact/ArtifactCard";
import { StreamRenderer } from "@/components/chat/StreamRenderer";

export function MessageList({
  messages,
  status,
  onRetry,
  onCrash,
}: {
  messages: ChatMessage[];
  status: ChatStatus;
  onRetry: (assistantIndex: number) => void;
  onCrash: (assistantIndex: number, message: string) => void;
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
        Nothing asked yet. The notebook is open.
      </div>
    );
  }

  return (
    <div className="flex-1 space-y-6 overflow-y-auto py-6" aria-live="polite">
      {messages.map((msg, i) =>
        msg.role === "user" ? (
          <div key={i} className="flex justify-end">
            <div
              className="max-w-[85%] rounded-lg px-4 py-2 text-sm"
              style={{ background: "var(--bg-raised)", border: "1px solid var(--rule)" }}
            >
              {msg.content}
            </div>
          </div>
        ) : (
          <div key={i}>
            <StreamRenderer message={msg} />
            <ArtifactCard
              artifact={msg.artifact}
              onRetry={() => onRetry(i)}
              onCrash={(message) => onCrash(i, message)}
            />
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
