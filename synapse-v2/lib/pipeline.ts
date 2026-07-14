/**
 * The visible pipeline.
 *
 *   [1] PLANNER   what experiment fits, and the lowest tier that can express it
 *   [2] CHECKER   is the student's premise sound? if not, say so plainly
 *   [3] BRIEF     describe what will be built -> "Generate Experiment"
 *        -- student confirms --
 *   [4] GENERATOR build it, at the planned tier, degrading if that fails
 *   [5] GUIDE     read the student's interactions and respond with insight
 *
 * Steps 1-3 are one call: they must feel instant, and they need the same
 * context. Steps 4-5 are separate calls on the strong model.
 */

import { z } from "zod";
import {
  type BriefEvent,
  type SynapseEvent,
  type Tier,
  type Turn,
  type InteractionEvent,
} from "./contract";
import { runStructured, runStreaming, type Message } from "./router";
import { CATALOG, catalogForPrompt, evidenceFor, fillSlots } from "./science/catalog";
import { RENDER_UI_TOOL, UISpecSchema, inspectSpec, tierBSystemPrompt } from "./uispec";
import { TIER_C_SYSTEM, extractHtml, validateGenerated } from "./sandbox";

type Emit = (event: SynapseEvent) => void;

/* ------------------------------------------------------------ fast pass */

const PlanOutput = z.object({
  title: z.string(),
  description: z.string(),
  manipulables: z.array(z.string()).default([]),
  tier: z.enum(["A", "B", "C"]),
  pattern: z.string().nullable().default(null),
  reason: z.string().default(""),
  contradiction: z
    .object({ student_claim: z.string(), correction: z.string() })
    .nullable()
    .default(null),
  explicit_generate_request: z.boolean().default(false),
});

const PLAN_TOOL = {
  name: "plan_experiment",
  description: "Plan the experiment, check the student's premise, and brief them on it.",
  schema: {
    type: "object" as const,
    properties: {
      title: { type: "string", description: "Short name for the experiment" },
      description: {
        type: "string",
        description:
          "2-3 sentences, addressed to the student, describing the experiment you will build and what they will see.",
      },
      manipulables: {
        type: "array",
        items: { type: "string" },
        description: "What the student will be able to change. Short noun phrases.",
      },
      tier: {
        type: "string",
        enum: ["A", "B", "C"],
        description: "Lowest tier that can faithfully express this experiment.",
      },
      pattern: {
        type: ["string", "null"],
        description: "For tier A: the component id. Otherwise null.",
      },
      reason: { type: "string", description: "One line: why this tier." },
      contradiction: {
        type: ["object", "null"],
        description:
          "Only if the student's own wording contradicts the real science. Otherwise null.",
        properties: {
          student_claim: { type: "string", description: "What they implied, quoted or paraphrased." },
          correction: {
            type: "string",
            description: "The contradiction, stated plainly and kindly, in 1-2 sentences.",
          },
        },
        required: ["student_claim", "correction"],
      },
      explicit_generate_request: {
        type: "boolean",
        description:
          "True only if the student explicitly asked to build/generate/make the experiment.",
      },
    },
    required: ["title", "description", "tier"],
  },
};

function planSystemPrompt(): string {
  return `You are the Planner, Checker and Brief for Synapse: a tool that turns a Malaysian Form 4-5 KSSM SPM science student's question into an interactive lab experiment (Physics, Chemistry, Biology).

You do three things in one pass, then call plan_experiment.

# 1. PLAN
Decide what experiment actually answers this student's question, and pick the LOWEST tier that can express it faithfully. Lower tiers are faster and more trustworthy.

Tier A — a pre-built science sim, specialised with the student's specifics. The machinery is
pre-built and correct; you only fill its slots. PREFER THIS whenever a component genuinely covers
the question. Available:

${catalogForPrompt()}

Tier B — no single sim fits, but the screen can be composed from layout, text, charts, controls and
live formulas (and may embed a Tier A sim inside it). Use for comparisons, multi-step reasoning,
calculators, relationships between variables, anything the catalog doesn't cover.

Tier C — the question needs a bespoke interactive that neither tier can express (a novel apparatus,
a custom animation, a game-like mechanic). Slowest and least predictable. Escalate only when B
genuinely cannot express it.

# 2. CHECK
Read the student's OWN WORDING for a claim that contradicts the real science. Malaysian SPM
students carry documented misconceptions, for example:
- "osmosis is water moving to where there is more water" (backwards: water moves toward higher SOLUTE)
- "heavier objects fall faster" (in vacuum, no)
- "current is used up as it goes round a series circuit" (current is conserved)
- "ionic bonds share electrons" (they transfer)
- "plants only respire at night" (they respire constantly)

If their wording contains such a claim, set "contradiction": quote what they implied, and state the
correction plainly. Do not soften it into vagueness, and do not silently build the correct thing as
if they had asked for it — they need to see the contradiction named before the experiment loads.
If their premise is sound, contradiction MUST be null. Do not invent one to seem useful.

# 3. BRIEF
Write "description" to the student, in plain language: what you are about to build, and what they
will be able to do with it. 2-3 sentences. No markdown.

Set explicit_generate_request only when they clearly asked you to build it ("generate the
experiment", "build me a sim", "show me the lab"). A plain question is not an explicit request.`;
}

