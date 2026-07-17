/**
 * The generative sandbox: the model designs the experiment itself.
 *
 * This is the difference between a smart component picker and an AI that
 * actually builds your lab. There is no "osmosis component" here. There are
 * state variables, per-frame formulas, and shapes whose positions are
 * expressions — and from those the model composes a beaker, a pendulum, a ray
 * diagram, a reaction vessel, whatever the question needs.
 *
 * It stays safe because it is still UI-as-data: every formula runs through the
 * restricted evaluator in ./expr.ts, so this is generated *behaviour* without
 * generated *code*. No eval, no DOM, no network.
 *
 * The load-bearing idea is `predict.options[].when`. The model does not get to
 * say which answer is correct — it writes the physics as a formula, and the
 * runtime evaluates it against whatever the student actually set. A model that
 * writes the misconception into its own formula is visibly wrong in the
 * pipeline panel, and a model that writes it correctly cannot then contradict
 * itself. It generalises the pin principle to experiments nobody pre-built.
 */

import { z } from "zod";
import { evaluate, EXPR_DOCS } from "./expr";

/* Design tokens, not arbitrary colour. Generated labs look like the app. */
export const SIM_COLORS = [
  "accent",
  "bio",
  "chem",
  "phys",
  "success",
  "warning",
  "danger",
  "muted",
  "text",
  "surface",
  "line",
] as const;

const MAX_PARAMS = 8;
const MAX_STATE = 8;
const MAX_DERIVED = 14;
const MAX_SCENE = 60;
const MAX_REPEAT = 60;

/**
 * A formula. Accepts a bare number too, because every numeric field here is a
 * formula string and a model that writes `"x": 0` rather than `"x": "0"` is
 * being reasonable, not wrong. Normalising is cheaper than a repair round-trip
 * (the first live run lost a pendulum to exactly this).
 */
const Formula = z
  .union([z.number(), z.string()])
  .transform((v) => (typeof v === "number" ? String(v) : v));

/** Likewise for flags: `"true"` is a reasonable thing to write in a JSON tree of strings. */
const Flag = z
  .union([z.boolean(), z.literal("true"), z.literal("false")])
  .transform((v) => v === true || v === "true");

const Param = z.object({
  id: z.string().regex(/^[a-zA-Z_][a-zA-Z0-9_]*$/, "id must be a valid identifier"),
  label: z.string(),
  min: z.number(),
  max: z.number(),
  step: z.number().optional(),
  value: z.number(),
  unit: z.string().optional(),
});

const SceneNode = z.object({
  shape: z.enum(["rect", "circle", "line", "arrow", "text", "path"]),
  repeat: z
    .object({
      count: z.number().int().min(1).max(MAX_REPEAT),
      as: z.string().regex(/^[a-zA-Z_][a-zA-Z0-9_]*$/),
    })
    .optional(),
  // Numeric attributes are formulas (strings), evaluated every frame.
  x: Formula.optional(),
  y: Formula.optional(),
  w: Formula.optional(),
  h: Formula.optional(),
  rx: Formula.optional(),
  cx: Formula.optional(),
  cy: Formula.optional(),
  r: Formula.optional(),
  x1: Formula.optional(),
  y1: Formula.optional(),
  x2: Formula.optional(),
  y2: Formula.optional(),
  width: Formula.optional(),
  opacity: Formula.optional(),
  size: Formula.optional(),
  fill: z.enum(SIM_COLORS).optional(),
  stroke: z.enum(SIM_COLORS).optional(),
  dash: Flag.optional(),
  text: z.string().optional(),
  d: z.string().optional(),
  anchor: z.enum(["start", "middle", "end"]).optional(),
});

export type SceneNode = z.infer<typeof SceneNode>;

const PredictOption = z.object({
  label: z.string(),
  /** The physics. Truth is whichever option's `when` holds for the student's values. */
  when: Formula,
  explain: z.string(),
});

