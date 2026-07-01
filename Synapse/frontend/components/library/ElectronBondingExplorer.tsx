"use client";

// Pattern: electron-bonding-explorer (Chemistry flagship — bonding & electrons).
// Contrasting cases: the student decides ionic vs covalent for a pair of atoms, then watches
// electrons TRANSFER (ionic) or be SHARED (covalent). The rule is encoded here, not guessed
// (constraint #6): metal + non-metal → ionic transfer; non-metal + non-metal → covalent share.
// Targets the bonding-sharing-vs-transfer misconception.

import { useEffect, useState } from "react";
import type { CSSProperties } from "react";

import { PatternCard, type LibraryComponentProps } from "./shared";

// KSSM-relevant classification (first 20 + common metals). Enough to keep the science honest.
const METALS = new Set(["Li", "Na", "K", "Mg", "Ca", "Al", "Be", "Zn", "Fe", "Cu", "Ba"]);
const NON_METALS = new Set(["H", "C", "N", "O", "F", "P", "S", "Cl", "Br", "I"]);

type Bond = "ionic" | "covalent" | "metallic";
type Pair = { left: string; right: string; formula?: string };

function classify(a: string, b: string): Bond {
  const am = METALS.has(a);
  const bm = METALS.has(b);
  if (am && bm) return "metallic";
  if (am !== bm) return "ionic"; // exactly one metal → transfer
  return "covalent"; // both non-metals → share
}

const DEFAULT_PAIRS: Pair[] = [
  { left: "Na", right: "Cl", formula: "NaCl" },
  { left: "H", right: "O", formula: "H₂O" },
];

export default function ElectronBondingExplorer({ props, meta, onInteraction }: LibraryComponentProps) {
  const pairs = parsePairs(props) ?? DEFAULT_PAIRS;
  const [idx, setIdx] = useState(0);
  const [guess, setGuess] = useState<Bond | null>(null);
  const [revealed, setRevealed] = useState(false);

  const pair = pairs[Math.min(idx, pairs.length - 1)];
  const answer = classify(pair.left, pair.right);
  const wasRight = guess === answer;

  // Report the outcome once, when the electrons are revealed (P3).
  useEffect(() => {
    if (revealed) onInteraction?.({ correct: wasRight });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [revealed]);

  return (
    <PatternCard title="Bonding & electrons" meta={meta}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 4, marginBottom: 6 }}>
        <Atom symbol={pair.left} kind={METALS.has(pair.left) ? "metal" : "non-metal"} />
        <BondView bond={answer} revealed={revealed} />
        <Atom symbol={pair.right} kind={METALS.has(pair.right) ? "metal" : "non-metal"} />
      </div>
      {pair.formula && (
        <div style={{ textAlign: "center", fontSize: 13, color: "var(--slate)", marginBottom: 10 }}>
          example: <strong style={{ color: "var(--ink)" }}>{pair.formula}</strong>
        </div>
      )}

      <p style={label}><strong>Which bond forms?</strong> Look at whether each atom is a metal or a non-metal.</p>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <GuessBtn active={guess === "ionic"} disabled={revealed} onClick={() => setGuess("ionic")} label="Ionic — electrons transfer" />
        <GuessBtn active={guess === "covalent"} disabled={revealed} onClick={() => setGuess("covalent")} label="Covalent — electrons shared" />
      </div>

      {!revealed ? (
        <button style={{ ...runBtn, opacity: guess ? 1 : 0.5, cursor: guess ? "pointer" : "not-allowed" }} disabled={!guess} onClick={() => setRevealed(true)}>
          Reveal the electrons →
        </button>
      ) : (
        <div style={{ marginTop: 12, borderRadius: 12, padding: 14, animation: "fade .3s", background: wasRight ? "var(--teal-soft)" : "#fff7ed", border: `1px solid ${wasRight ? "var(--teal)" : "#fed7aa"}` }}>
          <div style={{ fontWeight: 800, color: wasRight ? "var(--teal)" : "var(--amber)", marginBottom: 4 }}>
            {wasRight ? "Correct." : "Not quite."} It is a <strong>{answer}</strong> bond.
          </div>
          <p style={{ margin: "0 0 10px", fontSize: 14 }}>{explain(pair, answer)}</p>
          <div style={{ display: "flex", gap: 8 }}>
            {pairs.length > 1 && (
              <button style={retryBtn} onClick={() => { setIdx((idx + 1) % pairs.length); setGuess(null); setRevealed(false); }}>
                Contrast the next example →
              </button>
            )}
            <button style={retryBtn} onClick={() => { setGuess(null); setRevealed(false); }}>Retry this one</button>
          </div>
        </div>
      )}
    </PatternCard>
  );
}

