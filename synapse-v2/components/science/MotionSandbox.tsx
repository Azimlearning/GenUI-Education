"use client";

/**
 * Forces and motion sandbox — the flagship.
 *
 * Real integration, not an animation with a decided ending. Every frame solves
 * ΣF = ma from the current slot values and steps the state forward. The v-t
 * graph is plotted from the same state the trolley is drawn from, so the graph
 * cannot disagree with the motion.
 *
 * v1 modelled friction as kinetic-only, so a box under a force too small to
 * shift it was a special case rather than a physical result. Here static and
 * kinetic friction are distinct: below µs·N the box genuinely does not move,
 * which is the thing SPM students most need to see.
 */

import { useEffect, useMemo, useRef, useState } from "react";
import {
  Control,
  Predict,
  SciencePanel,
  Verdict,
  slotBool,
  slotNum,
  slotStr,
  type ScienceProps,
} from "./shared";

const G = 9.81;
const DT = 1 / 60;
const TRACK_M = 10;

type Phase = "predict" | "running" | "done";
type Outcome = "still" | "accelerating" | "constant";

interface Sample {
  t: number;
  v: number;
}

export default function MotionSandbox({ slots, onInteraction }: ScienceProps) {
  const showGraph = slotBool(slots, "show_graph", true);
  const predictPrompt = slotStr(
    slots,
    "predict_prompt",
    "What happens to the trolley when the force is applied?",
  );

  const [mass, setMass] = useState(() => slotNum(slots, "mass_kg", 2));
  const [force, setForce] = useState(() => slotNum(slots, "applied_force_n", 10));
  const [mu, setMu] = useState(() => slotNum(slots, "friction_coefficient", 0.1));
  const [incline, setIncline] = useState(() => slotNum(slots, "incline_deg", 0));

  const [phase, setPhase] = useState<Phase>("predict");
  const [guess, setGuess] = useState<string | null>(null);
  const [state, setState] = useState({ x: 0, v: 0, t: 0 });
  const [trace, setTrace] = useState<Sample[]>([]);

  /**
   * The free-body analysis, done once per parameter change.
   *
   * On an incline: the normal force carries only the perpendicular component of
   * weight, so friction weakens as the slope steepens while gravity's pull along
   * the slope grows. Both effects fall out of the geometry.
   */
  const physics = useMemo(() => {
    const theta = (incline * Math.PI) / 180;
    const weightAlong = mass * G * Math.sin(theta);
    const normal = mass * G * Math.cos(theta);
    const netDriving = force - weightAlong;

    // Static friction is a response, not a constant: it matches whatever is
    // applied, up to its limit. µs ≈ 1.2 µk is a standard teaching assumption.
    const staticLimit = mu * 1.2 * normal;
    const kinetic = mu * normal;
    const breaksFree = Math.abs(netDriving) > staticLimit;

    return { theta, weightAlong, normal, netDriving, staticLimit, kinetic, breaksFree };
  }, [mass, force, mu, incline]);

  /** What the sim will show. Computed from the physics, never chosen. */
  const outcome: Outcome = useMemo(() => {
    if (!physics.breaksFree) return "still";
    const accel = (Math.abs(physics.netDriving) - physics.kinetic) / mass;
    return accel < 0.05 ? "constant" : "accelerating";
  }, [physics, mass]);

  const raf = useRef<number | null>(null);
  const sim = useRef({ x: 0, v: 0, t: 0 });

  useEffect(() => {
    if (phase !== "running") return;
    sim.current = { x: 0, v: 0, t: 0 };
    setTrace([]);
    let acc = 0;
    let last: number | null = null;

    const step = (ts: number) => {
      if (last === null) last = ts;
      acc += Math.min(0.1, (ts - last) / 1000);
      last = ts;

      // Fixed-step integration so the physics is frame-rate independent.
      while (acc >= DT) {
        const s = sim.current;
        const moving = Math.abs(s.v) > 1e-4;
        let net: number;

        if (!moving && !physics.breaksFree) {
          net = 0; // Static friction holds it. Genuinely stationary.
        } else {
          // Kinetic friction opposes motion, or opposes the driving force at
          // the instant of breaking free.
          const dir = moving ? Math.sign(s.v) : Math.sign(physics.netDriving);
          net = physics.netDriving - physics.kinetic * dir;
          // Friction cannot reverse a body, only stop it.
          if (moving && Math.sign(net) !== Math.sign(s.v) && Math.abs(s.v) < 0.05) {
            sim.current = { ...s, v: 0 };
            net = 0;
          }
        }

        const a = net / mass;
        s.v += a * DT;
        s.x += s.v * DT;
        s.t += DT;

        if (s.x < 0) {
          s.x = 0;
          s.v = 0;
        }
        if (s.x > TRACK_M) {
          s.x = TRACK_M;
          s.v = 0;
        }
        acc -= DT;
      }

      const s = sim.current;
      setState({ ...s });
      setTrace((prev) =>
        prev.length && s.t - prev[prev.length - 1].t < 0.05
          ? prev
          : [...prev, { t: s.t, v: s.v }].slice(-240),
      );

      if (s.t >= 4 || s.x >= TRACK_M) setPhase("done");
      else raf.current = requestAnimationFrame(step);
    };

    raf.current = requestAnimationFrame(step);
    return () => {
      if (raf.current !== null) cancelAnimationFrame(raf.current);
    };
  }, [phase, physics, mass]);

  const run = () => {
    if (!guess) return;
    setPhase("running");
    onInteraction?.("ran the motion simulation", {
      predicted: guess,
      actual: outcome,
      correct: guess === outcome,
      mass_kg: mass,
      applied_force_n: force,
      friction_coefficient: mu,
      incline_deg: incline,
    });
  };

  const reset = () => {
    setPhase("predict");
    setGuess(null);
    setState({ x: 0, v: 0, t: 0 });
    setTrace([]);
  };

  const accel = physics.breaksFree
    ? (Math.abs(physics.netDriving) - physics.kinetic) / mass
    : 0;

  return (
    <SciencePanel title="Forces and motion sandbox" subject="physics" badge="ΣF = ma">
      <Track x={state.x} incline={incline} />

      <div className="readouts">
        <Readout label="Net force" value={physics.breaksFree ? (physics.netDriving - physics.kinetic * Math.sign(physics.netDriving)).toFixed(2) : "0.00"} unit="N" />
        <Readout label="Acceleration" value={accel.toFixed(2)} unit="m/s²" />
        <Readout label="Velocity" value={state.v.toFixed(2)} unit="m/s" />
        <Readout label="Distance" value={state.x.toFixed(2)} unit="m" />
      </div>

      {showGraph ? <VTGraph trace={trace} /> : null}

      <div className="sci-controls">
        <Control label="Applied force" value={force} min={0} max={100} step={0.5} suffix=" N" disabled={phase === "running"} onChange={(v) => { setForce(v); reset(); }} />
        <Control label="Mass" value={mass} min={0.5} max={20} step={0.5} suffix=" kg" disabled={phase === "running"} onChange={(v) => { setMass(v); reset(); }} />
        <Control label="Friction (µ)" value={mu} min={0} max={0.8} step={0.02} disabled={phase === "running"} onChange={(v) => { setMu(v); reset(); }} />
        <Control label="Incline" value={incline} min={0} max={40} step={1} suffix="°" disabled={phase === "running"} onChange={(v) => { setIncline(v); reset(); }} />
      </div>

      {phase === "predict" ? (
        <>
          <Predict
            prompt={predictPrompt}
            options={[
              { id: "still", label: "It stays still" },
              { id: "constant", label: "Constant speed" },
              { id: "accelerating", label: "It accelerates" },
            ]}
            chosen={guess}
            onChoose={setGuess}
          />
          <button className="btn-primary" disabled={!guess} onClick={run}>
            {guess ? "Release the trolley" : "Predict first, then run"}
          </button>
        </>
      ) : null}

      {phase === "done" ? (
        <>
          <Verdict correct={guess === outcome}>
            <Explanation outcome={outcome} physics={physics} mass={mass} force={force} accel={accel} incline={incline} />
          </Verdict>
          <button className="btn-secondary" onClick={reset}>
            Change the forces and try again
          </button>
        </>
      ) : null}
    </SciencePanel>
  );
}