export const SimSpec = z.object({
  title: z.string(),
  width: z.number().min(40).max(400).default(200),
  height: z.number().min(40).max(300).default(100),
  params: z.array(Param).max(MAX_PARAMS).default([]),
  /** Evaluated once at reset, in order, against params. May be a formula. */
  state: z.record(z.string(), Formula).default({}),
  derived: z.record(z.string(), Formula).default({}),
  step: z.record(z.string(), Formula).default({}),
  duration: z.number().min(0.5).max(20).default(4),
  scene: z.array(SceneNode).min(1).max(MAX_SCENE),
  readouts: z
    .array(
      z.object({
        label: z.string(),
        formula: Formula,
        unit: z.string().optional(),
        precision: z.number().int().min(0).max(4).optional(),
      }),
    )
    .max(6)
    .default([]),
  predict: z
    .object({
      prompt: z.string(),
      options: z.array(PredictOption).min(2).max(4),
    })
    .nullable()
    .default(null),
  caption: z.string().optional(),
});

export type SimSpec = z.infer<typeof SimSpec>;

/** Attributes whose value is a formula rather than a literal. */
const FORMULA_KEYS = [
  "x", "y", "w", "h", "rx", "cx", "cy", "r",
  "x1", "y1", "x2", "y2", "width", "opacity", "size",
] as const;

/**
 * Check every formula parses and references only names that exist.
 *
 * Probing with a scope of ones catches unknown names and syntax errors at
 * generation time, so a typo becomes one repair round-trip instead of a lab
 * that renders blank in front of a judge. It cannot catch wrong physics — that
 * is what the pipeline panel and a teacher's eyes are for.
 */
export function validateSim(spec: SimSpec): { ok: boolean; errors: string[] } {
  const errors: string[] = [];

  // Names available to every formula. `t` and `dt` are supplied by the runtime.
  const names = new Set<string>(["t", "dt"]);

  for (const p of spec.params) {
    if (names.has(p.id)) errors.push(`duplicate id "${p.id}"`);
    names.add(p.id);
    if (p.min >= p.max) errors.push(`param "${p.id}": min must be below max`);
    if (p.value < p.min || p.value > p.max) {
      errors.push(`param "${p.id}": value ${p.value} is outside ${p.min}..${p.max}`);
    }
  }
  const probe = (source: string, where: string, scope: Set<string>) => {
    const values: Record<string, number> = {};
    for (const n of scope) values[n] = 1;
    const result = evaluate(source, values);
    if (!result.ok) errors.push(`${where}: ${result.error} — in "${source}"`);
  };

  // Initial state resolves once, in order, against params and earlier state —
  // so a pendulum can start at its own amplitude slider.
  const initScope = new Set(spec.params.map((p) => p.id));
  for (const [key, formula] of Object.entries(spec.state)) {
    if (names.has(key) || initScope.has(key)) errors.push(`duplicate id "${key}"`);
    probe(formula, `state.${key}`, initScope);
    initScope.add(key);
    names.add(key);
  }
  if (Object.keys(spec.state).length > MAX_STATE) errors.push("too many state variables");
  if (Object.keys(spec.derived).length > MAX_DERIVED) errors.push("too many derived values");

  // Derived resolve in insertion order, so each may use the ones before it.
  for (const [key, formula] of Object.entries(spec.derived)) {
    probe(formula, `derived.${key}`, names);
    if (names.has(key) && !(key in spec.state)) errors.push(`duplicate id "${key}"`);
    names.add(key);
  }

  for (const [key, formula] of Object.entries(spec.step)) {
    if (!(key in spec.state)) {
      errors.push(`step."${key}" updates a variable that is not in state`);
    }
    probe(formula, `step.${key}`, names);
  }

  spec.scene.forEach((node, i) => {
    const scope = new Set(names);
    if (node.repeat) scope.add(node.repeat.as);
    for (const key of FORMULA_KEYS) {
      const v = node[key];
      if (typeof v === "string") probe(v, `scene[${i}].${key}`, scope);
    }
    if (node.shape === "text" && !node.text) errors.push(`scene[${i}]: text shape needs "text"`);
    if (node.shape === "path" && !node.d) errors.push(`scene[${i}]: path shape needs "d"`);
  });

  spec.readouts.forEach((r, i) => probe(r.formula, `readouts[${i}]`, names));

  if (spec.predict) {
    // The variables the outcome is allowed to depend on. `t`/`dt` are excluded
    // deliberately: which answer is right cannot be a function of the clock.
    const physical = new Set([
      ...spec.params.map((p) => p.id),
      ...Object.keys(spec.state),
      ...Object.keys(spec.derived),
    ]);

    spec.predict.options.forEach((o, i) => {
      probe(o.when, `predict.options[${i}].when`, names);

      // The teeth behind "computed, never asserted". A condition that mentions
      // none of the experiment's variables is a constant — the model declaring
      // the winner rather than writing the physics. Seen in the wild on the
      // first live run: when:"true" for the right answer, when:"false" for the
      // rest. `true`/`false` happened to fail as unknown names; "1" and "0"
      // would not have, so check the substance rather than the spelling.
      if (!referencesAny(o.when, physical)) {
        errors.push(
          `predict.options[${i}].when is the constant "${o.when}" — it must be computed from the experiment's variables (${[...physical].join(", ") || "none declared"}), not asserted. Write the condition under which this option is actually true.`,
        );
      }
    });
  }

  return { ok: errors.length === 0, errors };
}