function Atom({ symbol, kind }: { symbol: string; kind: "metal" | "non-metal" }) {
  return (
    <div style={{ textAlign: "center" }}>
      <div style={{ width: 62, height: 62, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800, fontSize: 20, color: "#fff", background: kind === "metal" ? "#f59e0b" : "#0d9488", boxShadow: "var(--shadow)" }}>
        {symbol}
      </div>
      <div style={{ fontSize: 10.5, color: "var(--slate)", marginTop: 4 }}>{kind}</div>
    </div>
  );
}

function BondView({ bond, revealed }: { bond: Bond; revealed: boolean }) {
  if (!revealed) return <div style={{ width: 60, textAlign: "center", color: "var(--slate)", fontSize: 22 }}>?</div>;
  if (bond === "ionic") {
    return (
      <div style={{ width: 60, textAlign: "center" }} title="electron transfers to the non-metal">
        <span style={{ fontSize: 18, color: "var(--indigo)", animation: "fade .5s" }}>e⁻ →</span>
        <div style={{ fontSize: 10, color: "var(--slate)" }}>transfer</div>
      </div>
    );
  }
  if (bond === "metallic") {
    return <div style={{ width: 60, textAlign: "center", color: "var(--slate)", fontSize: 12 }}>sea of e⁻</div>;
  }
  return (
    <div style={{ width: 60, textAlign: "center" }} title="electrons shared between non-metals">
      <span style={{ fontSize: 18, color: "var(--teal)", animation: "fade .5s" }}>· ·</span>
      <div style={{ fontSize: 10, color: "var(--slate)" }}>shared</div>
    </div>
  );
}

function explain(pair: Pair, bond: Bond): string {
  if (bond === "ionic")
    return `${pair.left} is a metal and ${pair.right} is a non-metal. The metal gives up electron(s) to the non-metal, forming oppositely charged ions held by electrostatic attraction. That is electron TRANSFER, not sharing.`;
  if (bond === "metallic")
    return `Both ${pair.left} and ${pair.right} are metals, so their outer electrons form a shared "sea" around positive ions (metallic bonding).`;
  return `${pair.left} and ${pair.right} are both non-metals. Neither gives up electrons, so they SHARE pairs of electrons to fill their outer shells. That is a covalent bond.`;
}

function parsePairs(props: Record<string, unknown>): Pair[] | null {
  const raw = props.pairs ?? props.examples;
  if (!Array.isArray(raw)) return null;
  const out: Pair[] = [];
  for (const item of raw) {
    if (item && typeof item === "object") {
      const o = item as Record<string, unknown>;
      const left = String(o.left ?? o.a ?? "");
      const right = String(o.right ?? o.b ?? "");
      if (left && right) out.push({ left, right, formula: o.formula ? String(o.formula) : undefined });
    }
  }
  return out.length ? out : null;
}

function GuessBtn({ active, disabled, onClick, label }: { active: boolean; disabled: boolean; onClick: () => void; label: string }) {
  return (
    <button onClick={onClick} disabled={disabled} style={{ ...guessBtn, border: active ? "2px solid var(--indigo-2)" : "1px solid var(--line)", background: active ? "var(--indigo-soft)" : "var(--white)", color: active ? "var(--indigo)" : "var(--slate)", cursor: disabled ? "default" : "pointer", opacity: disabled && !active ? 0.55 : 1 }}>
      {label}
    </button>
  );
}

const label: CSSProperties = { fontSize: 14, color: "var(--ink)", margin: "0 0 8px" };
const guessBtn: CSSProperties = { fontSize: 12.5, padding: "8px 12px", borderRadius: 10, fontFamily: "inherit", fontWeight: 600, flex: "1 1 40%", minWidth: 170 };
const runBtn: CSSProperties = { marginTop: 12, background: "var(--indigo)", color: "#fff", border: "none", padding: "10px 18px", borderRadius: 10, fontSize: 14, fontWeight: 700, fontFamily: "inherit" };
const retryBtn: CSSProperties = { background: "var(--white)", border: "1px solid var(--line)", color: "var(--slate)", padding: "6px 12px", borderRadius: 8, fontSize: 12.5, fontFamily: "inherit", cursor: "pointer" };
