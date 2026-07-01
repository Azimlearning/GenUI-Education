// Pattern: force-motion-sim (Newton's laws, momentum, friction).
// P0 placeholder.

import { ComingSoon, LibraryComponentProps, PatternCard, PropList } from "./shared";

export default function ForceMotionSim({ props, meta }: LibraryComponentProps) {
  return (
    <PatternCard title="Force & motion sandbox" meta={meta}>
      <PropList props={props} />
      <ComingSoon phase="P2+" />
    </PatternCard>
  );
}
