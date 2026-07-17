"use client";

/** The latency mask: genuinely informative pipeline stages, not a fake spinner. */
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
  return (
    <div
      className="mt-3 rounded-lg border px-4 py-3"
      style={{ borderColor: "var(--rule)", background: "var(--bg-raised)" }}
      role="status"
      aria-live="polite"
    >
      <ol className="space-y-1.5">
        {STAGES.filter(([key]) => key !== "revising" || stage === "revising").map(
          ([key, label]) => {
            const index = STAGES.findIndex(([k]) => k === key);
            const state =
              index < activeIndex ? "done" : index === activeIndex ? "active" : "pending";
            return (
              <li key={key} className="flex items-center gap-2 text-sm">
                <span
                  aria-hidden
                  className="inline-block h-2 w-2 rounded-full"
                  style={{
                    background:
                      state === "done"
                        ? "var(--accent)"
                        : state === "active"
                          ? "var(--ink)"
                          : "var(--rule)",
                  }}
                />
                <span
                  style={{
                    color: state === "pending" ? "var(--ink-dim)" : "var(--ink)",
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
        <details className="mt-2">
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
  );
}
