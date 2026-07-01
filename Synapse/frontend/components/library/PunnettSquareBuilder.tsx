"use client";

// Pattern: punnett-square-builder (genetics & inheritance).
// Builds the monohybrid cross from two parent genotypes and reveals the 2x2 grid + the
// genotype and phenotype ratios. Faithful: dominant allele (uppercase) masks the recessive;
// Bb x Bb → 3 dominant : 1 recessive.

import { useState } from "react";
import type { CSSProperties } from "react";

import { PatternCard, type LibraryComponentProps } from "./shared";

export default function PunnettSquareBuilder({ props, meta }: LibraryComponentProps) {
  const p1 = normalize(String(props.parent1 ?? "Bb"));
  const p2 = normalize(String(props.parent2 ?? "Bb"));
  const trait = (props.trait as Record<string, string>) ?? { B: "brown eyes", b: "blue eyes" };
  const [shown, setShown] = useState(false);

  const cells = [
    [combine(p1[0], p2[0]), combine(p1[0], p2[1])],
    [combine(p1[1], p2[0]), combine(p1[1], p2[1])],
  ];
  const flat = cells.flat();
  const dominantLetter = p1[0].toUpperCase();
  const dominant = flat.filter((g) => g.includes(dominantLetter)).length;
  const recessive = flat.length - dominant;

  return (
    <PatternCard title="Punnett square" meta={meta}>
      <div style={{ textAlign: "center", fontSize: 14, marginBottom: 10 }}>
        Cross <strong>{p1}</strong> × <strong>{p2}</strong>
      </div>
      <table style={{ margin: "0 auto", borderCollapse: "collapse" }}>
        <tbody>
          <tr><td style={hdr}></td><td style={hdr}>{p2[0]}</td><td style={hdr}>{p2[1]}</td></tr>
          {cells.map((row, i) => (
            <tr key={i}>
              <td style={hdr}>{p1[i]}</td>
              {row.map((g, j) => (
                <td key={j} style={{ ...box, background: shown ? (g.includes(dominantLetter) ? "var(--teal-soft)" : "#fff7ed") : "var(--white)" }}>
                  {shown ? g : "?"}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {!shown ? (
        <button style={runBtn} onClick={() => setShown(true)}>Reveal offspring</button>
      ) : (
        <div style={{ marginTop: 12, padding: 12, borderRadius: 10, background: "var(--indigo-soft)", fontSize: 14 }}>
          <div>Genotype ratio: {ratio(flat)}</div>
          <div>Phenotype ratio: <strong>{dominant} {trait[dominantLetter] ?? "dominant"}</strong> : <strong>{recessive} {trait[dominantLetter.toLowerCase()] ?? "recessive"}</strong></div>
        </div>
      )}
    </PatternCard>
  );
}

function normalize(g: string): string {
  const letters = g.replace(/[^A-Za-z]/g, "").slice(0, 2);
  return letters.length === 2 ? letters : "Bb";
}
function combine(a: string, b: string): string {
  // Uppercase (dominant) first for a canonical genotype label.
  return [a, b].sort((x, y) => (x.toLowerCase() === y.toLowerCase() ? (x < y ? -1 : 1) : 0)).join("");
}
function ratio(flat: string[]): string {
  const counts: Record<string, number> = {};
  for (const g of flat) counts[g] = (counts[g] ?? 0) + 1;
  return Object.entries(counts).map(([g, n]) => `${n} ${g}`).join(" : ");
}

const hdr: CSSProperties = { width: 44, height: 40, textAlign: "center", fontWeight: 800, color: "var(--indigo)", border: "1px solid var(--line)" };
const box: CSSProperties = { width: 56, height: 48, textAlign: "center", fontWeight: 700, fontSize: 16, border: "1px solid var(--line)" };
const runBtn: CSSProperties = { marginTop: 12, background: "var(--indigo)", color: "#fff", border: "none", padding: "10px 18px", borderRadius: 10, fontSize: 14, fontWeight: 700, fontFamily: "inherit", cursor: "pointer" };
