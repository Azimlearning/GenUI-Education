"use client";

// Pattern: gradient-diffusion-sandbox (flagship — osmosis / water in plants).
// Faithful predict-observe-explain sim: the student commits to a prediction, then watches water
// move across a selectively-permeable membrane TOWARD the higher-solute side (down the water-
// potential gradient). The osmosis-inverted-gradient misconception ("water moves to where there
// is more water") fails visibly. Science is encoded here, not faked (constraint #6):
// net water flux is always from lower solute → higher solute.

import { useState } from "react";
import type { CSSProperties } from "react";

import { PatternCard, type LibraryComponentProps } from "./shared";

type Guess = "toward-higher-solute" | "toward-lower-solute" | "none";
type Phase = "predict" | "running" | "explain";

export default function GradientDiffusionSandbox({ props, meta }: LibraryComponentProps) {
  const left = clamp(Number(props.left_concentration ?? 20));
  const right = clamp(Number(props.right_concentration ?? 70));
  const cellMode = String(props.cell_mode ?? "beaker") === "plant-cell";
  const predictPrompt = String(props.predict_prompt ?? "Which way will the water move?");

  // The faithful truth: water moves toward whichever side has MORE solute.
  const higher: "left" | "right" | "equal" =
    right > left ? "right" : left > right ? "left" : "equal";
  const correctGuess: Guess = higher === "equal" ? "none" : "toward-higher-solute";

  const [guess, setGuess] = useState<Guess | null>(null);
  const [phase, setPhase] = useState<Phase>("predict");

  // Animated water offset: positive = water accumulates on the right (higher-solute side).
  const flow = phase === "explain" ? (higher === "right" ? 1 : higher === "left" ? -1 : 0) : 0;

  const wasRight = guess === correctGuess;

  return (
    <PatternCard title={cellMode ? "Osmosis in a plant cell" : "Osmosis sandbox"} meta={meta}>
      {/* ── The apparatus ── */}
      {cellMode ? (
        <PlantCell inner={left} outer={right} flow={flow} />
      ) : (
        <Beaker left={left} right={right} flow={flow} />
      )}

      {/* ── Step 1: predict ── */}
      <div style={{ marginTop: 16 }}>
        <p style={label}>
          <strong>Predict.</strong> {predictPrompt}
        </p>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          <GuessButton
            active={guess === "toward-higher-solute"}
            disabled={phase !== "predict"}
            onClick={() => setGuess("toward-higher-solute")}
            label={cellMode ? "Water leaves the cell (toward more solute)" : "Toward the higher-solute side"}
          />
          <GuessButton
            active={guess === "toward-lower-solute"}
            disabled={phase !== "predict"}
            onClick={() => setGuess("toward-lower-solute")}
            label={cellMode ? "Water enters the cell (toward more water)" : "Toward the side with more water"}
          />
          <GuessButton
            active={guess === "none"}
            disabled={phase !== "predict"}
            onClick={() => setGuess("none")}
            label="No net movement"
          />
        </div>
      </div>

      {/* ── Step 2: run ── */}
      {phase === "predict" && (
        <button
          style={{ ...runBtn, opacity: guess ? 1 : 0.5, cursor: guess ? "pointer" : "not-allowed" }}
          disabled={!guess}
          onClick={() => {
            setPhase("running");
            // brief "running" beat so the water visibly moves, then reveal.
            window.setTimeout(() => setPhase("explain"), 1400);
          }}
        >
          Run the experiment →
        </button>
      )}
      {phase === "running" && <p style={{ ...label, color: "var(--teal)" }}>Water is moving…</p>}

      {/* ── Step 3: explain ── */}
      {phase === "explain" && (
        <Explanation
          wasRight={wasRight}
          higher={higher}
          left={left}
          right={right}
          cellMode={cellMode}
          onRetry={() => {
            setGuess(null);
            setPhase("predict");
          }}
        />
      )}
    </PatternCard>
  );
}

// ── Beaker: two compartments, membrane between; water level shifts toward higher solute ──
function Beaker({ left, right, flow }: { left: number; right: number; flow: number }) {
  const shift = flow * 22; // px the water surface moves
  return (
    <div style={{ display: "flex", alignItems: "stretch", gap: 6, height: 150 }}>
      <Compartment label="Left" conc={left} level={70 - shift} />
      <div style={membrane} title="selectively-permeable membrane" aria-label="membrane">
        {flow !== 0 && <Droplets direction={flow > 0 ? "right" : "left"} />}
      </div>
      <Compartment label="Right" conc={right} level={70 + shift} />
    </div>
  );
}

function Compartment({ label, conc, level }: { label: string; conc: number; level: number }) {
  return (
    <div style={{ flex: 1, position: "relative", border: "1px solid var(--line)", borderRadius: 10, overflow: "hidden", background: "#f8fafc" }}>
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          bottom: 0,
          height: `${clamp(level)}%`,
          background: `linear-gradient(180deg, rgba(13,148,136,0.28), rgba(13,148,136,${0.35 + conc / 250}))`,
          transition: "height 1.1s ease-in-out",
        }}
      />
      <div style={{ position: "absolute", top: 8, left: 0, right: 0, textAlign: "center" }}>
        <div style={{ fontSize: 11, color: "var(--slate)", fontWeight: 700 }}>{label}</div>
        <div style={{ fontSize: 20, fontWeight: 800, color: "var(--teal)" }}>{conc}</div>
        <div style={{ fontSize: 10, color: "var(--slate)" }}>solute conc.</div>
      </div>
    </div>
  );
}

