"use client";

import { Mascot } from "@/components/Mascot";

/** Honest failure state (design/FLOW.md section 5): the text explanation stays,
 *  the artifact admits defeat with dignity, retry re-runs the question. A warn
 *  left border, not danger. No reward here; we only celebrate a verified result.
 *  Axi looks sheepish, which turns a dead end into a warm moment. */
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
    <div className="mt-4 flex gap-3 rounded-card border-2 border-line border-l-[3px] border-l-warn bg-card px-5 py-4">
      <Mascot mood="oops" size={48} bob={false} className="mt-0.5 shrink-0" />
      <div>
        <p className="font-mono text-[10.5px] uppercase tracking-[0.08em] text-warn">
          Explanation only
        </p>
        <p className="mt-2 text-[15px] leading-relaxed text-ink-dim">{detail}</p>
        {retryable ? (
          <button
            type="button"
            onClick={onRetry}
            className="btn btn-ghost mt-3 min-h-[44px] px-4 text-sm"
          >
            Try again
          </button>
        ) : null}
      </div>
    </div>
  );
}
