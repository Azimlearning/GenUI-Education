// Shared scaffolding for the component library.
//
// Every library component is a PLACEHOLDER in P0 — it renders the pattern's identity and the
// props the Composer sent, plus an honest note that the faithful interactive lands in P1/P2.
// The point of P0 is that a streamed `component_block` reaches the right component and hydrates
// with real props; the faithful physics/interaction is the next phase (D-06, STATUS.md).

import type { CSSProperties } from "react";
import type { BlockMeta } from "@/lib/types";

export interface LibraryComponentProps {
  props: Record<string, unknown>;
  meta: BlockMeta;
  // Optional callback so a component can report how the learner did (P3 — closes the loop).
  // The page combines this with the block's meta (topic, misconception_id) before posting.
  onInteraction?: (ev: { correct: boolean }) => void;
}

const card: CSSProperties = {
  background: "var(--white)",
  border: "1px solid var(--line)",
  borderRadius: 16,
  boxShadow: "var(--shadow)",
  overflow: "hidden",
  animation: "fade .3s",
};

const head: CSSProperties = {
  display: "flex",
  alignItems: "center",
  gap: 12,
  padding: "16px 20px",
  borderBottom: "1px solid var(--line)",
  background: "var(--indigo-soft)",
};

const badge: CSSProperties = {
  fontSize: 12,
  fontWeight: 700,
  color: "var(--teal)",
  background: "var(--teal-soft)",
  padding: "4px 10px",
  borderRadius: 20,
  whiteSpace: "nowrap",
};

export function PatternCard({
  title,
  meta,
  children,
}: {
  title: string;
  meta: BlockMeta;
  children?: React.ReactNode;
}) {
  return (
    <div style={card}>
      <div style={head}>
        <div>
          <div style={{ fontSize: 17, fontWeight: 800, color: "var(--indigo)" }}>{title}</div>
          <div style={{ fontSize: 13, color: "var(--slate)" }}>
            {meta.subject} · Form {meta.form} · {meta.topic}
          </div>
        </div>
        <span style={{ ...badge, marginLeft: "auto" }}>{meta.strategy}</span>
      </div>
      <div style={{ padding: 20 }}>{children}</div>
    </div>
  );
}

export function PropList({ props }: { props: Record<string, unknown> }) {
  const entries = Object.entries(props);
  if (entries.length === 0) {
    return <p style={{ color: "var(--slate)", fontSize: 14 }}>No parameters configured.</p>;
  }
  return (
    <dl
      style={{
        display: "grid",
        gridTemplateColumns: "max-content 1fr",
        gap: "6px 16px",
        margin: 0,
        fontSize: 14,
      }}
    >
      {entries.map(([k, v]) => (
        <div key={k} style={{ display: "contents" }}>
          <dt style={{ color: "var(--slate)", fontWeight: 600 }}>{k}</dt>
          <dd style={{ margin: 0, color: "var(--ink)" }}>
            {typeof v === "object" ? JSON.stringify(v) : String(v)}
          </dd>
        </div>
      ))}
    </dl>
  );
}

export function ComingSoon({ phase }: { phase: string }) {
  return (
    <p
      style={{
        marginTop: 16,
        fontSize: 12.5,
        color: "var(--amber)",
        background: "#fff7ed",
        border: "1px solid #fed7aa",
        borderRadius: 10,
        padding: "8px 12px",
      }}
    >
      Placeholder — the faithful interactive for this pattern is built in {phase}. In P0 this
      proves the streamed component block reached the right component with real props.
    </p>
  );
}
