/**
 * The Tier A catalog: the short list of experiments we do NOT let the model
 * design.
 *
 * This used to be five components and the default path. It is now three, and
 * the exception. Everything else — circuits, refraction, reaction vessels,
 * anything a question asks for — is designed per question by the model as a
 * generative sim (see ../sim.ts), because a fixed library can only ever answer
 * the questions somebody anticipated.
 *
 * What survives here earns its place: each one targets a misconception that is
 * documented in the SPM cohort, where being right matters more than being
 * bespoke, and where a pin can guarantee it. Osmosis (water moves toward higher
 * solute), forces (moving is not the same as accelerating), bonding (transfer
 * vs share). If a component here does not have a pin, it should not be here.
 *
 * Two ideas do the work.
 *
 * 1. SLOTS. Each component declares a Zod schema of bounded, typed props. The
 *    model fills them from the student's specifics, so "show me diffusion" and
 *    "0.5 M NaCl vs 0.1 M across a partially permeable membrane at 37 C" hit the
 *    same component with different slot values. The specificity comes from the
 *    student; the interactive machinery is pre-built and correct.
 *
 * 2. PINS. Science-critical values are merged OVER whatever the model proposed.
 *    The model can choose the scenario; it cannot choose which way water moves.
 *    A wrong model answer structurally cannot ship a wrong sim. (v1 had this for
 *    one component out of fourteen. Here every component that has a science-
 *    critical invariant declares it.)
 */

import { z } from "zod";

export type Subject = "biology" | "chemistry" | "physics";

export interface ScienceComponent<S extends z.ZodType = z.ZodType> {
  /** Stable pattern id — the wire value the renderer resolves on. */
  id: string;
  title: string;
  subject: Subject;
  /** One line, shown to the model in the planner catalog. */
  summary: string;
  /** What the model may fill. */
  slots: S;
  /**
   * Science-critical values, merged over the model's fill. Keep this to things
   * that are true regardless of scenario — not defaults, invariants.
   */
  pins: Record<string, unknown>;
  /** Shown to the student in the brief: what they'll be able to change. */
  manipulables: string[];
  /** Slot keys whose values are echoed into the pipeline panel. */
  evidence_slots: string[];
}

/* ------------------------------------------------ concentration gradient */

const OsmosisSlots = z.object({
  scenario: z
    .enum(["beaker", "plant-cell", "animal-cell"])
    .default("beaker")
    .describe("Which vessel to show. plant-cell shows turgor/plasmolysis."),
  solute: z.string().default("sucrose").describe("The dissolved substance, e.g. 'NaCl'"),
  left_concentration: z.number().min(0).max(2).describe("Molarity, left compartment"),
  right_concentration: z.number().min(0).max(2).describe("Molarity, right compartment"),
  temperature_c: z.number().min(0).max(100).default(25),
  predict_prompt: z
    .string()
    .default("Which way will the water move, and why?")
    .describe("The question asked before the student may run the sim"),
});

const osmosis: ScienceComponent<typeof OsmosisSlots> = {
  id: "concentration-gradient-sandbox",
  title: "Concentration gradient sandbox",
  subject: "biology",
  summary:
    "Osmosis/diffusion across a selectively permeable membrane. Predict, run, then watch water move toward the higher solute concentration. Handles beaker, plant cell (turgor/plasmolysis) and animal cell (lysis/crenation).",
  slots: OsmosisSlots,
  pins: {
    // Water moves toward higher solute. This is the misconception the whole
    // component exists to break, so the model does not get a vote on it.
    particle: "water",
    membrane: "selectively-permeable",
    correct_direction: "toward-higher-solute",
  },
  manipulables: [
    "solute concentration on each side",
    "the vessel (beaker, plant cell, animal cell)",
    "temperature",
  ],
  evidence_slots: ["left_concentration", "right_concentration", "solute", "scenario"],
};

/* ------------------------------------------------------- forces & motion */

