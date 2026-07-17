"use client";

import { useCallback, useReducer, useRef } from "react";

import { Composer } from "@/components/chat/Composer";
import { MessageList } from "@/components/chat/MessageList";
import { Mascot } from "@/components/Mascot";
import { TopBar } from "@/components/TopBar";
import { chatReducer, initialChatState } from "@/lib/reducer";
import { getSessionId } from "@/lib/session";
import { streamAsk } from "@/lib/sse";

const EXAMPLES = [
  "How does a kidney clean blood?",
  "What is total internal reflection?",
  "Why is the sky blue?",
];

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

  // Retry re-asks the user question that produced this assistant message.
  const retryFrom = useCallback(
    (assistantIndex: number) => {
      for (let i = assistantIndex - 1; i >= 0; i--) {
        const msg = state.messages[i];
        if (msg && msg.role === "user") {
          void send(msg.content);
          return;
        }
      }
    },
    [state.messages, send]
  );

  const crashArtifact = useCallback((index: number, message: string) => {
    dispatch({ type: "artifact_crashed", index, message });
  }, []);

  const empty = state.messages.length === 0;

  return (
    <div className="flex min-h-dvh flex-col">
      <TopBar />

      {empty ? (
        /* The front door (design/FLOW.md section 1): a centred learning screen. */
        <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col justify-center px-5 pb-16 pt-8">
          <div className="flex items-end gap-3">
            <Mascot mood="happy" size={92} />
            <div className="relative mb-2 rounded-2xl border-2 border-[#cbe7e1] bg-primary-soft px-4 py-2.5 font-display text-[15px] font-semibold text-primary-btn">
              Hi, I&apos;m Axi. What should we figure out today?
              <span className="absolute -left-1.5 bottom-3 h-3 w-3 rotate-45 border-b-2 border-l-2 border-[#cbe7e1] bg-primary-soft" />
            </div>
          </div>

          <h1 className="mt-6 font-display text-[clamp(34px,7vw,52px)] font-semibold leading-[1.05] text-ink">
            Ask a question. Watch it get built, and{" "}
            <span className="text-verify-ink">checked</span>.
          </h1>
          <p className="mt-4 max-w-xl text-lg text-ink-dim">
            Axiom designs a working experiment for your question, checks the science is
            right, and hands it to you to play with.
          </p>

          <div className="mt-8">
            <Composer onSend={send} disabled={busy} variant="hero" />
          </div>

          <div className="mt-4 flex flex-wrap gap-2.5">
            {EXAMPLES.map((q) => (
              <button
                key={q}
                type="button"
                onClick={() => send(q)}
                disabled={busy}
                className="rounded-full border-2 border-line bg-card px-4 py-2 text-[13.5px] font-bold text-ink-dim shadow-[0_3px_0_var(--line)] transition-transform active:translate-y-[3px] active:shadow-[0_0_0_var(--line)] disabled:opacity-50"
              >
                {q}
              </button>
            ))}
          </div>
        </main>
      ) : (
        /* A live question: the stage takes over. */
        <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col px-4 sm:px-6">
          <MessageList
            messages={state.messages}
            status={state.status}
            onRetry={retryFrom}
            onCrash={crashArtifact}
          />

          {state.status === "error" && state.error ? (
            <p role="alert" className="pb-2 text-sm font-semibold text-danger">
              {state.error}
            </p>
          ) : null}

          <div className="sticky bottom-0 bg-canvas">
            <div className="mx-auto max-w-2xl">
              <Composer onSend={send} disabled={busy} />
            </div>
          </div>
        </main>
      )}
    </div>
  );
}
