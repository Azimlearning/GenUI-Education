// Pattern: titration-sandbox (acid-base titration, molarity, neutralisation).
// P0 placeholder.

import { ComingSoon, LibraryComponentProps, PatternCard, PropList } from "./shared";

export default function TitrationSandbox({ props, meta }: LibraryComponentProps) {
  return (
    <PatternCard title="Titration sandbox" meta={meta}>
      <PropList props={props} />
      <ComingSoon phase="P2+" />
    </PatternCard>
  );
}
