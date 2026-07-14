"use client";

/**
 * Circuit builder.
 *
 * Aimed at the misconception that current is "used up" as it travels — so the
 * per-resistor readouts always show current, and in series they are always
 * identical, which is the thing that has to be seen rather than asserted.
 *
 * v1 seeded state from props and then let the resistors go uneditable, which
 * left it a demo. Here every value the model fills stays live in the student's
 * hands.
 */

import { useMemo, useState } from "react";
import { Control, Predict, SciencePanel, Verdict, slotArr, slotBool, slotNum, slotStr, type ScienceProps } from "./shared";

export default function CircuitSandbox({ slots, onInteraction }: ScienceProps) {
  const showWork = slotBool(slots, "show_calculation", true);
  const predictPrompt = slotStr(
    slots,
    "predict_prompt",
    "What happens to the total current if you add another resistor?",
  );

  const [emf, setEmf] = useState(() => slotNum(slots, "emf_v", 6));
  const [topology, setTopology] = useState<"series" | "parallel">(
    () => (slotStr(slots, "topology", "series") === "parallel" ? "parallel" : "series"),
  );
  const [resistors, setResistors] = useState<number[]>(() => {
    const seed = slotArr<number>(slots, "resistors_ohm", [10, 20]).filter(
      (r) => typeof r === "number" && r > 0,
    );
    return seed.length ? seed : [10, 20];
  });
  const [guess, setGuess] = useState<string | null>(null);
  const [revealed, setRevealed] = useState(false);

  const solved = useMemo(() => {
    const total =
      topology === "series"
        ? resistors.reduce((s, r) => s + r, 0)
        : 1 / resistors.reduce((s, r) => s + 1 / r, 0);
    const current = emf / total;
    const branches = resistors.map((r) =>
      topology === "series"
        ? { r, i: current, v: current * r }
        : { r, i: emf / r, v: emf },
    );
    return { total, current, branches };
  }, [emf, resistors, topology]);

  const addResistor = () => {
    if (resistors.length >= 4) return;
    const next = [...resistors, 10];
    setResistors(next);
    setRevealed(true);
    onInteraction?.("added a resistor", {
      topology,
      resistor_count: next.length,
      total_resistance: Number(solved.total.toFixed(2)),
      emf_v: emf,
    });
  };

  const removeResistor = (i: number) => {
    if (resistors.length <= 1) return;
    setResistors(resistors.filter((_, j) => j !== i));
  };

  return (
    <SciencePanel title="Circuit builder" subject="physics" badge={`V = IR · ${topology}`}>
      <CircuitDiagram emf={emf} branches={solved.branches} topology={topology} />

      <div className="readouts">
        <div className="readout">
          <span className="readout-label">Total resistance</span>
          <span className="readout-value">{solved.total.toFixed(2)}<em>Ω</em></span>
        </div>
        <div className="readout">
          <span className="readout-label">Total current</span>
          <span className="readout-value">{solved.current.toFixed(3)}<em>A</em></span>
        </div>
        <div className="readout">
          <span className="readout-label">Supply</span>
          <span className="readout-value">{emf.toFixed(1)}<em>V</em></span>
        </div>
      </div>

      {showWork ? (
        <div className="working">
          <code>
            {topology === "series"
              ? `R = ${resistors.map((r) => r.toFixed(1)).join(" + ")} = ${solved.total.toFixed(2)} Ω`
              : `1/R = ${resistors.map((r) => `1/${r.toFixed(1)}`).join(" + ")}  →  R = ${solved.total.toFixed(2)} Ω`}
          </code>
          <code>
            I = V/R = {emf.toFixed(1)} / {solved.total.toFixed(2)} = {solved.current.toFixed(3)} A
          </code>
        </div>
      ) : null}

      <div className="sci-controls">
        <Control label="Supply voltage" value={emf} min={0} max={24} step={0.5} suffix=" V" onChange={setEmf} />
        {resistors.map((r, i) => (
          <div className="res-row" key={i}>
            <Control
              label={`R${i + 1}`}
              value={r}
              min={1}
              max={100}
              step={1}
              suffix=" Ω"
              onChange={(v) => setResistors(resistors.map((x, j) => (j === i ? v : x)))}
            />
            {resistors.length > 1 ? (
              <button className="res-del" onClick={() => removeResistor(i)} aria-label={`Remove R${i + 1}`}>
                ×
              </button>
            ) : null}
          </div>
        ))}
      </div>

      <div className="btn-row">
        <button
          className="btn-secondary"
          onClick={() => setTopology(topology === "series" ? "parallel" : "series")}
        >
          Switch to {topology === "series" ? "parallel" : "series"}
        </button>
        <button className="btn-secondary" onClick={addResistor} disabled={resistors.length >= 4}>
          Add a resistor
        </button>
      </div>

      {!revealed ? (
        <>
          <Predict
            prompt={predictPrompt}
            options={[
              { id: "up", label: "Current goes up" },
              { id: "down", label: "Current goes down" },
              { id: "same", label: "No change" },
            ]}
            chosen={guess}
            onChoose={setGuess}
          />
          <button className="btn-primary" disabled={!guess} onClick={addResistor}>
            {guess ? "Add one and see" : "Predict first"}
          </button>
        </>
      ) : (
        <Verdict correct={guess === (topology === "series" ? "down" : "up")}>
          {topology === "series" ? (
            <>
              In series, resistances add, so total resistance rose and the current fell to{" "}
              {solved.current.toFixed(3)} A. Look at the per-resistor readings: the current is{" "}
              <strong>identical</strong> through every resistor. Current is not consumed as it goes
              round — the same charge that leaves the cell returns to it. What gets shared out is
              the <em>voltage</em>.
            </>
          ) : (
            <>
              In parallel, each new resistor opens another path, so total resistance <em>falls</em>{" "}
              (below even the smallest single resistor) and total current rises to{" "}
              {solved.current.toFixed(3)} A. Each branch sees the full {emf.toFixed(1)} V, and draws
              current according to its own resistance.
            </>
          )}
        </Verdict>
      )}
    </SciencePanel>
  );
}