function Explanation({
  outcome,
  physics,
  mass,
  force,
  accel,
  incline,
}: {
  outcome: Outcome;
  physics: { staticLimit: number; kinetic: number; netDriving: number; weightAlong: number };
  mass: number;
  force: number;
  accel: number;
  incline: number;
}) {
  if (outcome === "still") {
    return (
      <>
        The trolley did not move. Your {force.toFixed(1)} N
        {incline > 0 ? `, minus the ${physics.weightAlong.toFixed(1)} N of weight pulling it back down the slope,` : ""}{" "}
        leaves {physics.netDriving.toFixed(1)} N trying to shift it — and static friction can resist
        up to {physics.staticLimit.toFixed(1)} N. Static friction is not a fixed force: it grows to
        match whatever you apply, until it runs out. You have not run it out yet.
      </>
    );
  }
  if (outcome === "constant") {
    return (
      <>
        The trolley moved at a near-constant speed. The driving force and kinetic friction
        ({physics.kinetic.toFixed(1)} N) are almost balanced, so the net force is roughly zero and
        so is the acceleration. This is the point SPM marks hardest: <em>moving</em> and{" "}
        <em>accelerating</em> are different things. No net force does not mean no motion — it means
        no <em>change</em> in motion.
      </>
    );
  }
  return (
    <>
      The trolley accelerated at {accel.toFixed(2)} m/s². Once you beat static friction
      ({physics.staticLimit.toFixed(1)} N), the leftover force divides by the mass:{" "}
      {physics.netDriving.toFixed(1)} N − {physics.kinetic.toFixed(1)} N of kinetic friction, over{" "}
      {mass.toFixed(1)} kg. Watch the velocity-time graph: a straight sloping line means constant
      acceleration, and its gradient <em>is</em> the acceleration.
    </>
  );
}

