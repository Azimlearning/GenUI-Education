"use client";

// Pattern: force-motion-sim (Physics flagship — forces & motion).
// Faithful predict-observe-explain: the trolley obeys ΣF = ma with kinetic friction opposing
// motion. The student predicts the outcome, then watches the trolley + a live velocity-time
// graph derived FROM the simulation (ticker-tape analogue) — not faked. Targets the
// newton-force-needed-to-keep-moving misconception.

import { useEffect, useRef, useState } from "react";
import type { CSSProperties } from "react";

import { PatternCard, type LibraryComponentProps } from "./shared";

const G = 9.8; // m/s^2

type Guess = "accelerate" | "constant" | "still";
type Phase = "predict" | "running" | "explain";

export default function ForceMotionSim({ props, meta }: LibraryComponentProps) {
  const mass = clampPos(Number(props.mass ?? 2), 0.1, 50); // kg
  const applied = clampPos(Number(props.applied_force ?? 12), 0, 500); // N
  const friction = clamp01(Number(props.friction ?? 0.2)); // coefficient
  const predictPrompt = String(props.predict_prompt ?? "Release the trolley. What happens?");
  const showGraph = String(props.show_graph ?? "v-t") !== "none";

  // Faithful physics: kinetic friction opposes motion once moving.
  const frictionForce = friction * mass * G;
  const netForce = applied - frictionForce;
  const accel = netForce / mass; // m/s^2 (can be negative if friction dominates)
  const outcome: Guess = applied <= frictionForce ? "still" : accel > 0.05 ? "accelerate" : "constant";

  const [guess, setGuess] = useState<Guess | null>(null);
  const [phase, setPhase] = useState<Phase>("predict");
  const [t, setT] = useState(0); // sim seconds elapsed
  const raf = useRef<number | null>(null);
  const start = useRef<number | null>(null);

  useEffect(() => {
    if (phase !== "running") return;
    const tick = (ts: number) => {
      if (start.current === null) start.current = ts;
      const elapsed = (ts - start.current) / 1000;
      setT(Math.min(elapsed, 3));
      if (elapsed >= 3) {
        setPhase("explain");
        return;
      }
      raf.current = requestAnimationFrame(tick);
    };
    raf.current = requestAnimationFrame(tick);
    return () => {
      if (raf.current) cancelAnimationFrame(raf.current);
      start.current = null;
    };
  }, [phase]);

  // Kinematics from the net force. Never let a still trolley drift.
  const a = outcome === "still" ? 0 : accel;
  const velocity = Math.max(0, a * t); // m/s
  const distance = Math.max(0, 0.5 * a * t * t); // m
  const trolleyX = Math.min(distance * 12, 240); // px, scaled for the track

  const wasRight = guess === outcome;

  return (
    <PatternCard title="Forces & motion (ticker-tape trolley)" meta={meta}>
      {/* readouts */}
      <div style={{ display: "flex", gap: 14, flexWrap: "wrap", fontSize: 12.5, color: "var(--slate)", marginBottom: 10 }}>
        <Chip label="mass" value={`${mass} kg`} />
        <Chip label="applied force" value={`${applied} N`} />
        <Chip label="friction µ" value={`${friction}`} />
        <Chip label="net force" value={`${netForce.toFixed(1)} N`} accent />
        <Chip label="acceleration" value={`${a.toFixed(2)} m/s²`} accent />
      </div>

      {/* track + trolley */}
      <div style={track}>
        <div style={{ ...trolley, transform: `translateX(${trolleyX}px)` }} title="trolley">
          <span style={{ fontSize: 18 }}>🛒</span>
        </div>
        {applied > 0 && <span style={arrow}>→ {applied} N</span>}
      </div>

      {/* v-t graph derived from the sim */}
      {showGraph && <VtGraph a={a} t={t} running={phase !== "predict"} />}

      {/* predict */}
      <div style={{ marginTop: 12 }}>
        <p style={label}><strong>Predict.</strong> {predictPrompt}</p>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <GuessBtn active={guess === "accelerate"} disabled={phase !== "predict"} onClick={() => setGuess("accelerate")} label="Speeds up (accelerates)" />
          <GuessBtn active={guess === "constant"} disabled={phase !== "predict"} onClick={() => setGuess("constant")} label="Moves at constant speed" />
          <GuessBtn active={guess === "still"} disabled={phase !== "predict"} onClick={() => setGuess("still")} label="Stays still / can't overcome friction" />
        </div>
      </div>

      {phase === "predict" && (
        <button style={{ ...runBtn, opacity: guess ? 1 : 0.5, cursor: guess ? "pointer" : "not-allowed" }} disabled={!guess} onClick={() => { setT(0); setPhase("running"); }}>
          Release the trolley →
        </button>
      )}
      {phase === "running" && <p style={{ ...label, color: "var(--teal)" }}>v = {velocity.toFixed(2)} m/s …</p>}

      {phase === "explain" && (
        <Explain wasRight={wasRight} outcome={outcome} applied={applied} frictionForce={frictionForce} netForce={netForce} a={a}
          onRetry={() => { setGuess(null); setT(0); setPhase("predict"); }} />
      )}
    </PatternCard>
  );
}

