/**
 * The Tier B contract: UI-as-data.
 *
 * The model composes a novel screen as a JSON tree from a bounded vocabulary.
 * Extends the vocabulary proven in ../GenUITestV2/lib/uispec.ts with the two
 * things this app needs:
 *
 *   1. "science" nodes — a Tier A component embedded inside a generated screen,
 *      so a composed explanation can sit next to a faithful sim.
 *   2. "computed" / "formulaChart" nodes — model-written formulas evaluated by
 *      lib/expr.ts. Generated *behaviour*, without generated *code*.
 */

import { z } from "zod";
import { EXPR_DOCS, evaluate } from "./expr";
import { SIM_DOCS, SimSpec, validateSim } from "./sim";
import { CATALOG, catalogForPrompt } from "./science/catalog";

export interface UINode {
  type: string;
  children?: UINode[];
  [key: string]: unknown;
}

export interface UISpec {
  title?: string;
  root: UINode;
}

const MAX_NODES = 80;
const MAX_DEPTH = 6;

/**
 * The schema is deliberately loose on node internals (the vocabulary is
 * documented to the model in prose, which it follows well) and strict on the
 * things that actually break the renderer: shape, depth, size.
 */
export const UISpecSchema = z.object({
  title: z.string().optional(),
  root: z.custom<UINode>(
    (v) =>
      typeof v === "object" && v !== null && (v as UINode).type === "column",
    { message: "root must be a node of type 'column'" },
  ),
});

/** Walk the tree, enforcing caps and collecting the input ids. */
export function inspectSpec(spec: UISpec): {
  ok: boolean;
  errors: string[];
  inputIds: string[];
  nodeCount: number;
  simCount: number;
} {
  const errors: string[] = [];
  const inputIds: string[] = [];
  let nodeCount = 0;
  let simCount = 0;

  const walk = (node: UINode, depth: number): void => {
    if (!node || typeof node !== "object" || typeof node.type !== "string") {
      errors.push("encountered a node with no type");
      return;
    }
    nodeCount++;
    if (depth > MAX_DEPTH) {
      errors.push(`tree deeper than ${MAX_DEPTH} levels`);
      return;
    }
    if (nodeCount > MAX_NODES) {
      errors.push(`tree larger than ${MAX_NODES} nodes`);
      return;
    }

    if (typeof node.id === "string") {
      if (inputIds.includes(node.id)) errors.push(`duplicate input id "${node.id}"`);
      inputIds.push(node.id);
    }

    if (node.type === "science") {
      const pattern = typeof node.pattern === "string" ? node.pattern : "";
      if (!CATALOG.some((c) => c.id === pattern)) {
        errors.push(`science node names unknown component "${pattern}"`);
      }
    }

    // A generated experiment is checked here, before it can reach the screen:
    // shape, then every formula probed for syntax and unknown names. A typo
    // becomes one repair round-trip instead of a lab that renders blank.
    if (node.type === "sim") {
      simCount++;
      const parsed = SimSpec.safeParse(node.spec);
      if (!parsed.success) {
        for (const issue of parsed.error.issues) {
          errors.push(`sim.${issue.path.join(".") || "(root)"}: ${issue.message}`);
        }
      } else {
        const report = validateSim(parsed.data);
        for (const e of report.errors) errors.push(`sim "${parsed.data.title}" — ${e}`);
        // The sim shares its sliders with the screen, so they are valid names
        // for a sibling chart or computed readout.
        for (const p of parsed.data.params) inputIds.push(p.id);
      }
    }

    if (Array.isArray(node.children)) {
      for (const child of node.children) walk(child, depth + 1);
    }
  };

  walk(spec.root, 1);

  /**
   * Second pass: every model-written formula on the screen must resolve.
   *
   * It has to run after the walk, because a "computed" node may legitimately
   * reference a slider declared later in the tree, or a sim's param — sims
   * publish their sliders to the screen, so a chart beside the pendulum can
   * track its length. Probing catches the typo the first live run shipped:
   * a chart reading `length` when nothing had published it.
   */
  const known = new Set(inputIds);
  const probeFormulas = (node: UINode): void => {
    if (!node || typeof node !== "object") return;
    for (const key of ["formula"] as const) {
      const src = node[key];
      if (typeof src !== "string") continue;
      const scope: Record<string, number> = {};
      for (const id of known) scope[id] = 1;
      if (typeof node.variable === "string") scope[node.variable] = 1;
      const result = evaluate(src, scope);
      if (!result.ok) {
        errors.push(
          `${node.type} formula "${src}" — ${result.error}. Available: ${[...known].join(", ") || "no inputs declared"}`,
        );
      }
    }
    if (Array.isArray(node.children)) node.children.forEach(probeFormulas);
  };
  probeFormulas(spec.root);

  return { ok: errors.length === 0, errors, inputIds, nodeCount, simCount };
}

