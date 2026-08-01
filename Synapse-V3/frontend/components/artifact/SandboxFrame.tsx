"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { fitArtifactToFrame } from "@/lib/artifactFrame";
import { parseBridgeMessage } from "@/lib/bridge";

const READY_TIMEOUT_MS = 5000;
const MAX_EVENTS_PER_SECOND = 10;

/**
 * The sandboxed artifact runtime (SECURITY.md section 2, permanent decisions):
 * sandbox="allow-scripts" ONLY, never allow-same-origin. srcdoc + allow-scripts
 * yields an opaque origin; that is the load-bearing control. The bridge is
 * one-way (iframe -> parent): validated with zod, source-checked, rate-limited.
 * Watchdog: no synapse_ready within 5s, or any synapse_error, degrades the card.
 *
 * Chrome only (design/FLOW.md section 4): verified artifacts receive a green frame.
 */
export function SandboxFrame({
  html,
  title,
  verified,
  onCrash,
  className,
}: {
  html: string;
  title: string;
  verified: boolean;
  onCrash: (message: string) => void;
  className?: string;
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
        case "synapse_ready":
          window.clearTimeout(watchdog);
          setReady(true);
          break;
        case "synapse_error":
          window.clearTimeout(watchdog);
          onCrashRef.current(msg.message);
          break;
        case "synapse_event":
          if (recentEvents >= MAX_EVENTS_PER_SECOND) return;
          recentEvents++;
          // Phase 5 forwards these to POST /api/artifact/{id}/event for the
          // Tutor loop; until then they are observability only.
          console.debug("synapse_event", msg.control, msg.value);
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
    <div
      className={
        "flex h-full min-h-0 flex-col overflow-hidden rounded-card border-2 bg-card " +
        (verified
          ? "border-verify-soft shadow-[0_4px_0_var(--verify-soft)]"
          : "border-warn/40 shadow-[0_4px_0_var(--gold-soft)]") +
        (className ? ` ${className}` : "")
      }
    >
      <div className="flex shrink-0 flex-wrap items-center justify-between gap-x-3 gap-y-2 border-b-2 border-line px-4 py-2.5">
        <span className="flex items-center gap-2 font-display text-[15px] font-semibold text-ink">
          {title}
        </span>
        <div className="flex items-center gap-2">
          {ready && !verified ? (
            <span className="inline-flex items-center gap-1.5 rounded-full bg-gold-soft px-2.5 py-1 font-display text-[12px] font-semibold text-warn">
              Not fully checked
            </span>
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
        srcDoc={fitArtifactToFrame(html)}
        title={title}
        className="block min-h-0 flex-1 w-full bg-canvas"
        style={{ border: "0", opacity: ready ? 1 : 0.4, transition: "opacity 300ms" }}
      />
      {!verified ? (
        <p className="shrink-0 border-t-2 border-line px-4 py-2.5 text-[13px] leading-relaxed text-warn">
          Heads up: this one did not fully pass the science check, so it is shown as a draft.
          Double-check the numbers before you trust them, or hit Reset and ask again.
        </p>
      ) : null}
    </div>
  );
}
