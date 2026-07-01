// Pattern: gradient-diffusion-sandbox (flagship — osmosis, diffusion, dialysis, gas exchange).
// P0 placeholder. P1 makes this a faithful predict-observe-explain sim (water flux follows the
// solute gradient; the student's wrong prediction fails visibly).

import { ComingSoon, LibraryComponentProps, PatternCard, PropList } from "./shared";

export default function GradientDiffusionSandbox({ props, meta }: LibraryComponentProps) {
  const left = Number(props.left_concentration ?? 0);
  const right = Number(props.right_concentration ?? 0);
  return (
    <PatternCard title="Gradient / diffusion sandbox" meta={meta}>
      <div style={{ display: "flex", gap: 8, marginBottom: 14 }}>
        <Compartment label="Left" value={left} />
        <div
          style={{
            width: 6,
            borderRadius: 3,
            background: "repeating-linear-gradient(0deg,var(--indigo-2),var(--indigo-2) 4px,transparent 4px,transparent 8px)",
          }}
          title="selectively permeable membrane"
        />
        <Compartment label="Right" value={right} />
      </div>
      <p style={{ fontSize: 14, color: "var(--ink)", margin: "0 0 4px" }}>
        <strong>Predict:</strong> {String(props.predict_prompt ?? "Which way will it move?")}
      </p>
      <PropList props={props} />
      <ComingSoon phase="P1" />
    </PatternCard>
  );
}

function Compartment({ label, value }: { label: string; value: number }) {
  return (
    <div
      style={{
        flex: 1,
        border: "1px solid var(--line)",
        borderRadius: 10,
        padding: 12,
        textAlign: "center",
        background: "var(--teal-soft)",
      }}
    >
      <div style={{ fontSize: 12, color: "var(--slate)", fontWeight: 600 }}>{label}</div>
      <div style={{ fontSize: 22, fontWeight: 800, color: "var(--teal)" }}>{value}</div>
      <div style={{ fontSize: 11, color: "var(--slate)" }}>solute conc.</div>
    </div>
  );
}