export const RENDER_UI_TOOL = {
  name: "render_ui",
  description:
    "Render the interactive screen as a declarative JSON tree from the documented vocabulary. This is the only way to respond.",
  schema: {
    type: "object" as const,
    properties: {
      title: { type: "string", description: "Short title for this screen" },
      root: {
        type: "object",
        description:
          "Root UINode. Must be {type:'column', children:[...]} using only the documented vocabulary.",
      },
    },
    required: ["root"],
  },
};

export function tierBSystemPrompt(): string {
  return `You are the Generator for Synapse, a science lab builder for Malaysian Form 4-5 KSSM SPM students (Physics, Chemistry, Biology). You never write prose answers. You DESIGN an interactive lab for the student's question and return it by calling the render_ui tool.

# Your job
**Design the experiment.** Not a page about the experiment — the experiment. The "sim" node (below)
lets you build one from scratch: state variables, formulas that step them, and shapes whose
positions are formulas. A beaker, a pendulum, a ray crossing a boundary, charges in a field, a
titration — all of it is shapes plus physics, and you write both.

Almost every screen you build should contain a sim. Text, callouts and tables are the framing
around the experiment, not a substitute for it. If you find yourself composing only cards and
stats, stop: the student asked to see something happen.

Every lab should let them predict, change something, and watch the consequence.

# Node vocabulary (the renderer knows ONLY these types)
Layout (may have "children"):
- {"type":"column","gap"?:number,"children":[...]}   vertical stack
- {"type":"row","gap"?:number,"children":[...]}      horizontal, wraps on small screens
- {"type":"card","title"?:string,"children":[...]}   bordered section
- {"type":"divider"}

Content:
- {"type":"heading","text":string,"level"?:1|2|3}
- {"type":"text","text":string,"muted"?:boolean}
- {"type":"callout","text":string,"tone":"info"|"success"|"warning"|"danger","title"?:string}
- {"type":"badge","text":string,"tone"?:"info"|"success"|"warning"|"danger"}
- {"type":"stat","label":string,"value":string,"delta"?:string,"tone"?:"success"|"danger"|"neutral"}
- {"type":"list","items":string[],"ordered"?:boolean}
- {"type":"table","columns":string[],"rows":string[][]}
- {"type":"progress","label":string,"value":number}   0-100
- {"type":"barChart","title"?:string,"items":[{"label":string,"value":number,"suffix"?:string}]}
- {"type":"equation","latex"?:string,"text":string,"caption"?:string}   a formula, shown prominently

Inputs ("id" must be unique across the whole tree):
- {"type":"slider","id":string,"label":string,"min":number,"max":number,"step"?:number,"value":number,"suffix"?:string}
- {"type":"input","id":string,"label":string,"placeholder"?:string,"value"?:string}
- {"type":"select","id":string,"label":string,"options":string[],"value"?:string}

Actions:
- {"type":"button","label":string,"action":string,"variant"?:"primary"|"secondary"}

Live computation (this is what makes your screens feel alive — USE IT):
- {"type":"computed","label":string,"formula":string,"suffix"?:string,"precision"?:number,"tone"?:"success"|"danger"|"neutral"}
    Recomputes on every slider/input change, with no round-trip to you.
- {"type":"formulaChart","title"?:string,"formula":string,"variable":string,"min":number,"max":number,"steps"?:number,"suffix"?:string}
    Plots "formula" as "variable" sweeps min..max. Other input ids resolve to their current values.

${EXPR_DOCS}

Formulas reference input ids directly. Example: a slider with id "mass" and one with
id "force" -> {"type":"computed","label":"Acceleration","formula":"force / mass","suffix":" m/s^2","precision":2}

${SIM_DOCS}

# The three pre-built sims
- {"type":"science","pattern":string,"slots":{...}}

${catalogForPrompt()}

These three exist because each targets a documented SPM misconception where the science is
guaranteed in code. Embed one ONLY when the question is squarely about that misconception. For
everything else, design the experiment yourself with a "sim" node — a fixed library can only answer
questions someone already anticipated, and this student asked their own.

# Interaction round-trip
Buttons carry an "action" string. When the student presses one you receive the action and ALL
current input values, and you generate the NEXT state of the screen. Use "computed" for anything
that should update instantly; use buttons for anything that needs your judgement (revealing an
answer, marking a prediction, going deeper).

# Hard rules
- Return ONLY the tool call. No prose, no markdown, no node types outside this list.
- Root must be a "column".
- Max ${MAX_DEPTH} levels deep, under ${MAX_NODES} nodes.
- Every number must be real and defensible for KSSM SPM. Never invent data.
- Formulas must be correct physics/chemistry. This is the part a student will trust most.
- Give the spec a short "title".`;
}
