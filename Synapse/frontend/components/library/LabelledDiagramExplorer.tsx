"use client";

// Pattern: labelled-diagram-explorer (digestive tract, cell, heart…). Labelled exploration.
// Click a part to read its role. Default is the digestive-tract "journey" — the path a food
// particle takes, with the KSSM enzymes named where they act.

import { useState } from "react";
import type { CSSProperties } from "react";

import { PatternCard, type LibraryComponentProps } from "./shared";

type Part = { id: string; label: string; blurb: string };

const DIGESTIVE: Part[] = [
  { id: "mouth", label: "Mouth", blurb: "Teeth break food up; salivary amylase begins digesting starch into maltose." },
  { id: "stomach", label: "Stomach", blurb: "Pepsin (in acid) digests protein into polypeptides; the acid also kills microbes." },
  { id: "small-intestine", label: "Small intestine", blurb: "Amylase, protease and lipase finish digestion; villi absorb the products." },
  { id: "pancreas", label: "Pancreas", blurb: "Secretes amylase, protease and lipase into the small intestine." },
  { id: "large-intestine", label: "Large intestine", blurb: "Absorbs water; the remaining material is egested." },
];

export default function LabelledDiagramExplorer({ props, meta }: LibraryComponentProps) {
  const parts = parseParts(props.parts) ?? DIGESTIVE;
  const [sel, setSel] = useState<Part>(parts[0]);

  return (
    <PatternCard title="Digestive system — follow the food" meta={meta}>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 10 }}>
        {parts.map((p, i) => (
          <span key={p.id} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <button onClick={() => setSel(p)}
              style={{ ...hotspot, border: sel.id === p.id ? "2px solid var(--indigo-2)" : "1px solid var(--line)", background: sel.id === p.id ? "var(--indigo-soft)" : "var(--white)", color: sel.id === p.id ? "var(--indigo)" : "var(--slate)" }}>
              {p.label}
            </button>
            {i < parts.length - 1 && <span style={{ color: "var(--line)" }}>→</span>}
          </span>
        ))}
      </div>
      <div style={{ padding: 12, borderRadius: 10, background: "var(--teal-soft)" }}>
        <div style={{ fontWeight: 800, color: "var(--teal)" }}>{sel.label}</div>
        <p style={{ margin: "4px 0 0", fontSize: 14 }}>{sel.blurb}</p>
      </div>
    </PatternCard>
  );
}

function parseParts(v: unknown): Part[] | null {
  if (!Array.isArray(v) || !v.length) return null;
  const out: Part[] = [];
  for (const item of v) {
    if (item && typeof item === "object") {
      const o = item as Record<string, unknown>;
      if (o.id && o.label) out.push({ id: String(o.id), label: String(o.label), blurb: String(o.blurb ?? "") });
    }
  }
  return out.length ? out : null;
}

const hotspot: CSSProperties = { padding: "8px 12px", borderRadius: 20, fontSize: 12.5, fontFamily: "inherit", fontWeight: 600, cursor: "pointer" };
