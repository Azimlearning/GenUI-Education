"use client";

/** The learning-app chrome (design/FLOW.md section 0): the wordmark, plus light
 *  motivators (streak, gems) so Axiom reads as a place you come back to. The
 *  counters are non-interactive labels, never nag banners. */
export function Logomark({ size = 28 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none" aria-hidden>
      <g transform="translate(16 16)">
        <ellipse rx="13.5" ry="5.6" fill="none" stroke="var(--primary)" strokeWidth="1.7" transform="rotate(-22)" />
        <ellipse rx="13.5" ry="5.6" fill="none" stroke="#c7d0cc" strokeWidth="1.4" transform="rotate(52)" />
        <circle r="3.6" fill="var(--ink)" />
      </g>
    </svg>
  );
}

export function TopBar() {
  return (
    <header className="sticky top-0 z-20 border-b-2 border-line bg-canvas">
      <div className="mx-auto flex max-w-5xl items-center gap-5 px-4 py-2.5 sm:px-6">
        <div className="mr-auto flex items-center gap-2.5">
          <Logomark />
          <span className="font-display text-[22px] font-bold tracking-tight text-ink">
            Axiom
          </span>
        </div>

        <span
          className="inline-flex items-center gap-1.5 font-display text-[15px] font-semibold text-gold"
          title="5 day streak"
        >
          <svg width="17" height="17" viewBox="0 0 20 20" fill="none" aria-hidden>
            <path
              d="M10 2c1 3-1 4-1 6a3 3 0 0 0 6 0c0-1 0-2-.5-3 2 2 3 4 3 6a7 7 0 1 1-14 0c0-3 2-5 3.5-7C8 7 8 5 10 2z"
              fill="currentColor"
            />
          </svg>
          5
        </span>

        <span
          className="hidden items-center gap-1.5 font-display text-[15px] font-semibold text-primary sm:inline-flex"
          title="gems"
        >
          <svg width="17" height="17" viewBox="0 0 20 20" fill="none" aria-hidden>
            <path d="M5 3h10l3 4-8 10L2 7z" fill="currentColor" />
            <path
              d="M5 3l5 4 5-4M2 7h16M10 17V7"
              stroke="#fff"
              strokeWidth="1"
              strokeLinejoin="round"
              opacity="0.55"
            />
          </svg>
          120
        </span>

        <span className="grid h-8 w-8 place-items-center rounded-full bg-primary-btn font-display text-[13px] font-bold text-white shadow-[0_3px_0_var(--primary-edge)]">
          A
        </span>
      </div>
    </header>
  );
}
