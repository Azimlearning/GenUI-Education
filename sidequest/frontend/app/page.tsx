"use client";

import { useCallback, useMemo, useReducer, useRef, useState } from "react";

import { Composer } from "@/components/chat/Composer";
import { MessageList } from "@/components/chat/MessageList";
import { LabPane } from "@/components/study/LabPane";
import { StudyRail } from "@/components/study/StudyRail";
import { chatReducer, initialChatState } from "@/lib/reducer";
import { getSessionId } from "@/lib/session";
import { streamAsk } from "@/lib/sse";

export default function ChatPage() {
  const [state, dispatch] = useReducer(chatReducer, initialChatState);
  const [selectedLabIndex, setSelectedLabIndex] = useState<number | null>(null);
  // Mobile-only: the lab renders as a full-screen overlay, so it needs an
  // explicit open/closed state independent of desktop's grid takeover.
  const [mobileLabOpen, setMobileLabOpen] = useState(false);
  const busyRef = useRef(false);

  const send = useCallback(async (message: string) => {
    if (busyRef.current) return;
    busyRef.current = true;
    setSelectedLabIndex(null);
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
  const latestLabIndex = useMemo(() => {
    for (let i = state.messages.length - 1; i >= 0; i--) {
      const message = state.messages[i];
      if (message?.role === "assistant" && message.artifact.status !== "none") return i;
    }
    return null;
  }, [state.messages]);
  const labIndex = selectedLabIndex ?? latestLabIndex;
  const labMessage =
    labIndex !== null && state.messages[labIndex]?.role === "assistant"
      ? state.messages[labIndex]
      : null;
  // Takeover begins the moment the pipeline commits to an artifact (the
  // first artifact_status event flips status away from "none"), not only
  // once it's ready, so the lazy-loading state itself fills the pane.
  const labActive = labMessage !== null && labMessage.artifact.status !== "none";

  // Re-open the mobile overlay whenever a NEW lab becomes active (a fresh
  // question just started building one), without fighting a user who
  // deliberately closed it to keep reading the current one.
  const lastAutoOpenedIndex = useRef<number | null>(null);
  if (labActive && labIndex !== null && lastAutoOpenedIndex.current !== labIndex) {
    lastAutoOpenedIndex.current = labIndex;
    if (!mobileLabOpen) setMobileLabOpen(true);
  }

  const openLab = useCallback((index: number) => {
    setSelectedLabIndex(index);
    setMobileLabOpen(true);
  }, []);

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

  return (
    <main
      className={
        "grid min-h-dvh overflow-x-hidden transition-[grid-template-columns] duration-300 ease-out " +
        (labActive
          ? "xl:grid-cols-[0px_1fr_4fr]"
          : "xl:grid-cols-[272px_minmax(420px,0.9fr)_minmax(460px,1.1fr)]")
      }
    >
      <div className="overflow-hidden">
        <StudyRail onPrompt={(prompt) => void send(prompt)} disabled={busy} />
      </div>

      <section className="flex min-h-dvh min-w-0 flex-col px-4 sm:px-6 xl:px-6">
        <header className="flex items-center justify-between border-b py-5" style={{ borderColor: "var(--rule)" }}>
          <div className={labActive ? "xl:hidden" : ""}>
            <p className="study-kicker xl:hidden">AXIOM / STUDY STUDIO</p>
            <h1 className="font-serif text-2xl xl:hidden">Make science stick.</h1>
            <p className="text-sm" style={{ color: "var(--ink-dim)" }}>
              A short explanation first. A hands-on lab beside it.
            </p>
          </div>
          <span className="study-badge">notebook</span>
        </header>

        <MessageList messages={state.messages} status={state.status} onOpenLab={openLab} compact={labActive} />

        {state.status === "error" && state.error ? (
          <p role="alert" className="pb-2 text-sm text-red-400">{state.error}</p>
        ) : null}

        <Composer onSend={send} disabled={busy} />
      </section>

      <LabPane
        message={labMessage}
        mobileOpen={mobileLabOpen}
        onCloseMobile={() => setMobileLabOpen(false)}
        onRetry={() => labIndex !== null && retryFrom(labIndex)}
        onCrash={(message) => labIndex !== null && crashArtifact(labIndex, message)}
      />
    </main>
  );
}
