"use client";

/** The latency mask made into momentum (design/FLOW.md section 3b): a filling
 *  bar, stages that check off teal into green, and the code appearing live.
 *  Genuinely informative, never a fake spinner. */
const STAGES: [string, string][] = [
  ["planning", "Designing the experiment"],
  ["generating", "Building the interactive"],
  ["verifying", "Checking the science"],
  ["revising", "Revising after review"],
  ["postprocessing", "Polishing"],
];

const Check = () => (
  <svg width="11" height="11" viewBox="0 0 12 12" fill="none" aria-hidden>
    <path
      d="M2.5 6.2l2.2 2.2L9.5 3.6"
      stroke="#fff"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

export function ProgressStages({
  stage,
  codePreview,
}: {
  stage: string;
  codePreview: string;
}) {
  // The "revising" step only exists in the rail when it is actually happening.
  const shown = STAGES.filter(([key]) => key !== "revising" || stage === "revising");
  const activeShownIndex = shown.findIndex(([key]) => key === stage);
  const activeIndex = STAGES.findIndex(([key]) => key === stage);
  const activeStage = activeIndex >= 0 ? STAGES[activeIndex] : undefined;
  const current = activeStage ? activeStage[1] : "Getting started";
  const stepNumber = activeShownIndex >= 0 ? activeShownIndex + 1 : 1;
  const percent = Math.round((stepNumber / shown.length) * 100);

  return (
    <div
      className="rounded-card border-2 border-line bg-canvas px-4 pb-4 pt-2"
      role="status"
      aria-live="polite"
    >
      <div className="flex items-center justify-between py-3">
        <span className="font-display text-sm font-semibold text-ink">{current}</span>
        <span className="rounded-full bg-primary-soft px-2.5 py-1 font-display text-[13px] font-semibold text-primary-btn">
          {stepNumber} of {shown.length}
        </span>
      </div>

      <div className="h-3 overflow-hidden rounded-full bg-line-2 shadow-inner">
        <div
          className="h-full rounded-full bg-primary transition-[width] duration-500"
          style={{ width: `${percent}%` }}
        />
      </div>

      <ol className="mt-3 space-y-0.5">
        {shown.map(([key, label]) => {
          const idx = STAGES.findIndex(([k]) => k === key);
          const state =
            idx < activeIndex ? "done" : idx === activeIndex ? "active" : "pending";
          return (
            <li key={key} className="grid grid-cols-[24px_1fr_auto] items-center gap-3 py-2">
              <span
                aria-hidden
                className={`grid h-[22px] w-[22px] place-items-center rounded-full ${
                  state === "done"
                    ? "bg-verify shadow-[0_2px_0_var(--verify-edge)]"
                    : state === "active"
                      ? "border-[3px] border-primary bg-card"
                      : "border-[3px] border-line-2 bg-card"
                }`}
              >
                {state === "done" ? (
                  <Check />
                ) : state === "active" ? (
                  <span className="node-pulse h-[7px] w-[7px] rounded-full bg-primary" />
                ) : null}
              </span>
              <span
                className={`text-[14.5px] font-semibold ${
                  state === "done"
                    ? "text-ink-dim"
                    : state === "active"
                      ? "text-ink"
                      : "text-ink-faint"
                }`}
              >
                {label}
              </span>
              <span
                className={`font-mono text-[10px] uppercase tracking-[0.06em] ${
                  state === "done"
                    ? "text-verify-ink"
                    : state === "active"
                      ? "text-primary-btn"
                      : "text-ink-faint"
                }`}
              >
                {state === "done" ? "done" : state === "active" ? "working" : "next"}
              </span>
            </li>
          );
        })}
      </ol>

      {codePreview ? (
        <details className="mt-2">
          <summary className="cursor-pointer select-none font-mono text-[11.5px] font-semibold text-ink-dim">
            Watch the code being written
          </summary>
          <pre
            className="mt-2.5 max-h-44 overflow-hidden whitespace-pre-wrap break-all rounded-ctl px-4 py-3 font-mono text-[11.5px] leading-snug"
            style={{ background: "#12211d", color: "#c7d6d1" }}
            aria-hidden
          >
            {codePreview}
          </pre>
        </details>
      ) : null}
    </div>
  );
}
