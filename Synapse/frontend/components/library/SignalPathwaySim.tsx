"use client";

// Pattern: signal-pathway-sim (neuron / reflex arc). Predict-observe + labelled exploration.
// Fire an impulse along the reflex arc; the active node lights up in order. Faithful pathway:
// receptor → sensory neuron → CNS (relay) → motor neuron → effector. Electrical along axons,
// chemical (neurotransmitter) across each synapse.

import { useEffect, useState } from "react";
import type { CSSProperties } from "react";

import { PatternCard, type LibraryComponentProps } from "./shared";

const DEFAULT = ["receptor", "sensory neuron", "CNS (relay)", "motor neuron", "effector"];

export default function SignalPathwaySim({ props, meta }: LibraryComponentProps) {
  const nodes = Array.isArray(props.pathway) && (props.pathway as unknown[]).length
    ? (props.pathway as unknown[]).map(String)
    : DEFAULT;
  const [active, setActive] = useState(-1);

  useEffect(() => {
    if (active < 0 || active >= nodes.length) return;
    const id = window.setTimeout(() => setActive((a) => (a + 1 <= nodes.length ? a + 1 : a)), 650);
    return () => window.clearTimeout(id);
  }, [active, nodes.length]);

  const running = active >= 0 && active < nodes.length;

  return (
    <PatternCard title="Reflex arc — impulse pathway" meta={meta}>
      <div style={{ display: "flex", alignItems: "center", gap: 4, flexWrap: "wrap", justifyContent: "center" }}>
        {nodes.map((n, i) => (
          <span key={n} style={{ display: "flex", alignItems: "center", gap: 4 }}>
            <span style={{ ...node, background: i <= active ? "var(--indigo)" : "var(--white)", color: i <= active ? "#fff" : "var(--slate)", borderColor: i <= active ? "var(--indigo)" : "var(--line)" }}>{n}</span>
            {i < nodes.length - 1 && <span style={{ color: i < active ? "var(--indigo)" : "var(--line)" }}>→</span>}
          </span>
        ))}
      </div>
      <button style={{ ...runBtn, opacity: running ? 0.5 : 1, cursor: running ? "default" : "pointer" }} disabled={running} onClick={() => setActive(0)}>
        Fire the impulse →
      </button>
      {active >= nodes.length && (
        <p style={{ marginTop: 10, fontSize: 14, color: "var(--teal)" }}>
          Response complete. The impulse travels electrically along each axon and crosses each synapse
          chemically (neurotransmitter). A reflex is fast because it does not wait for the brain.
        </p>
      )}
    </PatternCard>
  );
}

const node: CSSProperties = { padding: "8px 12px", borderRadius: 20, border: "1px solid var(--line)", fontSize: 12.5, fontWeight: 600, transition: "all .2s" };
const runBtn: CSSProperties = { marginTop: 14, background: "var(--indigo)", color: "#fff", border: "none", padding: "10px 18px", borderRadius: 10, fontSize: 14, fontWeight: 700, fontFamily: "inherit" };