export async function runFastPass(
  prompt: string,
  history: Turn[],
  emit: Emit,
): Promise<z.infer<typeof PlanOutput>> {
  emit({
    type: "pipeline_step",
    step: "planner",
    status: "thinking",
    detail: "Reading the question",
    evidence: [],
  });

  const messages: Message[] = [...history, { role: "user", content: prompt }];
  const plan = await runStructured({
    role: "fast",
    system: planSystemPrompt(),
    messages,
    tool: PLAN_TOOL,
    output: PlanOutput,
  });

  // A tier A plan naming a component that doesn't exist degrades to B rather
  // than failing: the planner's job is routing, not correctness.
  let tier: Tier = plan.tier;
  let pattern = plan.pattern;
  if (tier === "A" && (!pattern || !CATALOG.some((c) => c.id === pattern))) {
    tier = "B";
    pattern = null;
  }

  emit({
    type: "pipeline_step",
    step: "planner",
    status: "done",
    detail: plan.reason || `Chose tier ${tier}`,
    evidence: [`tier = ${tier}`, ...(pattern ? [`component = ${pattern}`] : [])],
  });

  emit({
    type: "pipeline_step",
    step: "checker",
    status: "done",
    detail: plan.contradiction
      ? "Found a contradiction in the premise"
      : "Premise is scientifically sound",
    evidence: plan.contradiction ? [plan.contradiction.correction] : [],
  });

  const brief: BriefEvent = {
    type: "brief",
    title: plan.title,
    description: plan.description,
    manipulables: plan.manipulables,
    tier,
    contradiction: plan.contradiction,
    requires_confirm: !plan.explicit_generate_request,
  };
  emit(brief);
  emit({
    type: "pipeline_step",
    step: "brief",
    status: "done",
    detail: brief.requires_confirm ? "Waiting for the student to confirm" : "Explicit request — building now",
    evidence: [],
  });

  return { ...plan, tier, pattern };
}

/* ------------------------------------------------------------ generator */

const SlotFillOutput = z.object({
  slots: z.record(z.string(), z.unknown()),
  note: z.string().default(""),
});

