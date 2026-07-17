"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { parseBridgeMessage } from "@/lib/bridge";
import { Mascot } from "@/components/Mascot";

const READY_TIMEOUT_MS = 5000;
const MAX_EVENTS_PER_SECOND = 10;

/**
 * The sandboxed artifact runtime (SECURITY.md section 2, permanent decisions):
 * sandbox="allow-scripts" ONLY, never allow-same-origin. srcdoc + allow-scripts
 * yields an opaque origin; that is the load-bearing control. The bridge is
 * one-way (iframe -> parent): validated with zod, source-checked, rate-limited.
 * Watchdog: no axiom_ready within 5s, or any axiom_error, degrades the card.
 *
 * Chrome only (design/FLOW.md section 4): the frame reads "confirmed" (green edge),
 * and the checkpoint is celebrated with a "Science checked" badge plus a little XP.
 */
export function SandboxFrame({
  html,
  title,
  onCrash,
}: {
  html: string;
  title: string;
  onCrash: (message: string) => void;
}) {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [epoch, setEpoch] = useState(0); // bump to remount (reset button)
  const [ready, setReady] = useState(false);

  const onCrashRef = useRef(onCrash);
  onCrashRef.current = onCrash;

  useEffect(() => {
    setReady(false);
    const watchdog = window.setTimeout(() => {
      onCrashRef.current("The interactive piece did not start in time.");
    }, READY_TIMEOUT_MS);

    let recentEvents = 0;
    const rateWindow = window.setInterval(() => {
      recentEvents = 0;
    }, 1000);
    let dropped = 0;

    function onMessage(event: MessageEvent) {
      // Accept only messages from the mounted artifact iframe itself.
      if (!iframeRef.current || event.source !== iframeRef.current.contentWindow) return;
      const msg = parseBridgeMessage(event.data);
      if (!msg) {
        dropped++;
        return;
      }
      switch (msg.type) {
        case "axiom_ready":
          window.clearTimeout(watchdog);
          setReady(true);
          break;
        case "axiom_error":
          window.clearTimeout(watchdog);
          onCrashRef.current(msg.message);
          break;
        case "axiom_event":
          if (recentEvents >= MAX_EVENTS_PER_SECOND) return;
          recentEvents++;
          // Phase 5 forwards these to POST /api/artifact/{id}/event for the
          // Tutor loop; until then they are observability only.
          console.debug("axiom_event", msg.control, msg.value);
          break;
      }
    }

    window.addEventListener("message", onMessage);
    return () => {
      window.removeEventListener("message", onMessage);
      window.clearTimeout(watchdog);
      window.clearInterval(rateWindow);
      if (dropped > 0) console.warn(`bridge: dropped ${dropped} invalid message(s)`);
    };
  }, [epoch, html]);

  const reset = useCallback(() => setEpoch((e) => e + 1), []);

  return (
    <div className="overflow-hidden rounded-card border-2 border-verify-soft bg-card shadow-[0_4px_0_var(--verify-soft)]">
      <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-2 border-b-2 border-line px-4 py-2.5">
        <span className="flex items-center gap-2 font-display text-[15px] font-semibold text-ink">
          {ready ? <Mascot mood="celebrate" size={32} bob={false} /> : null}
          {title}
        </span>
        <div className="flex items-center gap-2">
          {ready ? (
            <>
              <span className="pop rounded-full bg-gold-soft px-2.5 py-1 font-display text-[12px] font-bold text-gold">
                +10 XP
              </span>
              <span className="pop inline-flex items-center gap-1.5 rounded-full bg-verify px-2.5 py-1 pl-2 font-display text-[12px] font-semibold text-white shadow-[0_3px_0_var(--verify-edge)]">
                <svg width="13" height="13" viewBox="0 0 16 16" fill="none" aria-hidden>
                  <path
                    d="M4.5 8.2l2.3 2.3 4.7-5"
                    stroke="#fff"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                Science checked
              </span>
            </>
          ) : null}
          <button type="button" onClick={reset} className="btn btn-ghost px-3 py-1.5 text-xs">
            Reset
          </button>
        </div>
      </div>
      <iframe
        key={epoch}
        ref={iframeRef}
        sandbox="allow-scripts"
        srcDoc={html}
        title={title}
        className="block h-[min(480px,65dvh)] w-full bg-canvas"
        style={{ border: "0", opacity: ready ? 1 : 0.4, transition: "opacity 300ms" }}
      />
    </div>
  );
}
