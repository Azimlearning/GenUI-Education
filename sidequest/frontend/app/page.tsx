"use client";

import { useCallback, useReducer, useRef } from "react";

import { Composer } from "@/components/chat/Composer";
import { MessageList } from "@/components/chat/MessageList";
import { chatReducer, initialChatState } from "@/lib/reducer";
import { getSessionId } from "@/lib/session";
import { streamAsk } from "@/lib/sse";

export default function ChatPage() {
  const [state, dispatch] = useReducer(chatReducer, initialChatState);
  const busyRef = useRef(false);

  const send = useCallback(async (message: string) => {
    if (busyRef.current) return;
    busyRef.current = true;
    dispatch({ type: "user_sent", message });
    try {
      await streamAsk({
        sessionId: getSessionId(),
        message,
        onEvent: (event) => dispatch({ type: "stream_event", event }),
      });
    } catch (err) {
      dispatch({
        type: "stream_error",
        message: err instanceof Error ? err.message : "connection lost",
      });
    } finally {
      busyRef.current = false;
      dispatch({ type: "stream_closed" });
    }
  }, []);

  const busy = state.status === "waiting" || state.status === "streaming";

  return (
    <main className="mx-auto flex h-dvh max-w-3xl flex-col px-4">
      <header className="border-b py-4" style={{ borderColor: "var(--rule)" }}>
        <h1 className="text-lg font-semibold tracking-wide">Axiom</h1>
        <p className="text-sm" style={{ color: "var(--ink-dim)" }}>
          Ask a science question. Why does ice float? How do orbits work?
        </p>
      </header>

      <MessageList messages={state.messages} status={state.status} />

      {state.status === "error" && state.error ? (
        <p role="alert" className="pb-2 text-sm text-red-400">
          {state.error}
        </p>
      ) : null}

      <Composer onSend={send} disabled={busy} />
    </main>
  );
}
