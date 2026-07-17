"use client";

/** The latency mask: genuinely informative pipeline stages, not a fake spinner.
 *  Fills the whole lab pane (UX_IMPROVEMENT_PLAN.md W2: "real lazy-loading",
 *  not a small inline box) with a shimmering skeleton of where the finished
 *  artifact will land, so the takeover feels intentional while it builds. */
const STAGES: [string, string][] = [
  ["planning", "designing the experiment"],
  ["generating", "building the interactive"],
  ["verifying", "checking the science"],
  ["revising", "revising after review"],
  ["postprocessing", "polishing"],
];

export function ProgressStages({
  stage,
  codePreview,
}: {
  stage: string;
  codePreview: string;
}) {
  const activeIndex = STAGES.findIndex(([key]) => key === stage);
  const activeLabel = STAGES[activeIndex]?.[1] ?? "getting started";

  return (
    <div className="flex h-full min-h-[430px] flex-col gap-5" role="status" aria-live="polite">
      <div className="skeleton-card flex-1 min-h-[220px]">
        <div className="skeleton-shimmer skeleton-block-title" />
        <div className="skeleton-shimmer skeleton-block-stage" />
        <div className="mt-4 flex gap-3">
          <div className="skeleton-shimmer skeleton-block-control" />
          <div className="skeleton-shimmer skeleton-block-control" />
        </div>
      </div>

      <div className="skeleton-stagelist">
        <p className="study-kicker mb-3">{activeLabel}…</p>
        <ol className="space-y-2.5">
          {STAGES.filter(([key]) => key !== "revising" || stage === "revising").map(
            ([key, label]) => {
              const index = STAGES.findIndex(([k]) => k === key);
              const state =
                index < activeIndex ? "done" : index === activeIndex ? "active" : "pending";
              return (
                <li key={key} className="flex items-center gap-3 text-sm">
                  <span
                    aria-hidden
                    className={"skeleton-dot skeleton-dot-" + state}
                  />
                  <span
                    style={{
                      color: state === "pending" ? "var(--ink-dim)" : "var(--ink)",
                      fontWeight: state === "active" ? 700 : 400,
                    }}
                  >
                    {label}
                    {state === "active" ? "…" : ""}
                  </span>
                </li>
              );
            }
          )}
        </ol>

        {codePreview ? (
          <details className="mt-4">
            <summary
              className="cursor-pointer select-none text-xs"
              style={{ color: "var(--ink-dim)" }}
            >
              watch the code being written
            </summary>
            <pre
              className="mt-1 max-h-40 overflow-hidden whitespace-pre-wrap break-all rounded p-2 text-[11px] leading-snug"
              style={{ background: "var(--bg)", color: "var(--ink-dim)" }}
              aria-hidden
            >
              {codePreview}
            </pre>
          </details>
        ) : null}
      </div>
    </div>
  );
}
