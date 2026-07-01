"use client";

// Pattern: stage-sequencer (cell division stages). Retrieval + contrasting cases.
// The student clicks the stages in order; the component checks against the faithful order
// (prophase → metaphase → anaphase → telophase). `stages` can override the sequence.

import { useState } from "react";
import type { CSSProperties } from "react";

import { PatternCard, type LibraryComponentProps } from "./shared";

export default function StageSequencer({ props, meta }: LibraryComponentProps) {
  const correct = arr(props.stages, ["prophase", "metaphase", "anaphase", "telophase"]);
  const compare = props.compare ? String(props.compare) : "";
  const shuffled = useState(() => [...correct].sort((a, b) => (a > b ? 1 : -1)))[0];

  const [order, setOrder] = useState<string[]>([]);
  const remaining = shuffled.filter((s) => !order.includes(s));
  const finished = order.length === correct.length;
  const isCorrect = finished && order.every((s, i) => s === correct[i]);

  return (
    <PatternCard title="Put the stages in order" meta={meta}>
      <div style={{ minHeight: 40, display: "flex", gap: 8, flexWrap: "wrap", padding: 8, border: "1px dashed var(--line)", borderRadius: 10, marginBottom: 10 }}>
        {order.length === 0 && <span style={{ color: "var(--slate)", fontSize: 13 }}>click the stages in the correct order…</span>}
        {order.map((s, i) => <span key={s} style={{ ...pill, background: "var(--indigo-soft)", color: "var(--indigo)" }}>{i + 1}. {s}</span>)}
      </div>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        {remaining.map((s) => <button key={s} style={{ ...pill, cursor: "pointer", border: "1px solid var(--line)" }} onClick={() => setOrder([...order, s])}>{s}</button>)}
      </div>
      {finished && (
        <div style={{ marginTop: 12, borderRadius: 12, padding: 12, background: isCorrect ? "var(--teal-soft)" : "#fff7ed", border: `1px solid ${isCorrect ? "var(--teal)" : "#fed7aa"}` }}>
          <strong style={{ color: isCorrect ? "var(--teal)" : "var(--amber)" }}>
            {isCorrect ? "Correct order." : `Correct order: ${correct.join(" → ")}`}
          </strong>
          {compare && <p style={{ margin: "6px 0 0", fontSize: 13 }}>Note: mitosis keeps the chromosome number; {compare} halves it across two divisions.</p>}
          <div><button style={retryBtn} onClick={() => setOrder([])}>Reset</button></div>
        </div>
      )}
    </PatternCard>
  );
}

function arr(v: unknown, fallback: string[]): string[] {
  return Array.isArray(v) && v.length ? (v as unknown[]).map(String) : fallback;
}

const pill: CSSProperties = { padding: "8px 12px", borderRadius: 20, fontSize: 13, fontFamily: "inherit", background: "var(--white)", color: "var(--ink)" };
const retryBtn: CSSProperties = { marginTop: 8, background: "var(--white)", border: "1px solid var(--line)", color: "var(--slate)", padding: "6px 12px", borderRadius: 8, fontSize: 12.5, fontFamily: "inherit", cursor: "pointer" };