function VtGraph({ a, t, running }: { a: number; t: number; running: boolean }) {
  // Plot v = a·t over 0..3s. Slope = acceleration; a flat line = constant velocity.
  const W = 300, H = 90, T = 3;
  const vmax = Math.max(0.5, Math.abs(a) * T);
  const points: string[] = [];
  const upto = running ? t : T;
  for (let s = 0; s <= upto + 0.001; s += 0.15) {
    const v = Math.max(0, a * s);
    const x = (s / T) * W;
    const y = H - (v / vmax) * (H - 8);
    points.push(`${x.toFixed(1)},${y.toFixed(1)}`);
  }
  return (
    <div style={{ marginTop: 10 }}>
      <div style={{ fontSize: 11, color: "var(--slate)", marginBottom: 4 }}>velocity–time (from the sim)</div>
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" height={H} style={{ border: "1px solid var(--line)", borderRadius: 8, background: "#f8fafc" }}>
        <line x1="0" y1={H - 1} x2={W} y2={H - 1} stroke="var(--line)" />
        <polyline fill="none" stroke="var(--teal)" strokeWidth="2" points={points.join(" ")} />
      </svg>
    </div>
  );
}

function Explain({ wasRight, outcome, applied, frictionForce, netForce, a, onRetry }: {
  wasRight: boolean; outcome: Guess; applied: number; frictionForce: number; netForce: number; a: number; onRetry: () => void;
}) {
  const body =
    outcome === "still"
      ? `The applied force (${applied} N) does not exceed friction (${frictionForce.toFixed(1)} N), so the net force is zero or backward and the trolley stays put.`
      : `Net force = applied − friction = ${applied} − ${frictionForce.toFixed(1)} = ${netForce.toFixed(1)} N. ` +
        `By Newton's second law a = F/m = ${a.toFixed(2)} m/s², so the trolley keeps accelerating while the force acts. ` +
        "A moving object does NOT need a continuous force to keep moving — friction is what slows everyday objects, not the absence of a push (Newton's first law).";
  return (
    <div style={{ marginTop: 12, borderRadius: 12, padding: 14, animation: "fade .3s", background: wasRight ? "var(--teal-soft)" : "#fff7ed", border: `1px solid ${wasRight ? "var(--teal)" : "#fed7aa"}` }}>
      <div style={{ fontWeight: 800, color: wasRight ? "var(--teal)" : "var(--amber)", marginBottom: 4 }}>
        {wasRight ? "Correct." : "Not quite — look at the net force."}
      </div>
      <p style={{ margin: "0 0 10px", fontSize: 14 }}>{body}</p>
      <button style={retryBtn} onClick={onRetry}>Try another prediction</button>
    </div>
  );
}

function Chip({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <span>
      <span style={{ color: "var(--slate)" }}>{label}: </span>
      <strong style={{ color: accent ? "var(--indigo)" : "var(--ink)" }}>{value}</strong>
    </span>
  );
}

function GuessBtn({ active, disabled, onClick, label }: { active: boolean; disabled: boolean; onClick: () => void; label: string }) {
  return (
    <button onClick={onClick} disabled={disabled} style={{ ...guessBtn, border: active ? "2px solid var(--indigo-2)" : "1px solid var(--line)", background: active ? "var(--indigo-soft)" : "var(--white)", color: active ? "var(--indigo)" : "var(--slate)", cursor: disabled ? "default" : "pointer", opacity: disabled && !active ? 0.55 : 1 }}>
      {label}
    </button>
  );
}

function clamp01(n: number) { return Number.isNaN(n) ? 0 : Math.max(0, Math.min(1, n)); }
function clampPos(n: number, lo: number, hi: number) { return Number.isNaN(n) ? lo : Math.max(lo, Math.min(hi, n)); }

const label: CSSProperties = { fontSize: 14, color: "var(--ink)", margin: "0 0 8px" };
const track: CSSProperties = { position: "relative", height: 54, borderRadius: 10, background: "repeating-linear-gradient(90deg,#eef2ff,#eef2ff 18px,#e0e7ff 18px,#e0e7ff 20px)", border: "1px solid var(--line)", overflow: "hidden" };
const trolley: CSSProperties = { position: "absolute", left: 8, top: 10, transition: "transform 0.06s linear" };
const arrow: CSSProperties = { position: "absolute", right: 10, top: 8, fontSize: 12, color: "var(--indigo)", fontWeight: 700 };
const guessBtn: CSSProperties = { fontSize: 12.5, padding: "8px 12px", borderRadius: 10, fontFamily: "inherit", fontWeight: 600, flex: "1 1 30%", minWidth: 150 };
const runBtn: CSSProperties = { marginTop: 12, background: "var(--indigo)", color: "#fff", border: "none", padding: "10px 18px", borderRadius: 10, fontSize: 14, fontWeight: 700, fontFamily: "inherit" };
const retryBtn: CSSProperties = { background: "var(--white)", border: "1px solid var(--line)", color: "var(--slate)", padding: "6px 12px", borderRadius: 8, fontSize: 12.5, fontFamily: "inherit", cursor: "pointer" };
