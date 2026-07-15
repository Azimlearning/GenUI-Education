/**
 * Describe what's on the student's screen, for the Guide.
 *
 * The Guide runs as its own call and never sees the lab — only the interaction
 * event. That is fine for a pre-built sim, whose name says what it is, but
 * useless for one the model designed thirty seconds ago: the Guide gets
 * `{length: 1, mass: 2}` with no idea that `length` is a pendulum string, that
 * the period is meant to be mass-independent, or that the student was asked to
 * predict at all.
 *
 * So hand it the design. Including the step formulas, because the Guide should
 * be able to explain the physics the lab is actually running, not the physics it
 * assumes the lab is running.
 */

import { SimSpec } from "./sim";
import { BY_ID } from "./science/catalog";
import type { UISpec, UINode } from "./uispec";

/** A generated Tier B screen: every sim on it, in the model's own terms. */
export function describeSpec(spec: UISpec): string {
  const sims: string[] = [];

  const walk = (node: UINode): void => {
    if (!node || typeof node !== "object") return;

    if (node.type === "sim") {
      const parsed = SimSpec.safeParse(node.spec);
      if (parsed.success) sims.push(describeSim(parsed.data));
    }

    if (node.type === "science" && typeof node.pattern === "string") {
      const component = BY_ID.get(node.pattern);
      if (component) sims.push(`A pre-built "${component.title}": ${component.summary}`);
    }

    if (Array.isArray(node.children)) node.children.forEach(walk);
  };
  walk(spec.root);

  const head = `The student is looking at a screen titled "${spec.title ?? "untitled"}".`;
  return sims.length ? `${head}\n\n${sims.join("\n\n")}` : head;
}

function describeSim(sim: SimSpec): string {
  const lines: string[] = [
    `It contains an interactive simulation you designed for this question, called "${sim.title}".`,
  ];

  if (sim.params.length) {
    lines.push(
      `The student can drag: ${sim.params
        .map((p) => `${p.id} ("${p.label}", ${p.min} to ${p.max}${p.unit ?? ""})`)
        .join("; ")}.`,
    );
  }

  const step = Object.entries(sim.step);
  if (step.length) {
    lines.push(
      `It steps forward on these formulas, which ARE the physics it runs — refer to them rather than assuming:\n${step
        .map(([k, v]) => `  ${k} = ${v}`)
        .join("\n")}`,
    );
  }

  if (sim.predict) {
    lines.push(
      `Before running it they had to predict: "${sim.predict.prompt}"\nThe options, and the condition under which each is actually true:\n${sim.predict.options
        .map((o) => `  "${o.label}" when ${o.when}`)
        .join("\n")}`,
    );
  }

  return lines.join("\n");
}

/** A Tier A component, specialised with the values it was given. */
export function describeComponent(pattern: string, slots: Record<string, unknown>): string {
  const component = BY_ID.get(pattern);
  if (!component) return `The student is using an unknown component ("${pattern}").`;

  const filled = Object.entries(slots)
    .filter(([k]) => !k.startsWith("predict_"))
    .map(([k, v]) => `${k} = ${JSON.stringify(v)}`)
    .join(", ");

  return [
    `The student is using the pre-built "${component.title}". ${component.summary}`,
    `It is set up with: ${filled}.`,
    `They can change: ${component.manipulables.join(", ")}.`,
  ].join("\n");
}

/** A Tier C lab. We know it exists and roughly how big; the model wrote the rest. */
export function describeGenerated(html: string): string {
  const title = html.match(/<title[^>]*>([^<]{2,80})<\/title>/i)?.[1];
  const headings = [...html.matchAll(/<h[12][^>]*>([^<]{2,60})<\/h[12]>/gi)]
    .map((m) => m[1].trim())
    .slice(0, 4);
  const labels = [...html.matchAll(/<label[^>]*>([^<]{2,40})</gi)]
    .map((m) => m[1].trim())
    .slice(0, 6);

  return [
    `The student is using a full interactive lab you wrote from scratch${title ? `, titled "${title}"` : ""}.`,
    headings.length ? `Its sections: ${headings.join("; ")}.` : "",
    labels.length ? `Its controls: ${labels.join("; ")}.` : "",
    `You cannot see its current state — rely on the values reported with the interaction.`,
  ]
    .filter(Boolean)
    .join("\n");
}