function Readout({ label, value, unit }: { label: string; value: string; unit: string }) {
  return (
    <div className="readout">
      <span className="readout-label">{label}</span>
      <span className="readout-value">
        {value}
        <em>{unit}</em>
      </span>
    </div>
  );
}

function Track({ x, incline }: { x: number; incline: number }) {
  const pct = (x / TRACK_M) * 100;
  return (
    <div className="track-wrap">
      <div className="track" style={{ transform: `rotate(${-incline}deg)` }}>
        <div className="track-line" />
        <div className="trolley" style={{ left: `${pct}%` }}>
          <svg viewBox="0 0 48 32" width="44" height="30" aria-label="trolley">
            <rect x="4" y="6" width="40" height="14" rx="3" className="trolley-body" />
            <circle cx="14" cy="24" r="6" className="trolley-wheel" />
            <circle cx="34" cy="24" r="6" className="trolley-wheel" />
          </svg>
        </div>
        {incline > 0 ? <span className="track-angle">{incline}°</span> : null}
      </div>
    </div>
  );
}

/** Plotted from the same samples the trolley moved through. */
function VTGraph({ trace }: { trace: Sample[] }) {
  const W = 320;
  const H = 110;
  const maxV = Math.max(1, ...trace.map((s) => Math.abs(s.v)));
  const maxT = 4;

  const points = trace
    .map((s) => `${(s.t / maxT) * W},${H - (Math.abs(s.v) / maxV) * (H - 12) - 6}`)
    .join(" ");

  return (
    <figure className="graph">
      <figcaption>Velocity–time</figcaption>
      <svg viewBox={`0 0 ${W} ${H}`} className="graph-svg" role="img" aria-label="velocity time graph">
        <line x1="0" y1={H - 6} x2={W} y2={H - 6} className="axis" />
        <line x1="0" y1="0" x2="0" y2={H} className="axis" />
        {trace.length > 1 ? <polyline points={points} className="trace" /> : null}
      </svg>
      <div className="graph-axes">
        <span>0</span>
        <span>time (s) →</span>
        <span>{maxV.toFixed(1)} m/s</span>
      </div>
    </figure>
  );
}