function CircuitDiagram({
  emf,
  branches,
  topology,
}: {
  emf: number;
  branches: { r: number; i: number; v: number }[];
  topology: "series" | "parallel";
}) {
  // Line thickness tracks current, so "more current" is legible at a glance.
  const width = (i: number) => Math.max(1.2, Math.min(5, i * 8));

  return (
    <div className="circuit">
      <svg viewBox="0 0 320 160" className="circuit-svg" role="img" aria-label={`${topology} circuit`}>
        <g className="cell">
          <line x1="20" y1="60" x2="20" y2="100" strokeWidth="4" />
          <line x1="30" y1="70" x2="30" y2="90" strokeWidth="2" />
          <text x="14" y="120" className="circuit-text">{emf.toFixed(1)}V</text>
        </g>

        {topology === "series" ? (
          <SeriesPath branches={branches} width={width} />
        ) : (
          <ParallelPath branches={branches} width={width} />
        )}
      </svg>
    </div>
  );
}

function SeriesPath({
  branches,
  width,
}: {
  branches: { r: number; i: number; v: number }[];
  width: (i: number) => number;
}) {
  const span = 260 / branches.length;
  return (
    <g>
      <polyline
        points={`20,60 20,30 ${20 + 260},30 ${280},60`}
        className="wire"
        strokeWidth={width(branches[0]?.i ?? 0)}
      />
      <polyline
        points={`20,100 20,130 280,130 280,100`}
        className="wire"
        strokeWidth={width(branches[0]?.i ?? 0)}
      />
      <line x1="280" y1="60" x2="280" y2="100" className="wire" strokeWidth={width(branches[0]?.i ?? 0)} />
      {branches.map((b, i) => (
        <g key={i}>
          <rect x={40 + i * span} y="20" width={span * 0.5} height="20" className="resistor" />
          <text x={40 + i * span} y="14" className="circuit-text">
            {b.r.toFixed(0)}Ω
          </text>
          <text x={40 + i * span} y="54" className="circuit-text is-live">
            {b.i.toFixed(2)}A · {b.v.toFixed(1)}V
          </text>
        </g>
      ))}
    </g>
  );
}

function ParallelPath({
  branches,
  width,
}: {
  branches: { r: number; i: number; v: number }[];
  width: (i: number) => number;
}) {
  const total = branches.reduce((s, b) => s + b.i, 0);
  return (
    <g>
      <line x1="20" y1="60" x2="20" y2="20" className="wire" strokeWidth={width(total)} />
      <line x1="20" y1="20" x2="280" y2="20" className="wire" strokeWidth={width(total)} />
      <line x1="20" y1="100" x2="20" y2="145" className="wire" strokeWidth={width(total)} />
      <line x1="20" y1="145" x2="280" y2="145" className="wire" strokeWidth={width(total)} />
      {branches.map((b, i) => {
        const x = 90 + i * (190 / Math.max(1, branches.length));
        return (
          <g key={i}>
            <line x1={x} y1="20" x2={x} y2="60" className="wire" strokeWidth={width(b.i)} />
            <rect x={x - 10} y="62" width="20" height="42" className="resistor" />
            <line x1={x} y1="106" x2={x} y2="145" className="wire" strokeWidth={width(b.i)} />
            <text x={x + 14} y="80" className="circuit-text">{b.r.toFixed(0)}Ω</text>
            <text x={x + 14} y="96" className="circuit-text is-live">{b.i.toFixed(2)}A</text>
          </g>
        );
      })}
    </g>
  );
}
