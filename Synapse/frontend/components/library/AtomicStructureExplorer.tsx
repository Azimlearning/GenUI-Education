"use client";

// Pattern: atomic-structure-explorer (atomic structure — Bohr model).
// Shows the nucleus (protons/neutrons) and electron shells. Faithful shell filling for the
// first 20 elements: 2, 8, 8, 2. Electrons default from the proton count if `shells` is absent.

import { PatternCard, type LibraryComponentProps } from "./shared";

// Correct shell capacities used for the KSSM first-20 elements.
function shellsFor(electrons: number): number[] {
  const caps = [2, 8, 8, 2];
  const out: number[] = [];
  let left = electrons;
  for (const cap of caps) {
    if (left <= 0) break;
    const put = Math.min(cap, left);
    out.push(put);
    left -= put;
  }
  return out;
}

export default function AtomicStructureExplorer({ props, meta }: LibraryComponentProps) {
  const protons = clampInt(Number(props.protons ?? 11), 1, 20); // default sodium
  const neutrons = clampInt(Number(props.neutrons ?? 12), 0, 30);
  const shells = Array.isArray(props.shells) && (props.shells as unknown[]).length
    ? (props.shells as unknown[]).map((n) => Number(n))
    : shellsFor(protons);

  return (
    <PatternCard title="Atomic structure (Bohr model)" meta={meta}>
      <div style={{ display: "flex", justifyContent: "center" }}>
        <svg viewBox="0 0 220 220" width={220} height={220}>
          {shells.map((_, i) => {
            const r = 26 + (i + 1) * 22;
            return <circle key={i} cx={110} cy={110} r={r} fill="none" stroke="var(--line)" />;
          })}
          {shells.map((count, i) => {
            const r = 26 + (i + 1) * 22;
            return Array.from({ length: count }).map((__, e) => {
              const angle = (2 * Math.PI * e) / count;
              const x = 110 + r * Math.cos(angle);
              const y = 110 + r * Math.sin(angle);
              return <circle key={`${i}-${e}`} cx={x} cy={y} r={4.5} fill="var(--teal)" />;
            });
          })}
          <circle cx={110} cy={110} r={24} fill="var(--indigo)" />
          <text x={110} y={108} textAnchor="middle" fill="#fff" fontSize="11" fontWeight="700">{protons}p</text>
          <text x={110} y={120} textAnchor="middle" fill="#fff" fontSize="11">{neutrons}n</text>
        </svg>
      </div>
      <div style={{ textAlign: "center", fontSize: 14 }}>
        Proton number <strong>{protons}</strong> · nucleon number <strong>{protons + neutrons}</strong> · configuration <strong>{shells.join(", ")}</strong>
      </div>
    </PatternCard>
  );
}

function clampInt(n: number, lo: number, hi: number): number {
  if (Number.isNaN(n)) return lo;
  return Math.max(lo, Math.min(hi, Math.round(n)));
}
