// Pattern: quick-check-quiz (balancing equations, unit checks, formula recall).
// P0 placeholder.

import { ComingSoon, LibraryComponentProps, PatternCard, PropList } from "./shared";

export default function QuickCheckQuiz({ props, meta }: LibraryComponentProps) {
  return (
    <PatternCard title="Quick-check quiz" meta={meta}>
      <p
        style={{
          fontSize: 15,
          fontWeight: 700,
          color: "var(--ink)",
          margin: "0 0 12px",
          fontFamily: "ui-monospace, monospace",
        }}
      >
        {String(props.prompt ?? "—")}
      </p>
      <PropList props={props} />
      <ComingSoon phase="P2" />
    </PatternCard>
  );
}