/** Tier A: fill the component's slots from the student's specifics. */
async function generateTierA(
  pattern: string,
  prompt: string,
  history: Turn[],
  emit: Emit,
  repairContext?: string,
): Promise<boolean> {
  const component = CATALOG.find((c) => c.id === pattern);
  if (!component) return false;

  const schema = z.toJSONSchema(component.slots, { io: "input" });
  const system = `You are the Generator for Synapse. Specialise a pre-built science sim to this student's question by filling its slots.

Component: ${component.id}
${component.summary}

Fill every slot from the student's specifics. If they named concentrations, elements, masses,
voltages or angles, use THEIR numbers. If they didn't, choose values that make the effect clearly
visible to a Form 4-5 student — a demonstration that barely moves teaches nothing.

Write "predict_prompt" as a real question the student must answer before they run it. If their
question contained a misconception, aim the prediction squarely at it, so their wrong answer fails
visibly when they run the sim.

Some slots are science-critical and will be overwritten by the system regardless of what you send.
That is deliberate. Fill the rest well.${repairContext ? `\n\nYour previous attempt failed validation: ${repairContext}\nFix it.` : ""}`;

  const filled = await runStructured({
    role: "fast",
    system,
    messages: [...history, { role: "user", content: prompt }],
    tool: {
      name: "fill_slots",
      description: `Fill the slots for ${component.id}.`,
      schema: {
        type: "object",
        properties: {
          slots: { ...(schema as Record<string, unknown>), description: "The slot values." },
          note: { type: "string", description: "One line on what you specialised and why." },
        },
        required: ["slots"],
      },
    },
    output: SlotFillOutput,
  });

  const result = fillSlots(pattern, filled.slots);
  if (!result.ok) {
    if (!repairContext) {
      emit({
        type: "pipeline_step",
        step: "generator",
        status: "thinking",
        detail: "Slot values failed validation — repairing",
        evidence: [result.errors],
      });
      return generateTierA(pattern, prompt, history, emit, result.errors);
    }
    return false;
  }

  emit({ type: "component", pattern, slots: result.slots });
  emit({
    type: "pipeline_step",
    step: "generator",
    status: "done",
    detail: filled.note || `Specialised ${component.title}`,
    // Science-critical values on screen, so a wrong fill is visible not silent.
    evidence: evidenceFor(result.component, result.slots),
  });
  return true;
}

/** Tier B: compose a novel screen as UI-as-data. */
async function generateTierB(
  prompt: string,
  history: Turn[],
  emit: Emit,
  repairContext?: string,
): Promise<boolean> {
  const spec = await runStructured({
    role: "strong",
    system:
      tierBSystemPrompt() +
      (repairContext ? `\n\n# Your previous attempt was rejected\n${repairContext}\nFix it.` : ""),
    messages: [...history, { role: "user", content: prompt }],
    tool: RENDER_UI_TOOL,
    output: UISpecSchema,
  });

  const report = inspectSpec(spec);
  if (!report.ok) {
    if (!repairContext) {
      emit({
        type: "pipeline_step",
        step: "generator",
        status: "thinking",
        detail: "Screen failed validation — repairing",
        evidence: report.errors,
      });
      return generateTierB(prompt, history, emit, report.errors.join("; "));
    }
    return false;
  }

  emit({ type: "ui_spec", spec });
  emit({
    type: "pipeline_step",
    step: "generator",
    status: "done",
    detail: `Composed a ${report.nodeCount}-node screen`,
    evidence: [`title = ${JSON.stringify(spec.title ?? "")}`],
  });
  return true;
}

/** Tier C: write a whole self-contained interactive, streamed as it comes. */
async function generateTierC(
  prompt: string,
  history: Turn[],
  emit: Emit,
): Promise<boolean> {
  let raw = "";
  for await (const chunk of runStreaming({
    role: "strong",
    system: TIER_C_SYSTEM,
    messages: [...history, { role: "user", content: prompt }],
  })) {
    raw += chunk;
    // Stream the partial into the provisional preview, so a 40s build reads as
    // "the AI is building your lab" rather than a hang.
    emit({ type: "generated_code", chunk, done: false });
  }

  const html = extractHtml(raw);
  const check = validateGenerated(html);
  if (!check.ok) {
    emit({
      type: "pipeline_step",
      step: "generator",
      status: "failed",
      detail: "Generated interactive failed its safety check",
      evidence: check.errors,
    });
    return false;
  }

  emit({ type: "generated_code", chunk: "", done: true });
  emit({
    type: "pipeline_step",
    step: "generator",
    status: "done",
    detail: `Wrote a bespoke interactive (${html.length.toLocaleString()} chars)`,
    evidence: ["sandboxed: no network, no same-origin, no host DOM"],
  });
  return true;
}

/**
 * Run the generator at the planned tier, degrading down the ladder on failure.
 *
 * C -> B -> A -> plain explanation. Every failure mode lands on something that
 * works: the demo never shows a dead end.
 */
