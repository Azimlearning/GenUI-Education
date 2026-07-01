// Pattern: contrasting-pair-walkthrough (ionic vs covalent, mitosis vs meiosis, speed vs velocity).
// P0 placeholder.

import { ComingSoon, LibraryComponentProps, PatternCard, PropList } from "./shared";

export default function ContrastingPairWalkthrough({ props, meta }: LibraryComponentProps) {
  const left = String(props.left_label ?? "A");
  const right = String(props.right_label ?? "B");
  return (
    <PatternCard title="Contrasting-pair walkthrough" meta={meta}>
      <div style={{ display: "flex", gap: 10, marginBottom: 14 }}>
        <Pill label={left} />
        <span style={{ alignSelf: "center", color: "var(--slate)", fontWeight: 700 }}>vs</span>
        <Pill label={right} />
      </div>
      <PropList props={props} />
      <ComingSoon phase="P2" />
    </PatternCard>
  );
}

function Pill({ label }: { label: string }) {
  return (
    <div
      style={{
        flex: 1,
        textAlign: "center",
        padding: "10px 14px",
        borderRadius: 10,
        border: "1px solid var(--line)",
        background: "var(--indigo-soft)",
        fontWeight: 800,
        color: "var(--indigo)",
      }}
    >
      {label}
    </div>
  );
}
