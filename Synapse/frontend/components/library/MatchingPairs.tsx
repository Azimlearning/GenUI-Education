"use client";

// Pattern: matching-pairs (enzyme↔substrate, organ↔function). Retrieval practice.
// Click a left item, then its match on the right. Correct pairings come from `correct`
// (default: the KSSM digestive enzymes — amylase→starch, pepsin→protein, lipase→fat).

import { useState } from "react";
import type { CSSProperties } from "react";

import { PatternCard, type LibraryComponentProps } from "./shared";

export default function MatchingPairs({ props, meta }: LibraryComponentProps) {
  const left = arr(props.left, ["amylase", "pepsin", "lipase"]);
  const right = arr(props.right, ["starch", "protein", "fat"]);
  const correct = (props.correct as Record<string, string>) ?? { amylase: "starch", pepsin: "protein", lipase: "fat" };

  const [pick, setPick] = useState<string | null>(null);
  const [done, setDone] = useState<Record<string, boolean>>({});

  function choose(r: string) {
    if (!pick) return;
    if (correct[pick] === r) setDone((d) => ({ ...d, [pick]: true }));
    setPick(null);
  }
  const allDone = left.every((l) => done[l]);

  return (
    <PatternCard title="Match the pairs" meta={meta}>
      <div style={{ display: "flex", gap: 16 }}>
        <Column title="Enzyme" items={left} render={(l) => (
          <button key={l} disabled={done[l]} onClick={() => setPick(l)}
            style={{ ...cell, opacity: done[l] ? 0.5 : 1, border: pick === l ? "2px solid var(--indigo-2)" : "1px solid var(--line)", background: done[l] ? "var(--teal-soft)" : "var(--white)" }}>
            {l}{done[l] ? " ✓" : ""}
          </button>
        )} />
        <Column title="Substrate" items={right} render={(r) => (
          <button key={r} onClick={() => choose(r)} style={{ ...cell, border: "1px solid var(--line)", background: "var(--white)" }}>{r}</button>
        )} />
      </div>
      {allDone && <p style={{ marginTop: 12, color: "var(--teal)", fontWeight: 700 }}>All matched. Each enzyme is specific to its substrate (lock and key).</p>}
    </PatternCard>
  );
}

function Column({ title, items, render }: { title: string; items: string[]; render: (s: string) => React.ReactNode }) {
  return (
    <div style={{ flex: 1 }}>
      <div style={{ fontSize: 11, color: "var(--slate)", fontWeight: 700, marginBottom: 6 }}>{title}</div>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>{items.map(render)}</div>
    </div>
  );
}

function arr(v: unknown, fallback: string[]): string[] {
  return Array.isArray(v) && v.length ? (v as unknown[]).map(String) : fallback;
}

const cell: CSSProperties = { padding: "10px 12px", borderRadius: 10, fontSize: 14, fontFamily: "inherit", cursor: "pointer", color: "var(--ink)", textAlign: "left" };
