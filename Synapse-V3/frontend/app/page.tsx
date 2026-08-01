"use client";

import { useCallback, useEffect, useMemo, useReducer, useRef, useState } from "react";

import { Composer } from "@/components/chat/Composer";
import { MessageList } from "@/components/chat/MessageList";
import { TopBar } from "@/components/TopBar";
import { LabPane } from "@/components/study/LabPane";
import { StudyRail } from "@/components/study/StudyRail";
import { listSavedLabs, removeLab, saveLab, type SavedLab } from "@/lib/labLibrary";
import { chatReducer, initialChatState, type ChatMessage } from "@/lib/reducer";
import { getSessionId } from "@/lib/session";
import { streamAsk } from "@/lib/sse";

type AssistantMessage = Extract<ChatMessage, { role: "assistant" }>;

export default function ChatPage() {
  const [state, dispatch] = useReducer(chatReducer, initialChatState);
  const [selectedLabIndex, setSelectedLabIndex] = useState<number | null>(null);
  // Mobile-only: the lab renders as a full-screen overlay, so it needs an
  // explicit open/closed state independent of desktop's grid takeover.
  const [mobileLabOpen, setMobileLabOpen] = useState(false);
  // The saved-labs library: verified artifacts kept in localStorage so
  // reopening one costs nothing. Loaded after mount (no SSR storage).
  const [savedLabs, setSavedLabs] = useState<SavedLab[]>([]);
  const [viewingSaved, setViewingSaved] = useState<SavedLab | null>(null);
  const busyRef = useRef(false);

  useEffect(() => {
    setSavedLabs(listSavedLabs());
  }, []);

  const send = useCallback(async (message: string) => {
    if (busyRef.current) return;
    busyRef.current = true;
    setSelectedLabIndex(null);
    setViewingSaved(null);
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

  // Every artifact that reaches "ready" has passed the Verifier; bank it in
  // the library automatically so it never has to be regenerated (and paid
  // for) again. The ref guards against re-saving on unrelated re-renders.
  const bankedIdsRef = useRef<Set<string>>(new Set());
  useEffect(() => {
    state.messages.forEach((msg, i) => {
      if (msg.role !== "assistant" || msg.artifact.status !== "ready") return;
      if (bankedIdsRef.current.has(msg.artifact.artifactId)) return;
      bankedIdsRef.current.add(msg.artifact.artifactId);
      let question = "";
      for (let j = i - 1; j >= 0; j--) {
        const prev = state.messages[j];
        if (prev && prev.role === "user") {
          question = prev.content;
          break;
        }
      }
      setSavedLabs(
        saveLab({
          id: msg.artifact.artifactId,
          title: msg.artifact.title,
          question,
          html: msg.artifact.html,
          meta: msg.meta,
          verified: msg.artifact.verified,
          savedAt: Date.now(),
        })
      );
    });
  }, [state.messages]);

  const latestLabIndex = useMemo(() => {
    for (let i = state.messages.length - 1; i >= 0; i--) {
      const message = state.messages[i];
      if (message?.role === "assistant" && message.artifact.status !== "none") return i;
    }
    return null;
  }, [state.messages]);
  const labIndex = selectedLabIndex ?? latestLabIndex;
  // A reopened saved lab renders through the exact same LabPane/SandboxFrame
  // path as a live one, as a synthetic already-ready assistant message.
  const savedLabMessage: AssistantMessage | null = viewingSaved
    ? {
        role: "assistant",
        content: "",
        streaming: false,
        meta: viewingSaved.meta,
        artifact: {
          status: "ready",
          artifactId: viewingSaved.id,
          title: viewingSaved.title,
          html: viewingSaved.html,
          verified: viewingSaved.verified,
        },
      }
    : null;
  const labMessage =
    savedLabMessage ??
    (labIndex !== null && state.messages[labIndex]?.role === "assistant"
      ? state.messages[labIndex]
      : null);
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
    setViewingSaved(null);
    setSelectedLabIndex(index);
    setMobileLabOpen(true);
  }, []);

  const openSavedLab = useCallback((lab: SavedLab) => {
    setViewingSaved(lab);
    setMobileLabOpen(true);
  }, []);

  const deleteSavedLab = useCallback((id: string) => {
    setSavedLabs(removeLab(id));
    setViewingSaved((current) => (current?.id === id ? null : current));
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

  // The lab bench only enters the layout once a question has actually been
  // asked (or a saved lab was reopened); before that its column doesn't
  // exist, not just sit there empty.
  const started = state.messages.length > 0 || viewingSaved !== null;

  return (
    <div className="flex h-dvh flex-col overflow-hidden">
      <TopBar />
      <main
        className={
          "grid min-h-0 flex-1 overflow-x-hidden transition-[grid-template-columns] duration-300 ease-out " +
          (!started
            ? "xl:grid-cols-[272px_1fr]"
            : labActive
              ? "xl:grid-cols-[0px_1fr_4fr]"
              : "xl:grid-cols-[272px_minmax(420px,0.9fr)_minmax(460px,1.1fr)]")
        }
      >
      <div className="min-h-0 overflow-y-auto">
        <StudyRail
          onPrompt={(prompt) => void send(prompt)}
          disabled={busy}
          savedLabs={savedLabs}
          onOpenSaved={openSavedLab}
          onDeleteSaved={deleteSavedLab}
        />
      </div>

      <section className="flex min-h-0 min-w-0 flex-col px-4 sm:px-6 xl:px-6">
        <header className="flex items-center justify-between border-b py-5 xl:hidden" style={{ borderColor: "var(--rule)" }}>
          <div className={labActive ? "xl:hidden" : ""}>
            <h1 className="font-serif text-2xl xl:hidden">Make science stick.</h1>
          </div>
        </header>

        <MessageList messages={state.messages} status={state.status} onOpenLab={openLab} compact={labActive} />

        {state.status === "error" && state.error ? (
          <p role="alert" className="pb-2 text-sm text-red-400">{state.error}</p>
        ) : null}

        <Composer onSend={send} disabled={busy} />
      </section>

      {started ? (
        <LabPane
          message={labMessage}
          mobileOpen={mobileLabOpen}
          onCloseMobile={() => setMobileLabOpen(false)}
          onRetry={() => {
            // A saved lab has no live message to retry from; re-ask its
            // original question instead (a fresh, paid pipeline run).
            if (viewingSaved) {
              if (viewingSaved.question) void send(viewingSaved.question);
              return;
            }
            if (labIndex !== null) retryFrom(labIndex);
          }}
          onCrash={(message) => {
            if (viewingSaved) {
              // A banked lab that crashes on replay is stale; drop it.
              deleteSavedLab(viewingSaved.id);
              return;
            }
            if (labIndex !== null) crashArtifact(labIndex, message);
          }}
        />
      ) : null}
      </main>
    </div>
  );
}