export async function runGenerator(
  plan: { tier: Tier; pattern: string | null },
  prompt: string,
  history: Turn[],
  emit: Emit,
): Promise<{ tier: Tier | null; fellBackFrom: Tier | null }> {
  emit({
    type: "pipeline_step",
    step: "generator",
    status: "thinking",
    detail: `Building at tier ${plan.tier}`,
    evidence: [],
  });

  const ladder: Tier[] = plan.tier === "C" ? ["C", "B", "A"] : plan.tier === "B" ? ["B", "A"] : ["A"];

  for (const tier of ladder) {
    const isFallback = tier !== plan.tier;
    if (isFallback) {
      emit({
        type: "pipeline_step",
        step: "generator",
        status: "thinking",
        detail: `Tier ${plan.tier} did not land — falling back to tier ${tier}`,
        evidence: [],
      });
    }

    try {
      let ok = false;
      if (tier === "C") ok = await generateTierC(prompt, history, emit);
      else if (tier === "B") ok = await generateTierB(prompt, history, emit);
      else {
        // Falling back into A with no planned component: use the closest one.
        const pattern = plan.pattern ?? closestComponent(prompt);
        ok = await generateTierA(pattern, prompt, history, emit);
      }
      if (ok) return { tier, fellBackFrom: isFallback ? plan.tier : null };
    } catch (err) {
      emit({
        type: "pipeline_step",
        step: "generator",
        status: "failed",
        detail: `Tier ${tier} failed`,
        evidence: [err instanceof Error ? err.message : String(err)],
      });
    }
  }

  // Bottom of the ladder: say something true rather than nothing.
  emit({
    type: "guidance",
    text: "I couldn't build the interactive this time. Tell me which part of the concept you want to see and I'll try a simpler experiment.",
  });
  return { tier: null, fellBackFrom: plan.tier };
}

/** Crude keyword match — only ever used as the last rung of the fallback. */
function closestComponent(prompt: string): string {
  const p = prompt.toLowerCase();
  const hit = (words: string[]) => words.some((w) => p.includes(w));
  if (hit(["osmosis", "diffusion", "membrane", "concentration", "solute", "turgor", "cell"]))
    return "concentration-gradient-sandbox";
  if (hit(["bond", "ionic", "covalent", "electron", "molecule"])) return "bonding-explorer";
  if (hit(["circuit", "resistor", "ohm", "current", "voltage"])) return "circuit-sandbox";
  if (hit(["refract", "light", "snell", "lens", "ray", "internal reflection"]))
    return "refraction-sandbox";
  return "motion-sandbox";
}

/* ---------------------------------------------------------------- guide */

const GuideOutput = z.object({
  text: z.string(),
  regenerate: z.boolean().default(false),
});

/**
 * The Guide: what makes an interactive a lesson rather than a toy.
 *
 * Reads what the student actually did, and responds to THAT.
 */
export async function runGuide(
  interaction: InteractionEvent,
  prompt: string,
  history: Turn[],
  emit: Emit,
): Promise<void> {
  emit({
    type: "pipeline_step",
    step: "guide",
    status: "thinking",
    detail: `Reading: ${interaction.action}`,
    evidence: [],
  });

  const described = Object.entries(interaction.values)
    .map(([k, v]) => `${k} = ${v}`)
    .join(", ");

  const guide = await runStructured({
    role: "fast",
    system: `You are the Guide for Synapse. A Form 4-5 KSSM SPM student is working with an interactive experiment you built. They just did something. Respond to what they ACTUALLY did.

Rules:
- Interpret what their specific manipulation demonstrated. Name the values they used.
- If they made a prediction and it was wrong, say so directly and point at what the sim showed.
- Push them toward the NEXT prediction. End with a question they can test by changing something.
- 2-4 sentences. Plain language, no markdown, no lists. Talk like a good teacher standing next to them.
- Never praise a manipulation that showed nothing. Tell them what to change to see the effect.`,
    messages: [
      ...history,
      {
        role: "user",
        content: `Their original question: "${prompt}"\n\nWhat they just did: ${interaction.action}${described ? `\nCurrent values: ${described}` : ""}`,
      },
    ],
    tool: {
      name: "guide",
      description: "Respond to the student's interaction.",
      schema: {
        type: "object",
        properties: {
          text: { type: "string", description: "Your response to the student." },
          regenerate: {
            type: "boolean",
            description: "True only if the screen itself must change to answer them.",
          },
        },
        required: ["text"],
      },
    },
    output: GuideOutput,
  });

  emit({ type: "guidance", text: guide.text });
  emit({
    type: "pipeline_step",
    step: "guide",
    status: "done",
    detail: "Responded to the interaction",
    evidence: [],
  });
}
