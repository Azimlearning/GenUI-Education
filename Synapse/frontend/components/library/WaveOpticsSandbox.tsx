"use client";

// Pattern: wave-optics-sandbox (waves & optics — refraction).
// Refraction ray sandbox: drag the incidence angle; the refracted ray bends by Snell's law
// (n1 sinθ1 = n2 sinθ2). Faithful: entering a denser medium (n2 > n1) bends the ray TOWARD the
// normal; total internal reflection when the critical angle is exceeded going into a less dense
// medium.

import { useState } from "react";

import { PatternCard, type LibraryComponentProps } from "./shared";

export default function WaveOpticsSandbox({ props, meta }: LibraryComponentProps) {
  const n1 = clampN(Number(props.n1 ?? 1.0)); // e.g. air
  const n2 = clampN(Number(props.n2 ?? 1.5)); // e.g. glass
  const [incidence, setIncidence] = useState(40); // degrees from normal

  const sinR = (n1 / n2) * Math.sin(deg(incidence));
  const tir = Math.abs(sinR) > 1; // total internal reflection
  const refraction = tir ? incidence : rad(Math.asin(sinR));

  // geometry (normal is vertical; interface horizontal at y=100)
  const cx = 150, iy = 100, len = 90;
  const inX = cx - len * Math.sin(deg(incidence));
  const inY = iy - len * Math.cos(deg(incidence));
  const outAngle = tir ? incidence : refraction;
  const outX = cx + (tir ? -1 : 1) * len * Math.sin(deg(outAngle));
  const outY = iy + (tir ? -1 : 1) * len * Math.cos(deg(outAngle));

  return (
    <PatternCard title="Refraction (Snell's law)" meta={meta}>
      <div style={{ display: "flex", justifyContent: "center" }}>
        <svg viewBox="0 0 300 200" width="100%" height={180}>
          <rect x={0} y={100} width={300} height={100} fill="#e6f0ff" />
          <line x1={0} y1={100} x2={300} y2={100} stroke="var(--slate)" />
          <line x1={cx} y1={20} x2={cx} y2={180} stroke="var(--line)" strokeDasharray="4 4" />
          <line x1={inX} y1={inY} x2={cx} y2={iy} stroke="var(--indigo)" strokeWidth="2.5" />
          <line x1={cx} y1={iy} x2={outX} y2={outY} stroke={tir ? "var(--rose)" : "var(--teal)"} strokeWidth="2.5" />
          <text x={8} y={94} fontSize="10" fill="var(--slate)">n₁ = {n1}</text>
          <text x={8} y={116} fontSize="10" fill="var(--slate)">n₂ = {n2}</text>
        </svg>
      </div>
      <label style={{ fontSize: 13, color: "var(--slate)" }}>
        Angle of incidence: <strong style={{ color: "var(--ink)" }}>{incidence}°</strong>
        <input type="range" min={0} max={89} value={incidence} onChange={(e) => setIncidence(Number(e.target.value))} style={{ display: "block", width: "100%" }} />
      </label>
      <p style={{ fontSize: 14, marginTop: 8 }}>
        {tir
          ? "Total internal reflection — beyond the critical angle the ray reflects back instead of refracting."
          : n2 > n1
            ? `Entering the denser medium, the ray bends toward the normal: refraction angle ≈ ${refraction.toFixed(1)}°.`
            : `Entering the less dense medium, the ray bends away from the normal: refraction angle ≈ ${refraction.toFixed(1)}°.`}
      </p>
    </PatternCard>
  );
}

function deg(d: number): number { return (d * Math.PI) / 180; }
function rad(r: number): number { return (r * 180) / Math.PI; }
function clampN(n: number): number { return Number.isNaN(n) || n < 1 ? 1 : Math.min(n, 3); }
