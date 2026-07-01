// The visible agent pipeline (D-03 — the differentiator, and the demo wow).
// Rendered as a single connected reasoning trace: numbered steps down a vertical rail, each
// agent thinking then concluding, live, as the SSE events arrive. This is deliberately NOT four
// identical floating cards — it should read as one continuous chain of reasoning.

import type { CSSProperties } from "react";
import { AGENT_LABEL, type AgentName, type AgentStep } from "@/lib/types";

const ORDER: AgentName[] = [
  "diagnostician",
  "pedagogy_strategist",
  "component_composer",
  "tutor_loop",
];

type StepState = "thinking" | "done" | "skipped";

export default function AgentPipeline({ steps }: { steps: AgentStep[] }) {
  if (steps.length === 0) return null;

  const byAgent = new Map<AgentName, AgentStep[]>();
  for (const s of steps) {
    if (!byAgent.has(s.agent)) byAgent.set(s.agent, []);
    byAgent.get(s.agent)!.push(s);
  }

  const active = ORDER.filter((a) => byAgent.has(a));

  return (
    <section style={panel}>
      <div style={panelLabel}>Reasoning trace</div>
      <ol style={list}>
        {active.map((agent, i) => (
          <TraceStep
            key={agent}
            index={i + 1}
            agent={agent}
            steps={byAgent.get(agent)!}
            isLast={i === active.length - 1}
          />
        ))}
      </ol>
    </section>
  );
}

function TraceStep({
  index,
  agent,
  steps,
  isLast,
}: {
  index: number;
  agent: AgentName;
  steps: AgentStep[];
  isLast: boolean;
}) {
  const state: StepState = steps.every((s) => s.status === "skipped")
    ? "skipped"
    : steps.some((s) => s.status === "done")
      ? "done"
      : "thinking";

  return (
    <li style={{ ...row, paddingBottom: isLast ? 0 : 22 }}>
      {!isLast && <span style={connector} aria-hidden />}
      <span style={dot(state)}>{index}</span>
      <div style={content}>
        <div style={stepHead}>
          <span style={agentName}>{AGENT_LABEL[agent]}</span>
          <span style={statusText(state)}>
            {state === "skipped" ? "skipped" : state === "done" ? "done" : "thinking…"}
          </span>
        </div>
        <div style={{ display: "grid", gap: 3 }}>
          {steps.map((s, i) => (
            <p
              key={i}
              style={{
                margin: 0,
                fontSize: 14,
                lineHeight: 1.55,
                color: s.status === "thinking" ? "var(--slate)" : "var(--ink)",
              }}
            >
              {s.detail}
            </p>
          ))}
        </div>
      </div>
    </li>
  );
}

// ── styles ──
const panel: CSSProperties = {
  marginTop: 28,
  background: "var(--white)",
  border: "1px solid var(--line)",
  borderRadius: 14,
  padding: "20px 22px",
  animation: "fade .3s",
};
const panelLabel: CSSProperties = {
  fontSize: 12,
  fontWeight: 600,
  textTransform: "uppercase",
  letterSpacing: 1.2,
  color: "var(--slate)",
  marginBottom: 18,
};
const list: CSSProperties = {
  listStyle: "none",
  margin: 0,
  padding: 0,
};
const row: CSSProperties = {
  position: "relative",
  paddingLeft: 40,
};
const DOT = 26;
const connector: CSSProperties = {
  position: "absolute",
  left: (DOT - 2) / 2, // center on the dot
  top: DOT + 2,
  bottom: 0,
  width: 2,
  background: "var(--line)",
};
function dot(state: StepState): CSSProperties {
  const palette = {
    done: { bg: "var(--indigo)", color: "#fff", border: "var(--indigo)" },
    thinking: { bg: "var(--white)", color: "var(--indigo)", border: "var(--indigo-2)" },
    skipped: { bg: "#f1f5f9", color: "var(--slate)", border: "var(--line)" },
  }[state];
  return {
    position: "absolute",
    left: 0,
    top: 0,
    width: DOT,
    height: DOT,
    borderRadius: 999,
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: 12,
    fontWeight: 700,
    fontVariantNumeric: "tabular-nums",
    background: palette.bg,
    color: palette.color,
    border: `1.5px solid ${palette.border}`,
    zIndex: 1,
  };
}
const content: CSSProperties = { paddingTop: 1 };
const stepHead: CSSProperties = {
  display: "flex",
  alignItems: "baseline",
  gap: 10,
  marginBottom: 5,
};
const agentName: CSSProperties = {
  fontFamily: "var(--font-display)",
  fontSize: 16,
  fontWeight: 600,
  color: "var(--ink)",
};
function statusText(state: StepState): CSSProperties {
  const color =
    state === "done" ? "var(--teal)" : state === "skipped" ? "var(--slate)" : "var(--indigo-2)";
  return {
    fontSize: 11,
    fontWeight: 600,
    textTransform: "uppercase",
    letterSpacing: 0.8,
    color,
  };
}