// ── Plant cell: cytoplasm gains/loses water → turgid or plasmolysed ──
function PlantCell({ inner, outer, flow }: { inner: number; outer: number; flow: number }) {
  // flow > 0 means net water toward the higher-solute side. If outer solute is higher, water
  // leaves the cell → it shrinks (plasmolysis). If inner is higher, water enters → turgid.
  const waterLeaves = outer > inner;
  const scale = flow === 0 ? 0.86 : waterLeaves ? 0.66 : 0.98;
  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: 150, background: "#f8fafc", border: "1px solid var(--line)", borderRadius: 10 }}>
      <div style={{ position: "relative", width: 150, height: 110, border: "2px solid #14532d", borderRadius: 8, background: "#dcfce7" }}>
        <div
          style={{
            position: "absolute",
            inset: 0,
            margin: "auto",
            width: "88%",
            height: "88%",
            transform: `scale(${scale})`,
            transformOrigin: "center",
            transition: "transform 1.1s ease-in-out",
            background: "#86efac",
            border: "1px solid #16a34a",
            borderRadius: 6,
          }}
          title="cytoplasm"
        />
        <span style={{ position: "absolute", bottom: 4, right: 6, fontSize: 10, color: "#14532d" }}>
          outer solution: {outer}
        </span>
      </div>
    </div>
  );
}

function Droplets({ direction }: { direction: "left" | "right" }) {
  return (
    <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", justifyContent: "space-around" }}>
      {[0, 1, 2].map((i) => (
        <span
          key={i}
          style={{
            fontSize: 10,
            color: "var(--teal)",
            textAlign: "center",
            animation: "fade 0.9s ease-in-out infinite",
          }}
        >
          {direction === "right" ? "→" : "←"}
        </span>
      ))}
    </div>
  );
}

function GuessButton({ active, disabled, onClick, label }: { active: boolean; disabled: boolean; onClick: () => void; label: string }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{
        ...guessBtn,
        border: active ? "2px solid var(--indigo-2)" : "1px solid var(--line)",
        background: active ? "var(--indigo-soft)" : "var(--white)",
        color: active ? "var(--indigo)" : "var(--slate)",
        cursor: disabled ? "default" : "pointer",
        opacity: disabled && !active ? 0.55 : 1,
      }}
    >
      {label}
    </button>
  );
}

function Explanation({ wasRight, higher, left, right, cellMode, onRetry }: {
  wasRight: boolean;
  higher: "left" | "right" | "equal";
  left: number;
  right: number;
  cellMode: boolean;
  onRetry: () => void;
}) {
  const hiConc = higher === "left" ? left : right;
  const loConc = higher === "left" ? right : left;
  const body =
    higher === "equal"
      ? "The two solutions have equal solute concentration, so there is no water-potential gradient and no net movement."
      : `Water moved toward the ${higher} side, which has the HIGHER solute concentration (${hiConc} vs ${loConc}). ` +
        "Osmosis is the net movement of water across a selectively permeable membrane from a region of " +
        "lower solute concentration to higher solute concentration — down the water-potential gradient. " +
        (cellMode
          ? higher === "left"
            ? "With more solute inside, water enters and the cell becomes turgid."
            : "With more solute outside, water leaves and the cell plasmolyses (wilts)."
          : "Water moves toward more solute, not toward more water.");
  return (
    <div style={{ marginTop: 14, borderRadius: 12, padding: 14, animation: "fade .3s", background: wasRight ? "var(--teal-soft)" : "#fff7ed", border: `1px solid ${wasRight ? "var(--teal)" : "#fed7aa"}` }}>
      <div style={{ fontWeight: 800, color: wasRight ? "var(--teal)" : "var(--amber)", marginBottom: 4 }}>
        {wasRight ? "Correct — nicely predicted." : "Not quite — watch what actually happened."}
      </div>
      <p style={{ margin: "0 0 10px", fontSize: 14, color: "var(--ink)" }}>{body}</p>
      <button style={retryBtn} onClick={onRetry}>
        Try another prediction
      </button>
    </div>
  );
}

function clamp(n: number): number {
  if (Number.isNaN(n)) return 0;
  return Math.max(0, Math.min(100, n));
}

// ── styles ──
const label: CSSProperties = { fontSize: 14, color: "var(--ink)", margin: "0 0 8px" };
const membrane: CSSProperties = {
  position: "relative",
  width: 10,
  borderRadius: 3,
  background:
    "repeating-linear-gradient(0deg,var(--indigo-2),var(--indigo-2) 4px,transparent 4px,transparent 8px)",
};
const guessBtn: CSSProperties = {
  fontSize: 12.5,
  padding: "8px 12px",
  borderRadius: 10,
  fontFamily: "inherit",
  fontWeight: 600,
  flex: "1 1 30%",
  minWidth: 140,
};
const runBtn: CSSProperties = {
  marginTop: 14,
  background: "var(--indigo)",
  color: "#fff",
  border: "none",
  padding: "10px 18px",
  borderRadius: 10,
  fontSize: 14,
  fontWeight: 700,
  fontFamily: "inherit",
};
const retryBtn: CSSProperties = {
  background: "var(--white)",
  border: "1px solid var(--line)",
  color: "var(--slate)",
  padding: "6px 12px",
  borderRadius: 8,
  fontSize: 12.5,
  fontFamily: "inherit",
  cursor: "pointer",
};
