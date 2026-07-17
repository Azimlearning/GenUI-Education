"use client";

import { useEffect, useRef } from "react";

import type { ChatMessage, ChatStatus } from "@/lib/reducer";
import { ArtifactCard } from "@/components/artifact/ArtifactCard";
import { StreamRenderer } from "@/components/chat/StreamRenderer";
import { Mascot } from "@/components/Mascot";

const BackChevron = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden>
    <path
      d="M10 3l-5 5 5 5"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

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

  return (
    <div className="flex-1 space-y-8 overflow-y-auto py-8" aria-live="polite">
      {messages.map((msg, i) =>
        msg.role === "user" ? (
          <div key={i}>
            <div className="flex items-center gap-1.5 text-ink-faint">
              <BackChevron />
              <span className="font-mono text-[11px] font-semibold uppercase tracking-[0.08em]">
                Your question
              </span>
            </div>
            <h2 className="mt-1.5 font-display text-[27px] font-semibold leading-tight text-ink">
              {msg.content}
            </h2>
          </div>
        ) : (
          <div
            key={i}
            className={
              msg.artifact.status === "none"
                ? ""
                : "grid gap-6 lg:grid-cols-2 lg:items-start"
            }
          >
            <StreamRenderer message={msg} />
            {msg.artifact.status === "none" ? null : (
              <ArtifactCard
                artifact={msg.artifact}
                onRetry={() => onRetry(i)}
                onCrash={(message) => onCrash(i, message)}
              />
            )}
          </div>
        )
      )}
      {status === "waiting" ? (
        <div className="flex items-center gap-2.5 text-ink-dim">
          <Mascot mood="thinking" size={44} />
          <span className="text-sm font-semibold">Axi is thinking</span>
        </div>
      ) : null}
      <div ref={bottomRef} />
    </div>
  );
}