/**
 * Does this formula actually read any of these names?
 *
 * Matching identifiers against the variable set only — function names like
 * `abs` are never in it, so they can't make a constant look physical.
 */
function referencesAny(source: string, names: Set<string>): boolean {
  const ids = source.match(/[a-zA-Z_][a-zA-Z0-9_]*/g) ?? [];
  return ids.some((id) => names.has(id));
}

/**
 * Resolve the starting state. Formulas evaluate in order against the params, so
 * initial values can track the student's sliders rather than being frozen.
 */
export function initialState(
  spec: SimSpec,
  params: Record<string, number>,
): Record<string, number> {
  const scope: Record<string, number> = { ...params };
  const out: Record<string, number> = {};
  for (const [key, formula] of Object.entries(spec.state)) {
    const r = evaluate(formula, scope);
    out[key] = r.ok ? r.value : 0;
    scope[key] = out[key];
  }
  return out;
}

/**
 * Which prediction option is actually true, given the student's current values.
 * Returns the first whose `when` holds — so the model should write mutually
 * exclusive conditions, and ordering breaks any tie it failed to.
 */
export function resolveOutcome(
  spec: SimSpec,
  scope: Record<string, number>,
): number | null {
  if (!spec.predict) return null;
  for (let i = 0; i < spec.predict.options.length; i++) {
    const result = evaluate(spec.predict.options[i].when, scope);
    if (result.ok && result.value !== 0) return i;
  }
  return null;
}

