"use client";

/**
 * The Tier C host.
 *
 * Everything here exists to hold one line: generated code never touches the host
 * DOM. It runs in an iframe with allow-scripts but NOT allow-same-origin, which
 * gives it an opaque origin — no reach into our cookies, storage, or document.
 * Messages out are untrusted input and are validated like any other.
 *
 * While generation streams, the raw partial paints into a provisional preview,
 * so a 40 second build reads as the AI working rather than as a hang.
 */

import { useEffect, useMemo, useRef, useState } from "react";
import { buildSrcdoc } from "@/lib/sandbox";

interface SandboxProps {
  html: string;
  streaming: boolean;
  onInteraction?: (action: string, values: Record<string, string | number | boolean>) => void;
}

export default function Sandbox({ html, streaming, onInteraction }: SandboxProps) {
  const frame = useRef<HTMLIFrameElement | null>(null);
  const [height, setHeight] = useState(420);
  const [error, setError] = useState<string | null>(null);

  // Only rebuild the document when the stream finishes. Re-writing srcdoc on
  // every token would restart the frame's scripts sixty times a second.
  const srcdoc = useMemo(() => (streaming ? null : buildSrcdoc(html)), [html, streaming]);

  useEffect(() => {
    const onMessage = (event: MessageEvent) => {
      // The frame is sandboxed to an opaque origin, so event.origin is "null"
      // and cannot be used to authenticate. Check the source handle instead:
      // only our own frame can be contentWindow.
      if (!frame.current || event.source !== frame.current.contentWindow) return;

      const data = event.data;
      if (!data || typeof data !== "object" || data.__synapse !== true) return;

      if (data.kind === "height" && typeof data.height === "number") {
        setHeight(Math.max(200, Math.min(1400, data.height + 8)));
        return;
      }

      if (data.kind === "error" && typeof data.message === "string") {
        setError(data.message);
        return;
      }

      if (data.kind === "interaction" && typeof data.action === "string") {
        // Values come from generated code: coerce to primitives and cap the
        // size rather than forwarding whatever shape arrived.
        const values: Record<string, string | number | boolean> = {};
        if (data.values && typeof data.values === "object") {
          for (const [k, v] of Object.entries(data.values).slice(0, 24)) {
            if (typeof v === "string") values[k] = v.slice(0, 200);
            else if (typeof v === "number" && Number.isFinite(v)) values[k] = v;
            else if (typeof v === "boolean") values[k] = v;
          }
        }
        onInteraction?.(data.action.slice(0, 200), values);
      }
    };

    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, [onInteraction]);

  if (streaming) {
    return <StreamingPreview html={html} />;
  }

  return (
    <div className="sandbox">
      <div className="sandbox-bar">
        <span className="sandbox-tag">Generated interactive</span>
        <span className="sandbox-note">sandboxed · no network · no access to this page</span>
      </div>
      <iframe
        ref={frame}
        className="sandbox-frame"
        style={{ height }}
        // allow-scripts WITHOUT allow-same-origin. Granting both together would
        // let the frame reach up and strip its own sandbox attribute.
        sandbox="allow-scripts"
        referrerPolicy="no-referrer"
        srcDoc={srcdoc ?? ""}
        title="Generated science interactive"
      />
      {error ? (
        <div className="sandbox-error">
          The generated interactive reported an error: <code>{error}</code>
        </div>
      ) : null}
    </div>
  );
}

/**
 * The provisional preview.
 *
 * Shows the shape of the lab as it's written — headings and controls appearing
 * one by one. Deliberately NOT rendered as live HTML: half a document is not a
 * document, and mounting partial markup means mounting partially-written script.
 */
function StreamingPreview({ html }: { html: string }) {
  const skeleton = useMemo(() => readShape(html), [html]);

  return (
    <div className="sandbox is-building">
      <div className="sandbox-bar">
        <span className="sandbox-tag is-live">
          <span className="pulse" />
          Writing your lab
        </span>
        <span className="sandbox-note">{html.length.toLocaleString()} chars</span>
      </div>
      <div className="preview">
        {skeleton.length === 0 ? (
          <>
            <div className="skel skel-title" />
            <div className="skel skel-line" />
            <div className="skel skel-line is-short" />
            <div className="skel skel-box" />
          </>
        ) : (
          skeleton.map((item, i) => (
            <div key={i} className={`preview-item is-${item.kind}`}>
              {item.text}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

/**
 * Read the structure out of a partially-written document.
 *
 * Regex over half-finished HTML is exactly as unreliable as it sounds, which is
 * why this only ever produces a preview: nothing here is rendered as markup.
 */
function readShape(html: string): { kind: string; text: string }[] {
  const items: { kind: string; text: string }[] = [];
  const patterns: [RegExp, string][] = [
    [/<title[^>]*>([^<]{2,80})<\/title>/gi, "title"],
    [/<h1[^>]*>([^<]{2,80})<\/h1>/gi, "title"],
    [/<h2[^>]*>([^<]{2,80})<\/h2>/gi, "heading"],
    [/<h3[^>]*>([^<]{2,80})<\/h3>/gi, "heading"],
    [/<label[^>]*>([^<]{2,60})</gi, "control"],
    [/<button[^>]*>([^<]{2,40})<\/button>/gi, "button"],
    [/<canvas[\s>]/gi, "canvas"],
  ];

  for (const [pattern, kind] of patterns) {
    for (const match of html.matchAll(pattern)) {
      const text = kind === "canvas" ? "drawing surface" : match[1]?.trim();
      if (text) items.push({ kind, text });
    }
  }

  return items.slice(0, 14);
}
