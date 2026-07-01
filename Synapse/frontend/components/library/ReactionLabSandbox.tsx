"use client";

// Pattern: reaction-lab-sandbox (chemistry reactions with apparatus + reagents).
// Predict-observe-explain: pick two reagents, predict the observation, then mix. Outcomes come
// from a small encoded rules table (not free-generated), so the chemistry stays correct
// (constraint #6): acid + alkali → salt + water; acid + carbonate → salt + water + CO2 (fizzing);
// acid + reactive metal → salt + hydrogen (fizzing).

import { useState } from "react";
import type { CSSProperties } from "react";

import { PatternCard, type LibraryComponentProps } from "./shared";

type Reagent = "acid" | "alkali" | "carbonate" | "metal";
type Rule = { a: Reagent; b: Reagent; product: string; observation: string };

const RULES: Rule[] = [
  { a: "acid", b: "alkali", product: "salt + water", observation: "Neutralisation. No gas; temperature rises slightly." },
  { a: "acid", b: "carbonate", product: "salt + water + CO₂", observation: "Fizzing — carbon dioxide turns limewater milky." },
  { a: "acid", b: "metal", product: "salt + hydrogen", observation: "Fizzing — hydrogen gives a squeaky pop with a lit splint." },
];

function lookup(a: Reagent, b: Reagent): Rule | null {
  return RULES.find((r) => (r.a === a && r.b === b) || (r.a === b && r.b === a)) ?? null;
}

const CHOICES: Reagent[] = ["acid", "alkali", "carbonate", "metal"];

export default function ReactionLabSandbox({ props, meta }: LibraryComponentProps) {
  void props;
  const [a, setA] = useState<Reagent | null>(null);
  const [b, setB] = useState<Reagent | null>(null);
  const [mixed, setMixed] = useState(false);
  const rule = a && b ? lookup(a, b) : null;

  return (
    <PatternCard title="Reaction lab" meta={meta}>
      <div style={{ display: "flex", gap: 16, marginBottom: 10 }}>
        <Picker title="Reagent A" value={a} onPick={(r) => { setA(r); setMixed(false); }} />
        <Picker title="Reagent B" value={b} onPick={(r) => { setB(r); setMixed(false); }} />
      </div>
      <button style={{ ...runBtn, opacity: a && b ? 1 : 0.5, cursor: a && b ? "pointer" : "not-allowed" }} disabled={!a || !b} onClick={() => setMixed(true)}>
        Mix them →
      </button>
      {mixed && (
        <div style={{ marginTop: 12, padding: 12, borderRadius: 10, background: rule ? "var(--teal-soft)" : "#fff7ed", border: `1px solid ${rule ? "var(--teal)" : "#fed7aa"}`, fontSize: 14, animation: "fade .3s" }}>
          {rule ? (
            <>
              <div style={{ fontWeight: 800, color: "var(--teal)" }}>{a} + {b} → {rule.product}</div>
              <p style={{ margin: "4px 0 0" }}>{rule.observation}</p>
            </>
          ) : (
            <span style={{ color: "var(--amber)" }}>These two do not react appreciably in the KSSM syllabus. Try acid with an alkali, carbonate, or reactive metal.</span>
          )}
        </div>
      )}
    </PatternCard>
  );
}

function Picker({ title, value, onPick }: { title: string; value: Reagent | null; onPick: (r: Reagent) => void }) {
  return (
    <div style={{ flex: 1 }}>
      <div style={{ fontSize: 11, color: "var(--slate)", fontWeight: 700, marginBottom: 6 }}>{title}</div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
        {CHOICES.map((c) => (
          <button key={c} onClick={() => onPick(c)}
            style={{ ...chip, border: value === c ? "2px solid var(--indigo-2)" : "1px solid var(--line)", background: value === c ? "var(--indigo-soft)" : "var(--white)", color: value === c ? "var(--indigo)" : "var(--slate)" }}>
            {c}
          </button>
        ))}
      </div>
    </div>
  );
}

const chip: CSSProperties = { padding: "7px 12px", borderRadius: 20, fontSize: 12.5, fontFamily: "inherit", fontWeight: 600, cursor: "pointer" };
const runBtn: CSSProperties = { background: "var(--indigo)", color: "#fff", border: "none", padding: "10px 18px", borderRadius: 10, fontSize: 14, fontWeight: 700, fontFamily: "inherit" };
