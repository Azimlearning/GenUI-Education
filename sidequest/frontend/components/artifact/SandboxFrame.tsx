"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { parseBridgeMessage } from "@/lib/bridge";

const READY_TIMEOUT_MS = 5000;
const MAX_EVENTS_PER_SECOND = 10;

/**
 * The sandboxed artifact runtime (SECURITY.md section 2, permanent decisions):
 * sandbox="allow-scripts" ONLY, never allow-same-origin. srcdoc + allow-scripts
 * yields an opaque origin; that is the load-bearing control. The bridge is
 * one-way (iframe -> parent): validated with zod, source-checked, rate-limited.
 * Watchdog: no axiom_ready within 5s, or any axiom_error, degrades the card.
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
    <div
      className="mt-3 overflow-hidden rounded-lg border"
      style={{ borderColor: "var(--rule)", background: "var(--bg-raised)" }}
    >
      <div
        className="flex items-center justify-between border-b px-3 py-2"
        style={{ borderColor: "var(--rule)" }}
      >
        <span className="text-sm font-medium">{title}</span>
        <button
          type="button"
          onClick={reset}
          className="rounded px-3 py-1.5 text-xs"
          style={{ border: "1px solid var(--rule)", color: "var(--ink-dim)" }}
        >
          Reset
        </button>
      </div>
      <iframe
        key={epoch}
        ref={iframeRef}
        sandbox="allow-scripts"
        srcDoc={html}
        title={title}
        className="block h-[min(480px,65dvh)] w-full"
        style={{ border: "0", opacity: ready ? 1 : 0.4, transition: "opacity 300ms" }}
      />
    </div>
  );
}
