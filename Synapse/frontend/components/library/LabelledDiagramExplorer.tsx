// Pattern: labelled-diagram-explorer (animal/plant cell, heart, electrolytic cell).
// P0 placeholder.

import { ComingSoon, LibraryComponentProps, PatternCard, PropList } from "./shared";

export default function LabelledDiagramExplorer({ props, meta }: LibraryComponentProps) {
  return (
    <PatternCard title="Labelled diagram explorer" meta={meta}>
      <p style={{ fontSize: 14, color: "var(--ink)", margin: "0 0 10px" }}>
        Diagram: <strong>{String(props.diagram ?? "—")}</strong> · mode:{" "}
        <strong>{String(props.mode ?? "explore")}</strong>
      </p>
      <PropList props={props} />
      <ComingSoon phase="P2" />
    </PatternCard>
  );
}