/** Documented to the model in the Tier B system prompt. */
export const SIM_DOCS = `### The "sim" node — build the experiment yourself

This is how you create an interactive lab for a question no pre-built sim covers. You describe a
simulation as data: variables, formulas, and shapes whose positions are formulas. The runtime
animates it. Use this for anything a student should be able to run and watch.

{"type":"sim","spec":{ ... }}

The spec:
- "title": string
- "width"/"height": the drawing area's coordinate system (default 200 x 100). All scene numbers are
  in these units. Pick a shape that suits the experiment (a tall beaker might be 100 x 120).
- "params": student-adjustable sliders. [{"id","label","min","max","step"?,"value","unit"?}]
  Their ids become variables in every formula. Max ${MAX_PARAMS}.
- "state": {"name": startingNumber} — variables the simulation integrates over time. Max ${MAX_STATE}.
- "step": {"name": formula} — how each state variable changes each tick. "dt" (seconds since the
  last frame) and "t" (seconds since the run started) are in scope.
  e.g. {"v": "v + (force/mass) * dt", "x": "x + v * dt"}
- "derived": {"name": formula} — values computed fresh each frame from params and state, in the
  order written (later ones may use earlier ones). Use these to keep the scene readable. Max ${MAX_DERIVED}.
- "duration": seconds the run lasts (default 4).
- "scene": the shapes, drawn in order. Max ${MAX_SCENE}.
- "readouts": [{"label","formula","unit"?,"precision"?}] — live numbers beside the sim. Label units.
- "predict": the prediction gate (see below). Omit only for a purely exploratory sim.
- "caption": one line under the sim, e.g. what the dots represent.

A sim's "params" are shared with the rest of the screen: a "computed" or "formulaChart" node beside
the sim can reference a param id directly and it will track the student's slider live. Use that to
put a graph next to the apparatus.

Scene shapes. Every numeric attribute is a FORMULA STRING, so it can depend on state and params:
- {"shape":"rect","x","y","w","h","rx"?,"fill","opacity"?}
- {"shape":"circle","cx","cy","r","fill","opacity"?}
- {"shape":"line","x1","y1","x2","y2","stroke","width"?,"dash"?}
- {"shape":"arrow","x1","y1","x2","y2","stroke","width"?}     draws an arrowhead at (x2,y2)
- {"shape":"text","x","y","text","size"?,"fill"?,"anchor"?}   "text" is literal, not a formula
- {"shape":"path","d","stroke"?,"fill"?}                      "d" is a literal SVG path, static

Colours are design tokens, not hex: ${SIM_COLORS.join(", ")}. The lab then matches the app.

Repeat, for particles and fields — draw one shape many times with an index variable:
  {"repeat":{"count":12,"as":"i"},"shape":"circle","cx":"10 + i*15","cy":"50 + sin(t + i)*20","r":"2","fill":"bio"}

# The prediction gate — this is the pedagogy, not decoration
The student must commit before they see the answer. A misconception only breaks if you staked
something on it first.

"predict": {
  "prompt": "A real question, aimed at the misunderstanding you are targeting",
  "options": [
    {"label":"Water moves left","when":"cLeft > cRight","explain":"Why that happened, in 1-2 sentences."},
    {"label":"Water moves right","when":"cRight > cLeft","explain":"..."},
    {"label":"No net movement","when":"abs(cRight - cLeft) < 0.02","explain":"..."}
  ]
}

**"when" is the physics, and you do not get to shortcut it.** The runtime evaluates each "when"
against the student's ACTUAL slider values, and whichever holds first is the truth — so the outcome
is computed, never asserted. Write conditions that are mutually exclusive and that genuinely follow
from the science. The "explain" is shown for whatever actually happened, so write each one as if it
is the case.

You do not know which option is correct, because it depends on values the student has not chosen
yet. That is the point. **Every "when" MUST reference at least one param, state or derived
variable** — a condition that mentions none of them is rejected and you will be asked to write it
again. In particular:

  BAD:  {"label":"Longer period","when":"true"}        <- asserting the answer
  BAD:  {"label":"Shorter period","when":"false"}      <- asserting the answer
  BAD:  {"label":"No change","when":"1"}               <- same thing, spelled differently
  GOOD: {"label":"Longer period","when":"length > 1.0"}
  GOOD: {"label":"No change","when":"abs(massA - massB) > 0"}   <- period is mass-independent,
                                                                   so this is TRUE whenever the
                                                                   masses differ. That is physics.

If an option is correct regardless of the sliders — the pendulum's period does not depend on mass,
however the student sets it — express that as the condition under which the student would SEE it
(e.g. "when the masses differ"), not as "true".

${EXPR_DOCS}

# Rules for a sim that teaches
- Make the effect BIG. A demonstration that barely moves teaches nothing. Choose param ranges and
  starting values where the difference is obvious.
- The physics goes in the formulas, correctly. Integrate real equations of motion; do not fake an
  animation that always ends the same way.
- It must look right on the first frame, before anything is pressed.
- Label every readout with its unit. SPM marks units.
- One idea per sim.`;
