// Renders a streamed ComponentBlock by resolving its pattern to a library component.
// If the backend sends a pattern the frontend doesn't know, we fail loud-but-graceful (a
// visible notice) rather than throwing — schema drift between the two halves is the top D-10 risk.

import type { ComponentBlock } from "@/lib/types";
import { resolvePattern } from "@/lib/blocks";

export default function BlockRenderer({
  block,
  onInteraction,
}: {
  block: ComponentBlock;
  onInteraction?: (ev: { correct: boolean }) => void;
}) {
  const Component = resolvePattern(block.pattern);

  if (!Component) {
    return (
      <div
        style={{
          border: "1px solid var(--rose)",
          background: "#fff1f2",
          color: "var(--rose)",
          borderRadius: 12,
          padding: 16,
          fontSize: 14,
        }}
      >
        Unknown component pattern <code>{block.pattern}</code>. The backend registry and the
        frontend library map are out of sync (see D-10 / lib/blocks.ts).
      </div>
    );
  }

  return <Component props={block.props} meta={block.meta} onInteraction={onInteraction} />;
}
