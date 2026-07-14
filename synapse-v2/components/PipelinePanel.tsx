"use client";

/**
 * The visible pipeline.
 *
 * This is the oversight mechanism, not decoration: the chosen tier, the filled
 * science-critical slot values, and any flagged contradiction are all on screen.
 * A wrong fill is meant to be catchable here by a teacher who knows the science,
 * which is the thing an opaque chatbot answer structurally cannot offer.
 */

import { PIPELINE_STEPS, STEP_BLURBS, STEP_LABELS, type PipelineStepEvent } from "@/lib/contract";

export default function PipelinePanel({ steps }: { steps: PipelineStepEvent[] }) {
  if (steps.length === 0) return null;

  // Last event per step wins; the rail shows the steps that have been reached.
  const latest = new Map<string, PipelineStepEvent>();
  const evidence = new Map<string, string[]>();
  for (const step of steps) {
    latest.set(step.step, step);
    if (step.evidence.length) {
      evidence.set(step.step, [...(evidence.get(step.step) ?? []), ...step.evidence]);
    }
  }

  const reached = PIPELINE_STEPS.filter((name) => latest.has(name));

  return (
    <aside className="pipeline" aria-label="Pipeline reasoning">
      <header className="pipeline-head">
        <h2>Pipeline</h2>
        <p>What the AI is doing, and why</p>
      </header>

      <ol className="rail">
        {reached.map((name, i) => {
          const step = latest.get(name)!;
          const facts = evidence.get(name) ?? [];
          return (
            <li key={name} className={`rail-step is-${step.status}`}>
              <span className="rail-marker">
                {step.status === "thinking" ? <span className="pulse" /> : i + 1}
              </span>
              <div className="rail-body">
                <span className="rail-name">
                  {STEP_LABELS[name]}
                  {step.status === "failed" ? <em className="rail-failed">failed</em> : null}
                </span>
                <span className="rail-detail">{step.detail || STEP_BLURBS[name]}</span>
                {facts.length ? (
                  <ul className="rail-evidence">
                    {facts.map((fact, j) => (
                      <li key={j}>
                        <code>{fact}</code>
                      </li>
                    ))}
                  </ul>
                ) : null}
              </div>
            </li>
          );
        })}
      </ol>
    </aside>
  );
}
