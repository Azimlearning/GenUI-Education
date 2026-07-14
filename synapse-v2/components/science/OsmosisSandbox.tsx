"use client";

/**
 * Concentration gradient sandbox — the flagship.
 *
 * The misconception this exists to break: "water moves to where there is more
 * water." It is backwards, it is documented in the SPM cohort (Odom & Barrow
 * 1995), and a student holding it can still pass a written question by pattern-
 * matching. So: make them predict, then show them water crossing toward the
 * higher SOLUTE concentration, and name what just happened.
 *
 * Direction is DERIVED from the concentrations, never from a slot. The model
 * chooses the scenario; the science decides the outcome.
 */

import { useEffect, useMemo, useRef, useState } from "react";
import {
  Control,
  Predict,
  SciencePanel,
  Verdict,
  slotNum,
  slotStr,
  type ScienceProps,
} from "./shared";

type Phase = "predict" | "running" | "done";

export default function OsmosisSandbox({ slots, onInteraction }: ScienceProps) {
  const solute = slotStr(slots, "solute", "sucrose");
  const scenario = slotStr(slots, "scenario", "beaker") as "beaker" | "plant-cell" | "animal-cell";
  const temperature = slotNum(slots, "temperature_c", 25);
  const predictPrompt = slotStr(slots, "predict_prompt", "Which way will the water move, and why?");

  const [left, setLeft] = useState(() => slotNum(slots, "left_concentration", 0.1));
  const [right, setRight] = useState(() => slotNum(slots, "right_concentration", 0.8));
  const [phase, setPhase] = useState<Phase>("predict");
  const [guess, setGuess] = useState<string | null>(null);
  const [t, setT] = useState(0);

  // The science. Water moves toward higher solute — down its OWN potential
  // gradient, which is the opposite of the solute's. Derived, never supplied.
  const truth = useMemo(() => {
    const diff = right - left;
    if (Math.abs(diff) < 0.02) return "none" as const;
    return diff > 0 ? ("right" as const) : ("left" as const);
  }, [left, right]);

  // Net flow slows as the gradient closes; rate scales with the difference and
  // (loosely) with temperature. Not a quantitative model, but the right shape.
  const rate = useMemo(
    () => Math.abs(right - left) * (0.6 + temperature / 120),
    [right, left, temperature],
  );

  const raf = useRef<number | null>(null);
  useEffect(() => {
    if (phase !== "running") return;
    let start: number | null = null;
    const tick = (ts: number) => {
      if (start === null) start = ts;
      const elapsed = (ts - start) / 1000;
      const progress = Math.min(1, elapsed / 3.2);
      setT(progress);
      if (progress < 1) raf.current = requestAnimationFrame(tick);
      else setPhase("done");
    };
    raf.current = requestAnimationFrame(tick);
    return () => {
      if (raf.current !== null) cancelAnimationFrame(raf.current);
    };
  }, [phase]);

  const run = () => {
    if (!guess) return;
    setT(0);
    setPhase("running");
    onInteraction?.("ran the osmosis simulation", {
      predicted: guess,
      actual: truth,
      correct: guess === truth,
      left_concentration: left,
      right_concentration: right,
      solute,
      scenario,
    });
  };

  const reset = () => {
    setPhase("predict");
    setGuess(null);
    setT(0);
  };

  // Eased flow: fast while the gradient is wide, tailing off as it equalises.
  const flow = (1 - Math.pow(1 - t, 2)) * Math.min(1, rate);
  const shift = truth === "none" ? 0 : (truth === "right" ? 1 : -1) * flow * 18;

  const options = [
    { id: "left", label: "Water moves left" },
    { id: "right", label: "Water moves right" },
    { id: "none", label: "No net movement" },
  ];

  return (
    <SciencePanel
      title="Concentration gradient sandbox"
      subject="biology"
      badge={`${solute} · ${temperature}°C`}
    >
      {scenario === "beaker" ? (
        <Beaker left={left} right={right} shift={shift} solute={solute} />
      ) : (
        <Cell
          left={left}
          right={right}
          flow={flow}
          direction={truth}
          animal={scenario === "animal-cell"}
        />
      )}

      <div className="sci-controls">
        <Control
          label={`Left ${solute}`}
          value={left}
          min={0}
          max={2}
          step={0.05}
          suffix=" M"
          disabled={phase === "running"}
          onChange={(v) => {
            setLeft(v);
            reset();
          }}
        />
        <Control
          label={`Right ${solute}`}
          value={right}
          min={0}
          max={2}
          step={0.05}
          suffix=" M"
          disabled={phase === "running"}
          onChange={(v) => {
            setRight(v);
            reset();
          }}
        />
      </div>

      {phase === "predict" ? (
        <>
          <Predict prompt={predictPrompt} options={options} chosen={guess} onChoose={setGuess} />
          <button className="btn-primary" disabled={!guess} onClick={run}>
            {guess ? "Run the experiment" : "Predict first, then run"}
          </button>
        </>
      ) : null}

      {phase === "running" ? <p className="sci-status">Running…</p> : null}

      {phase === "done" ? (
        <>
          <Verdict correct={guess === truth}>
            {truth === "none" ? (
              <>
                Both sides are at {left.toFixed(2)} M, so there is no concentration gradient. Water
                still crosses the membrane in both directions — but the two rates are equal, so
                there is no <em>net</em> movement. Equilibrium is busy, not still.
              </>
            ) : (
              <>
                Water moved <strong>{truth}</strong>, toward the {Math.max(left, right).toFixed(2)} M
                side — the side with <em>more {solute}</em>, and therefore <em>less water</em>. Water
                moves down its own concentration gradient: from where water is abundant to where it
                is scarce. That is the same thing as moving toward the higher solute concentration.
                {guess === (truth === "right" ? "left" : "right")
                  ? " You predicted the opposite, which is the most common way this is misremembered: water chases the water, not the solute."
                  : ""}
              </>
            )}
          </Verdict>
          <button className="btn-secondary" onClick={reset}>
            Change the concentrations and try again
          </button>
        </>
      ) : null}
    </SciencePanel>
  );
}