const MotionSlots = z.object({
  mass_kg: z.number().min(0.1).max(50).describe("Mass of the trolley"),
  applied_force_n: z.number().min(0).max(200).describe("Force applied, newtons"),
  friction_coefficient: z.number().min(0).max(1).default(0.1),
  incline_deg: z.number().min(0).max(45).default(0),
  show_graph: z.boolean().default(true).describe("Show the live velocity-time graph"),
  predict_prompt: z
    .string()
    .default("What happens to the trolley when the force is applied?"),
});

const motion: ScienceComponent<typeof MotionSlots> = {
  id: "motion-sandbox",
  title: "Forces and motion sandbox",
  subject: "physics",
  summary:
    "A trolley obeying Newton's second law with friction and optional incline. Real integration loop, live velocity-time graph plotted from the simulation state. Good for F=ma, friction, equilibrium, acceleration.",
  slots: MotionSlots,
  pins: {
    // The sim integrates real kinematics; the model cannot supply an outcome.
    law: "newton-second",
    gravity: 9.81,
  },
  manipulables: ["applied force", "mass", "friction", "incline angle"],
  evidence_slots: ["mass_kg", "applied_force_n", "friction_coefficient", "incline_deg"],
};

/* --------------------------------------------------------------- bonding */

const BondingSlots = z.object({
  pairs: z
    .array(
      z.object({
        a: z.string().describe("Element symbol, e.g. 'Na'"),
        b: z.string().describe("Element symbol, e.g. 'Cl'"),
      }),
    )
    .min(1)
    .max(6)
    .describe("Element pairs to contrast. Include both ionic and covalent examples."),
  show_electronegativity: z.boolean().default(true),
  predict_prompt: z.string().default("Will these atoms transfer electrons, or share them?"),
});

const bonding: ScienceComponent<typeof BondingSlots> = {
  id: "bonding-explorer",
  title: "Electron bonding explorer",
  subject: "chemistry",
  summary:
    "Contrasting cases for ionic vs covalent vs metallic bonding. Classifies each pair from real electronegativity differences (not a metal/non-metal lookup), animates transfer vs sharing, and places the pair on the electronegativity-difference scale.",
  slots: BondingSlots,
  pins: {
    // Bond type is computed from the electronegativity table in bonding.ts.
    classification: "electronegativity-difference",
  },
  manipulables: ["which element pair to inspect", "electron shell view"],
  evidence_slots: ["pairs"],
};

/* --------------------------------------------------------------- export */

export const CATALOG: ScienceComponent[] = [osmosis, motion, bonding];

export const BY_ID = new Map(CATALOG.map((c) => [c.id, c]));

/** The catalog as the planner sees it: id, what it's for, and its slot shape. */
export function catalogForPrompt(): string {
  return CATALOG.map((c) => {
    const shape = z.toJSONSchema(c.slots, { io: "input" });
    return [
      `## ${c.id}  (${c.subject})`,
      c.summary,
      `slots: ${JSON.stringify(shape)}`,
    ].join("\n");
  }).join("\n\n");
}

/**
 * Validate a model fill and stamp the pins over it.
 *
 * Order matters: parse first so the model's values are bounded, then pin, so a
 * pinned invariant cannot be argued out of by a validation-passing lie.
 */
export function fillSlots(
  id: string,
  proposed: unknown,
):
  | { ok: true; component: ScienceComponent; slots: Record<string, unknown> }
  | { ok: false; errors: string } {
  const component = BY_ID.get(id);
  if (!component) return { ok: false, errors: `Unknown component "${id}"` };

  const parsed = component.slots.safeParse(proposed);
  if (!parsed.success) {
    return {
      ok: false,
      errors: parsed.error.issues
        .map((i) => `${i.path.join(".") || "(root)"}: ${i.message}`)
        .join("; "),
    };
  }

  return {
    ok: true,
    component,
    slots: { ...(parsed.data as Record<string, unknown>), ...component.pins },
  };
}

/** Science-critical values, formatted for the pipeline panel. */
export function evidenceFor(
  component: ScienceComponent,
  slots: Record<string, unknown>,
): string[] {
  return component.evidence_slots
    .filter((k) => slots[k] !== undefined)
    .map((k) => `${k} = ${JSON.stringify(slots[k])}`);
}
