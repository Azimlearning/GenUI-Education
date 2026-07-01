// The visible agent pipeline (D-03 — the differentiator, and the demo wow).
// Renders the streamed `agent_step` events grouped by agent, showing each agent thinking then
// concluding, live, as the SSE events arrive.

import type { CSSProperties } from "react";
import { AGENT_LABEL, type AgentName, type AgentStep } from "@/lib/types";

const ORDER: AgentName[] = [
  "diagnostician",
  "pedagogy_strategist",
  "component_composer",
  "tutor_loop",
];

const ACCENT: Record<AgentName, string> = {
  diagnostician: "var(--indigo)",
  pedagogy_strategist: "var(--indigo-2)",
  component_composer: "var(--teal)",
  tutor_loop: "var(--amber)",
};

export default function AgentPipeline({ steps }: { steps: AgentStep[] }) {
  if (steps.length === 0) return null;

  const byAgent = new Map<AgentName, AgentStep[]>();
  for (const s of steps) {
    if (!byAgent.has(s.agent)) byAgent.set(s.agent, []);
    byAgent.get(s.agent)!.push(s);
  }

  const active = ORDER.filter((a) => byAgent.has(a));

  return (
    <div style={{ display: "grid", gap: 12, marginTop: 24 }}>
      <div style={labelRow}>The agents, reasoning</div>
      {active.map((agent) => (
        <AgentCard key={agent} agent={agent} steps={byAgent.get(agent)!} />
      ))}
    </div>
  );
}

function AgentCard({ agent, steps }: { agent: AgentName; steps: AgentStep[] }) {
  const accent = ACCENT[agent];
  const isDone = steps.some((s) => s.status === "done");
  const isSkipped = steps.every((s) => s.status === "skipped");

  return (
    <div style={{ ...card, borderLeft: `4px solid ${accent}` }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
        <span style={{ fontWeight: 800, color: accent, fontSize: 14 }}>{AGENT_LABEL[agent]}</span>
        <span style={statusPill(isSkipped ? "skipped" : isDone ? "done" : "thinking")}>
          {isSkipped ? "skipped" : isDone ? "done" : "thinking…"}
        </span>
      </div>
      <ul style={{ margin: 0, paddingLeft: 18, display: "grid", gap: 4 }}>
        {steps.map((s, i) => (
          <li
            key={i}
            style={{
              fontSize: 13.5,
              color: s.status === "thinking" ? "var(--slate)" : "var(--ink)",
            }}
          >
            {s.detail}
          </li>
        ))}
      </ul>
    </div>
  );
}

const labelRow: CSSProperties = {
  textAlign: "center",
  fontSize: 12,
  color: "#94a3b8",
  textTransform: "uppercase",
  letterSpacing: 1,
};

const card: CSSProperties = {
  background: "var(--white)",
  border: "1px solid var(--line)",
  borderRadius: 12,
  boxShadow: "var(--shadow)",
  padding: "12px 16px",
  animation: "fade .3s",
};

function statusPill(status: "thinking" | "done" | "skipped"): CSSProperties {
  const map = {
    thinking: { color: "var(--indigo-2)", bg: "var(--indigo-soft)" },
    done: { color: "var(--teal)", bg: "var(--teal-soft)" },
    skipped: { color: "var(--slate)", bg: "#f1f5f9" },
  }[status];
  return {
    fontSize: 11,
    fontWeight: 700,
    color: map.color,
    background: map.bg,
    padding: "2px 8px",
    borderRadius: 12,
  };
}
