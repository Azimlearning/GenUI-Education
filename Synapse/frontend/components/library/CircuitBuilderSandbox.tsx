"use client";

// Pattern: circuit-builder-sandbox (electricity — Ohm's law, series/parallel).
// Adjust EMF and resistors; the component computes current and voltages correctly.
// Faithful: V = IR; series → same current, resistances add; parallel → same voltage,
// 1/Rt = Σ(1/R).

import { useState } from "react";
import type { CSSProperties } from "react";

import { PatternCard, type LibraryComponentProps } from "./shared";

export default function CircuitBuilderSandbox({ props, meta }: LibraryComponentProps) {
  const [emf, setEmf] = useState(clampPos(Number(props.emf ?? 6), 1, 24));
  const [topology, setTopology] = useState<"series" | "parallel">(
    String(props.topology ?? "series") === "parallel" ? "parallel" : "series",
  );
  const resistors = arrNums(props.resistors, [2, 4]); // ohms

  const rTotal = topology === "series"
    ? resistors.reduce((a, b) => a + b, 0)
    : 1 / resistors.reduce((a, b) => a + 1 / b, 0);
  const current = emf / rTotal; // A (total)

  return (
    <PatternCard title="Circuit — Ohm's law" meta={meta}>
      <div style={{ display: "flex", gap: 16, alignItems: "center", marginBottom: 10, flexWrap: "wrap" }}>
        <label style={{ fontSize: 13, color: "var(--slate)" }}>
          EMF: <strong style={{ color: "var(--ink)" }}>{emf} V</strong>
          <input type="range" min={1} max={24} value={emf} onChange={(e) => setEmf(Number(e.target.value))} style={{ display: "block", width: 160 }} />
        </label>
        <div style={{ display: "flex", gap: 6 }}>
          {(["series", "parallel"] as const).map((t) => (
            <button key={t} onClick={() => setTopology(t)}
              style={{ ...tab, background: topology === t ? "var(--indigo-soft)" : "var(--white)", border: topology === t ? "2px solid var(--indigo-2)" : "1px solid var(--line)", color: topology === t ? "var(--indigo)" : "var(--slate)" }}>
              {t}
            </button>
          ))}
        </div>
      </div>

      <div style={{ display: "flex", gap: 10, justifyContent: "center", marginBottom: 10 }}>
        {resistors.map((r, i) => (
          <div key={i} style={{ padding: "10px 14px", border: "1px solid var(--line)", borderRadius: 8, background: "#f8fafc", textAlign: "center" }}>
            <div style={{ fontWeight: 800, color: "var(--indigo)" }}>R{i + 1}</div>
            <div style={{ fontSize: 13 }}>{r} Ω</div>
            <div style={{ fontSize: 11, color: "var(--slate)" }}>
              {topology === "series" ? `${(current * r).toFixed(2)} V` : `${(emf / r).toFixed(2)} A`}
            </div>
          </div>
        ))}
      </div>

      <div style={{ padding: 12, borderRadius: 10, background: "var(--teal-soft)", fontSize: 14 }}>
        Total resistance <strong>{rTotal.toFixed(2)} Ω</strong> · total current I = V/R ={" "}
        <strong>{current.toFixed(2)} A</strong>.{" "}
        {topology === "series"
          ? "In series the current is the same everywhere and the voltages add up."
          : "In parallel each branch has the full voltage and the branch currents add up."}
      </div>
    </PatternCard>
  );
}

function arrNums(v: unknown, fallback: number[]): number[] {
  if (Array.isArray(v) && v.length) {
    const nums = (v as unknown[]).map(Number).filter((n) => n > 0);
    if (nums.length) return nums;
  }
  return fallback;
}
function clampPos(n: number, lo: number, hi: number) { return Number.isNaN(n) ? lo : Math.max(lo, Math.min(hi, n)); }

const tab: CSSProperties = { padding: "6px 14px", borderRadius: 8, fontSize: 13, fontFamily: "inherit", fontWeight: 600, cursor: "pointer", textTransform: "capitalize" };
