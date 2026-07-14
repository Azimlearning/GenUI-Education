"use client";

/**
 * Refraction and total internal reflection.
 *
 * Snell's law solved live: n1 sin θ1 = n2 sin θ2. TIR is not a mode or a flag —
 * it is what happens when the solve has no answer, because sin θ2 > 1. The
 * student discovers the critical angle by sweeping past it, which is the only
 * way it ever really lands.
 */

import { useMemo, useState } from "react";
import { Control, SciencePanel, slotNum, slotStr, type ScienceProps } from "./shared";

export default function RefractionSandbox({ slots, onInteraction }: ScienceProps) {
  const m1 = slotStr(slots, "medium_1", "air");
  const m2 = slotStr(slots, "medium_2", "water");

  const [n1, setN1] = useState(() => slotNum(slots, "n1", 1.0));
  const [n2, setN2] = useState(() => slotNum(slots, "n2", 1.33));
  const [theta1, setTheta1] = useState(() => slotNum(slots, "incidence_deg", 30));
  const [touched, setTouched] = useState(false);

  const solved = useMemo(() => {
    const rad = (theta1 * Math.PI) / 180;
    const sin2 = (n1 * Math.sin(rad)) / n2;

    // No solution means the refracted ray cannot exist: total internal reflection.
    const tir = Math.abs(sin2) > 1;
    const theta2 = tir ? null : (Math.asin(sin2) * 180) / Math.PI;

    // A critical angle only exists going from denser to less dense.
    const critical = n1 > n2 ? (Math.asin(n2 / n1) * 180) / Math.PI : null;

    return { theta2, tir, critical, bendsToward: n2 > n1 };
  }, [n1, n2, theta1]);

  const onSweep = (v: number) => {
    setTheta1(v);
    if (!touched) setTouched(true);
  };

  const report = () => {
    onInteraction?.("explored the angle of incidence", {
      n1,
      n2,
      incidence_deg: theta1,
      refraction_deg: solved.theta2 === null ? "total internal reflection" : Number(solved.theta2.toFixed(1)),
      critical_angle: solved.critical === null ? "none" : Number(solved.critical.toFixed(1)),
    });
  };

  return (
    <SciencePanel
      title="Refraction and total internal reflection"
      subject="physics"
      badge="n₁ sin θ₁ = n₂ sin θ₂"
    >
      <RayDiagram theta1={theta1} theta2={solved.theta2} tir={solved.tir} m1={m1} m2={m2} />

      <div className="readouts">
        <div className="readout">
          <span className="readout-label">Angle of incidence</span>
          <span className="readout-value">{theta1.toFixed(1)}<em>°</em></span>
        </div>
        <div className="readout">
          <span className="readout-label">Angle of refraction</span>
          <span className="readout-value">
            {solved.theta2 === null ? "—" : solved.theta2.toFixed(1)}
            <em>{solved.theta2 === null ? "TIR" : "°"}</em>
          </span>
        </div>
        <div className="readout">
          <span className="readout-label">Critical angle</span>
          <span className="readout-value">
            {solved.critical === null ? "—" : solved.critical.toFixed(1)}
            <em>{solved.critical === null ? "n/a" : "°"}</em>
          </span>
        </div>
      </div>

      <div className="working">
        <code>
          {n1.toFixed(2)} × sin({theta1.toFixed(1)}°) = {n2.toFixed(2)} × sin(θ₂)
        </code>
        <code>
          sin(θ₂) = {((n1 * Math.sin((theta1 * Math.PI) / 180)) / n2).toFixed(3)}
          {solved.tir ? "  → greater than 1, so no refracted ray can exist" : ""}
        </code>
      </div>

      <div className="sci-controls">
        <Control label="Angle of incidence" value={theta1} min={0} max={89} step={0.5} suffix="°" onChange={onSweep} />
        <Control label={`n₁ (${m1})`} value={n1} min={1} max={2.5} step={0.01} onChange={setN1} />
        <Control label={`n₂ (${m2})`} value={n2} min={1} max={2.5} step={0.01} onChange={setN2} />
      </div>

      <div className={`callout ${solved.tir ? "is-warning" : "is-info"}`}>
        {solved.tir ? (
          <>
            <strong>Total internal reflection.</strong> Past the critical angle of{" "}
            {solved.critical?.toFixed(1)}°, Snell's law asks for an angle whose sine exceeds 1 —
            which no angle has. So no light escapes into the {m2}: all of it reflects back. This is
            the whole basis of fibre optics.
          </>
        ) : solved.bendsToward ? (
          <>
            The ray bends <strong>toward the normal</strong> entering the denser {m2} (n₂ = {n2.toFixed(2)}
            {" "}&gt; n₁ = {n1.toFixed(2)}): light slows down, so the wavefront pivots.{" "}
            {n1 >= n2 ? "" : "There is no critical angle in this direction — you can only get TIR going from dense to less dense."}
          </>
        ) : (
          <>
            The ray bends <strong>away from the normal</strong> entering the less dense {m2}. Keep
            increasing the angle: at {solved.critical?.toFixed(1)}° the refracted ray flattens to
            90° along the boundary, and beyond it there is no refracted ray at all.
          </>
        )}
      </div>

      <button className="btn-secondary" onClick={report} disabled={!touched}>
        Ask about what I'm seeing
      </button>
    </SciencePanel>
  );
}

function RayDiagram({
  theta1,
  theta2,
  tir,
  m1,
  m2,
}: {
  theta1: number;
  theta2: number | null;
  tir: boolean;
  m1: string;
  m2: string;
}) {
  const W = 320;
  const H = 200;
  const cx = W / 2;
  const cy = H / 2;
  const L = 120;

  const rad = (d: number) => (d * Math.PI) / 180;

  // Incident ray arrives from the upper left, measured from the normal.
  const ix = cx - Math.sin(rad(theta1)) * L;
  const iy = cy - Math.cos(rad(theta1)) * L;

  // Reflected ray leaves at the same angle on the other side. Always drawn:
  // partial reflection happens at every boundary, not only past critical.
  const rx = cx + Math.sin(rad(theta1)) * L;
  const ry = cy - Math.cos(rad(theta1)) * L;

  const tx = theta2 === null ? 0 : cx + Math.sin(rad(theta2)) * L;
  const ty = theta2 === null ? 0 : cy + Math.cos(rad(theta2)) * L;

  return (
    <div className="ray">
      <svg viewBox={`0 0 ${W} ${H}`} className="ray-svg" role="img" aria-label="ray diagram">
        <rect x="0" y="0" width={W} height={cy} className="medium-1" />
        <rect x="0" y={cy} width={W} height={cy} className="medium-2" />
        <line x1="0" y1={cy} x2={W} y2={cy} className="boundary" />
        <line x1={cx} y1="10" x2={cx} y2={H - 10} className="normal" />

        <line x1={ix} y1={iy} x2={cx} y2={cy} className="ray-incident" markerEnd="url(#arrow)" />
        <line x1={cx} y1={cy} x2={rx} y2={ry} className={`ray-reflected${tir ? " is-total" : ""}`} />
        {theta2 !== null ? (
          <line x1={cx} y1={cy} x2={tx} y2={ty} className="ray-refracted" markerEnd="url(#arrow)" />
        ) : null}

        <text x="8" y="16" className="ray-label">{m1}</text>
        <text x="8" y={H - 8} className="ray-label">{m2}</text>
        <text x={cx + 4} y="20" className="ray-label is-dim">normal</text>

        <defs>
          <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
            <path d="M 0 0 L 10 5 L 0 10 z" className="arrowhead" />
          </marker>
        </defs>
      </svg>
    </div>
  );
}
