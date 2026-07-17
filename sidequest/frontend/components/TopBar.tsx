"use client";

import { useEffect, useState } from "react";

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

function ThemeToggle() {
  const [theme, setTheme] = useState<"light" | "dark">("light");
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    const current =
      (document.documentElement.dataset.theme as "light" | "dark" | undefined) ??
      (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    setTheme(current);
    setMounted(true);
  }, []);

  const applyTheme = (next: "light" | "dark") => {
    document.documentElement.dataset.theme = next;
    try {
      localStorage.setItem("axiom-theme", next);
    } catch {
      /* private mode: session-only, no persistence */
    }
  };

  const toggle = () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);

    const doc = document as Document & {
      startViewTransition?: (cb: () => void) => { ready: Promise<void> };
    };
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    // No View Transitions support (or reduced motion): swap instantly.
    if (!doc.startViewTransition || reduce) {
      applyTheme(next);
      return;
    }

    // The sweep: the new theme is revealed by a circle expanding from the centre.
    const transition = doc.startViewTransition(() => applyTheme(next));
    transition.ready
      .then(() => {
        document.documentElement.animate(
          { clipPath: ["circle(0% at 50% 0%)", "circle(160% at 50% 0%)"] },
          {
            duration: 820,
            easing: "cubic-bezier(0.65, 0, 0.35, 1)",
            pseudoElement: "::view-transition-new(root)",
          }
        );
      })
      .catch(() => {
        /* transition skipped (e.g. tab hidden): theme already applied */
      });
  };

  const dark = theme === "dark";
  return (
    <button
      type="button"
      onClick={toggle}
      aria-label={dark ? "Switch to light mode" : "Switch to dark mode"}
      className="grid h-8 w-8 place-items-center rounded-full border-2 border-line bg-card text-ink-dim shadow-[0_2px_0_var(--line-2)] hover:text-ink"
    >
      {/* Render a stable icon until mounted to avoid a hydration mismatch. */}
      {mounted && dark ? (
        <svg width="17" height="17" viewBox="0 0 20 20" fill="none" aria-hidden>
          <circle cx="10" cy="10" r="4" stroke="currentColor" strokeWidth="1.6" />
          <path
            d="M10 1.5v2.5M10 16v2.5M18.5 10H16M4 10H1.5M15.5 4.5l-1.8 1.8M6.3 13.7l-1.8 1.8M15.5 15.5l-1.8-1.8M6.3 6.3L4.5 4.5"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinecap="round"
          />
        </svg>
      ) : (
        <svg width="17" height="17" viewBox="0 0 20 20" fill="none" aria-hidden>
          <path
            d="M16.5 11.5A6.5 6.5 0 0 1 8.5 3.5a6.5 6.5 0 1 0 8 8z"
            stroke="currentColor"
            strokeWidth="1.6"
            strokeLinejoin="round"
          />
        </svg>
      )}
    </button>
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

        <ThemeToggle />

        <span className="grid h-8 w-8 place-items-center rounded-full bg-primary-btn font-display text-[13px] font-bold text-white shadow-[0_3px_0_var(--primary-edge)]">
          A
        </span>
      </div>
    </header>
  );
}
