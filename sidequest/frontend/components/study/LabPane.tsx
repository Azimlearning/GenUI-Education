"use client";

import { ArtifactCard } from "@/components/artifact/ArtifactCard";
import type { ChatMessage } from "@/lib/reducer";

type AssistantMessage = Extract<ChatMessage, { role: "assistant" }>;

function readable(value: string) {
  return value.replace(/_/g, " ");
}

export function LabPane({
  message,
  mobileOpen,
  onCloseMobile,
  onRetry,
  onCrash,
}: {
  message: AssistantMessage | null;
  mobileOpen: boolean;
  onCloseMobile: () => void;
  onRetry: () => void;
  onCrash: (message: string) => void;
}) {
  const artifact = message?.artifact;
  const hasArtifact = Boolean(artifact && artifact.status !== "none");
  const isExperiment = message?.meta?.intent.artifact_type === "virtual_experiment";
  // Below xl, the lab is a full-screen overlay while a question is active on
  // mobile; above xl it is always part of the grid (desktop takeover instead
  // widens its grid track, handled by the parent, not this component).
  const mobileOverlay = hasArtifact && mobileOpen;

  return (
    <aside
      className={
        (mobileOverlay
          ? "fixed inset-0 z-50 "
          : hasArtifact
            ? "hidden "
            : "min-h-[420px] border-t ") +
        "xl:static xl:z-auto xl:block xl:min-h-0 xl:border-l xl:border-t-0"
      }
      style={{ borderColor: "var(--rule)" }}
    >
      <div className="flex h-full flex-col bg-[var(--bg-lab)]">
        <header
          className="flex items-center justify-between border-b px-5 py-4"
          style={{ borderColor: "var(--rule)" }}
        >
          <div>
            <p className="study-kicker">INTERACTIVE WORKSPACE</p>
            <h2 className="mt-1 font-serif text-xl">Your lab bench</h2>
          </div>
          <div className="flex items-center gap-2">
            {message?.meta ? (
              <>
                <span className="study-badge study-badge-domain">
                  {readable(message.meta.intent.domain)}
                </span>
                <span className="study-badge study-badge-type">
                  {readable(message.meta.intent.artifact_type)}
                </span>
              </>
            ) : null}
            {mobileOverlay ? (
              <button
                type="button"
                onClick={onCloseMobile}
                className="lab-close-btn xl:hidden"
                aria-label="Back to explanation"
              >
                ← Back
              </button>
            ) : null}
          </div>
        </header>

        <div className="flex-1 p-4 xl:min-h-0">
          {artifact && artifact.status !== "none" ? (
            <ArtifactCard artifact={artifact} onRetry={onRetry} onCrash={onCrash} />
          ) : (
            <div className="lab-empty flex h-full min-h-[360px] flex-col justify-between p-6">
              <div>
                <p className="study-kicker">READY WHEN YOU ARE</p>
                <h3 className="mt-3 font-serif text-3xl leading-tight">Ask a question.<br />Make it tangible.</h3>
                <p className="mt-4 max-w-sm text-sm leading-relaxed" style={{ color: "var(--ink-dim)" }}>
                  Visual models, simulations, and experiments open here so your explanation stays easy to scan.
                </p>
              </div>
              <div className="grid grid-cols-3 gap-3 text-center text-xs" style={{ color: "var(--ink-dim)" }}>
                <div className="lab-symbol">∆<span>change</span></div>
                <div className="lab-symbol">→<span>observe</span></div>
                <div className="lab-symbol">✦<span>understand</span></div>
              </div>
            </div>
          )}
        </div>

        {isExperiment ? (
          <p className="mx-4 mb-4 rounded-lg px-3 py-2 text-xs leading-relaxed" style={{ background: "var(--bg-raised)", color: "var(--ink-dim)" }}>
            Lab cue: drag materials or tools onto the bench, then run a trial and compare the readout.
          </p>
        ) : null}
      </div>
    </aside>
  );
}