/* ------------------------------------------------------------- visuals */

function Beaker({
  left,
  right,
  shift,
  solute,
}: {
  left: number;
  right: number;
  shift: number;
  solute: string;
}) {
  const dots = (c: number, side: "l" | "r") => {
    const n = Math.round(c * 14);
    return Array.from({ length: n }, (_, i) => {
      // Deterministic scatter: same layout every render, no hydration mismatch.
      const seed = (i * 2654435761) % 1000;
      const x = 8 + ((seed % 100) / 100) * 84;
      const y = 10 + (((seed >> 3) % 100) / 100) * 76;
      return <circle key={`${side}${i}`} cx={`${x}%`} cy={`${y}%`} r="3.5" className="solute-dot" />;
    });
  };

  return (
    <div className="beaker">
      <div className="beaker-half" style={{ flex: 1 + shift / 100 }}>
        <span className="beaker-tag">{left.toFixed(2)} M</span>
        <svg className="beaker-fill" preserveAspectRatio="none" viewBox="0 0 100 100">
          <rect x="0" y="0" width="100" height="100" className="water" />
          {dots(left, "l")}
        </svg>
      </div>
      <div className="membrane" title="Selectively permeable: water passes, solute does not">
        <span>membrane</span>
      </div>
      <div className="beaker-half" style={{ flex: 1 - shift / 100 }}>
        <span className="beaker-tag">{right.toFixed(2)} M</span>
        <svg className="beaker-fill" preserveAspectRatio="none" viewBox="0 0 100 100">
          <rect x="0" y="0" width="100" height="100" className="water" />
          {dots(right, "r")}
        </svg>
      </div>
      <p className="beaker-cap">
        Dots are {solute} molecules — too large for the membrane. Only water crosses.
      </p>
    </div>
  );
}

function Cell({
  left,
  right,
  flow,
  direction,
  animal,
}: {
  left: number;
  right: number;
  flow: number;
  direction: "left" | "right" | "none";
  animal: boolean;
}) {
  // Inside is "left", the surrounding solution is "right".
  const gainsWater = direction === "left";
  const scale = direction === "none" ? 1 : gainsWater ? 1 + flow * 0.22 : 1 - flow * 0.3;

  const state = animal
    ? gainsWater
      ? flow > 0.7
        ? "lysed (burst)"
        : "swelling"
      : flow > 0.7
        ? "crenated (shrivelled)"
        : "shrinking"
    : gainsWater
      ? "turgid"
      : flow > 0.7
        ? "plasmolysed"
        : "flaccid";

  return (
    <div className="cellview">
      <div className="cell-outer">
        <span className="cell-tag">outside · {right.toFixed(2)} M</span>
        {!animal ? <div className="cell-wall" /> : null}
        <div
          className={`cell-membrane${animal ? " is-animal" : ""}`}
          style={{ transform: `scale(${scale})` }}
        >
          <span className="cell-inner-tag">{left.toFixed(2)} M</span>
        </div>
      </div>
      <p className="cell-state">
        {animal ? "Animal cell" : "Plant cell"}: <strong>{state}</strong>
        {!animal && direction === "right" && flow > 0.7
          ? " — the membrane has pulled away from the cell wall."
          : ""}
      </p>
    </div>
  );
}
