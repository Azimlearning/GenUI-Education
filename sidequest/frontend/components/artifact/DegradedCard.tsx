"use client";

/** Honest failure state (principle 4): text explanation stays, artifact
 *  admits defeat, retry re-runs the question. Never show a broken artifact. */
export function DegradedCard({
  detail,
  retryable,
  onRetry,
}: {
  detail: string;
  retryable: boolean;
  onRetry: () => void;
}) {
  return (
    <div
      className="mt-3 rounded-lg border px-4 py-3"
      style={{ borderColor: "var(--rule)", background: "var(--bg-raised)" }}
    >
      <p className="text-sm" style={{ color: "var(--ink-dim)" }}>
        {detail}
      </p>
      {retryable ? (
        <button
          type="button"
          onClick={onRetry}
          className="mt-2 min-h-[44px] rounded-lg px-4 text-sm"
          style={{ border: "1px solid var(--rule)", color: "var(--ink)" }}
        >
          Try again
        </button>
      ) : null}
    </div>
  );
}
