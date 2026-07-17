import { describe, expect, test } from "bun:test";
import { SimSpec, SIM_DOCS, initialState, resolveOutcome, validateSim } from "../sim";

/** A minimal but real osmosis sim, of the shape the model is asked to write. */
const osmosis = SimSpec.parse({
  title: "Osmosis",
  width: 200,
  height: 100,
  params: [
    { id: "cLeft", label: "Left solute", min: 0, max: 2, value: 0, unit: " M" },
    { id: "cRight", label: "Right solute", min: 0, max: 2, value: 1.5, unit: " M" },
  ],
  state: { shift: 0 },
  derived: { gradient: "cRight - cLeft" },
  step: { shift: "shift + gradient * dt * 4" },
  scene: [
    { shape: "rect", x: "0", y: "0", w: "100 + shift", h: "100", fill: "bio", opacity: "0.3" },
    { repeat: { count: 8, as: "i" }, shape: "circle", cx: "110 + i*10", cy: "20 + i*8", r: "2", fill: "bio" },
  ],
  readouts: [{ label: "Gradient", formula: "gradient", unit: " M" }],
  predict: {
    prompt: "Which way will water move?",
    options: [
      { label: "Left", when: "cLeft > cRight", explain: "Toward the left's higher solute." },
      { label: "Right", when: "cRight > cLeft", explain: "Toward the right's higher solute." },
      { label: "Neither", when: "abs(cRight - cLeft) < 0.02", explain: "No gradient, no net flow." },
    ],
  },
});

describe("validateSim", () => {
  test("accepts a well-formed generated experiment", () => {
    expect(validateSim(osmosis)).toEqual({ ok: true, errors: [] });
  });

  // The whole reason formulas are probed at generation time: a typo should cost
  // one repair round-trip, not render a blank lab in front of a judge.
  test("catches a formula referencing a variable that does not exist", () => {
    const bad = SimSpec.parse({ ...osmosis, step: { shift: "shift + cMiddle * dt" } });
    const r = validateSim(bad);
    expect(r.ok).toBe(false);
    expect(r.errors.some((e) => e.includes("cMiddle"))).toBe(true);
  });

  test("catches a syntax error in a scene formula", () => {
    const bad = SimSpec.parse({
      ...osmosis,
      scene: [{ shape: "rect", x: "0", y: "0", w: "100 +", h: "100", fill: "bio" }],
    });
    expect(validateSim(bad).ok).toBe(false);
  });

  test("catches a step that updates a variable not in state", () => {
    const bad = SimSpec.parse({ ...osmosis, step: { velocity: "1 + dt" } });
    const r = validateSim(bad);
    expect(r.ok).toBe(false);
    expect(r.errors.some((e) => e.includes("not in state"))).toBe(true);
  });

  test("catches a duplicate id between a param and state", () => {
    const bad = SimSpec.parse({ ...osmosis, state: { cLeft: 0 } });
    expect(validateSim(bad).errors.some((e) => e.includes("duplicate"))).toBe(true);
  });

  test("catches a param whose starting value is out of its own range", () => {
    const bad = SimSpec.parse({
      ...osmosis,
      params: [{ id: "cLeft", label: "x", min: 0, max: 1, value: 5 }],
      derived: {},
      step: {},
      predict: null,
      readouts: [],
      scene: [{ shape: "rect", x: "0", y: "0", w: "cLeft", h: "10", fill: "bio" }],
    });
    expect(validateSim(bad).errors.some((e) => e.includes("outside"))).toBe(true);
  });

  test("a repeat's index variable is in scope for that node only", () => {
    const ok = SimSpec.parse({
      ...osmosis,
      scene: [{ repeat: { count: 5, as: "k" }, shape: "circle", cx: "k * 10", cy: "50", r: "2", fill: "bio" }],
    });
    expect(validateSim(ok).ok).toBe(true);

    const leaked = SimSpec.parse({
      ...osmosis,
      scene: [
        { repeat: { count: 5, as: "k" }, shape: "circle", cx: "k * 10", cy: "50", r: "2", fill: "bio" },
        { shape: "circle", cx: "k * 2", cy: "50", r: "2", fill: "bio" },
      ],
    });
    expect(validateSim(leaked).ok).toBe(false);
  });

  test("derived may reference earlier derived but not later ones", () => {
    // readouts cleared too: the base spec reads `gradient`, which these
    // overrides remove. (The validator caught that on the first run — which is
    // the point of probing every formula.)
    const forward = SimSpec.parse({
      ...osmosis,
      derived: { a: "cLeft * 2", b: "a + 1" },
      step: { shift: "shift + b * dt" },
      readouts: [],
    });
    expect(validateSim(forward)).toEqual({ ok: true, errors: [] });

    const backward = SimSpec.parse({
      ...osmosis,
      derived: { b: "a + 1", a: "cLeft * 2" },
      step: { shift: "shift + dt" },
      readouts: [],
    });
    expect(validateSim(backward).ok).toBe(false);
  });
});

// Caught in the wild on the first live run: the model wrote when:"true" for the
// right answer and when:"false" for the others — asserting the outcome instead
// of deriving it. These are the teeth that make that a repair, not a demo.
describe("validateSim — a `when` may not assert the answer", () => {
  const withWhen = (whens: string[]) =>
    SimSpec.parse({
      ...osmosis,
      predict: {
        prompt: "?",
        options: whens.map((w, i) => ({ label: `opt${i}`, when: w, explain: "" })),
      },
    });

  for (const constant of ["true", "false", "1", "0", "2 > 1", "abs(-1)"]) {
    test(`rejects when:"${constant}"`, () => {
      const r = validateSim(withWhen([constant, "cRight > cLeft"]));
      expect(r.ok).toBe(false);
      expect(r.errors.some((e) => e.includes("asserted") || e.includes("unknown name"))).toBe(true);
    });
  }

  test("accepts a condition that reads the student's values", () => {
    expect(validateSim(withWhen(["cLeft > cRight", "cRight > cLeft"])).ok).toBe(true);
  });

  test("accepts a condition built from a derived value", () => {
    expect(validateSim(withWhen(["gradient > 0", "gradient <= 0"])).ok).toBe(true);
  });

  test("a function name alone does not make a constant look physical", () => {
    // `abs` is a function, not one of the experiment's variables.
    expect(validateSim(withWhen(["abs(1) > 0", "cLeft > 0"])).ok).toBe(false);
  });
});

describe("initialState", () => {
  test("resolves formulas against the params, in order", () => {
    const spec = SimSpec.parse({
      ...osmosis,
      params: [{ id: "amp", label: "Amplitude", min: 0, max: 1, value: 0.4 }],
      state: { theta: "amp", omega: "0", peak: "theta * 2" },
      derived: {},
      step: { theta: "theta + omega * dt", omega: "omega - theta * dt", peak: "peak" },
      readouts: [],
      predict: null,
      scene: [{ shape: "circle", cx: "50 + theta * 10", cy: "50", r: "3", fill: "phys" }],
    });
    expect(validateSim(spec)).toEqual({ ok: true, errors: [] });
    expect(initialState(spec, { amp: 0.4 })).toEqual({ theta: 0.4, omega: 0, peak: 0.8 });
  });

  test("tracks the student's slider rather than freezing at the default", () => {
    const spec = SimSpec.parse({
      ...osmosis,
      params: [{ id: "amp", label: "A", min: 0, max: 1, value: 0.4 }],
      state: { theta: "amp" },
      derived: {},
      step: { theta: "theta" },
      readouts: [],
      predict: null,
      scene: [{ shape: "circle", cx: "theta", cy: "1", r: "1", fill: "phys" }],
    });
    expect(initialState(spec, { amp: 0.9 }).theta).toBe(0.9);
  });

  test("a number is accepted wherever a formula is expected", () => {
    // The model writing 0 rather than "0" cost a whole generation once.
    const spec = SimSpec.parse({
      ...osmosis,
      state: { shift: 0 },
      scene: [{ shape: "rect", x: 0, y: 0, w: 100, h: 100, fill: "bio" }],
    });
    expect(spec.state.shift).toBe("0");
    expect(validateSim(spec).ok).toBe(true);
  });
});

describe("SimSpec schema", () => {
  test("rejects a colour outside the design tokens", () => {
    const r = SimSpec.safeParse({
      ...osmosis,
      scene: [{ shape: "rect", x: "0", y: "0", w: "10", h: "10", fill: "#ff0000" }],
    });
    expect(r.success).toBe(false);
  });

  test("rejects an id that is not a valid identifier", () => {
    const r = SimSpec.safeParse({
      ...osmosis,
      params: [{ id: "c-left", label: "x", min: 0, max: 1, value: 0 }],
    });
    expect(r.success).toBe(false);
  });

  test("caps repeat count", () => {
    const r = SimSpec.safeParse({
      ...osmosis,
      scene: [{ repeat: { count: 5000, as: "i" }, shape: "circle", cx: "i", cy: "1", r: "1", fill: "bio" }],
    });
    expect(r.success).toBe(false);
  });

  test("requires at least one scene node", () => {
    expect(SimSpec.safeParse({ ...osmosis, scene: [] }).success).toBe(false);
  });
});

// The generalisation of the pin principle: the model writes the physics, the
// runtime decides the answer from the student's actual values.
describe("resolveOutcome — truth is computed, not asserted", () => {
  test("right when the right side has more solute", () => {
    expect(resolveOutcome(osmosis, { cLeft: 0, cRight: 1.5 })).toBe(1);
  });

  test("left when the left side has more solute", () => {
    expect(resolveOutcome(osmosis, { cLeft: 1.5, cRight: 0 })).toBe(0);
  });

  test("neither when they are equal", () => {
    expect(resolveOutcome(osmosis, { cLeft: 1, cRight: 1 })).toBe(2);
  });

  test("the outcome tracks the student's values, not the model's default", () => {
    // Same spec, opposite sliders: the answer flips. A model that hardcoded
    // "right" would be wrong here, and cannot be, because it never said "right".
    const a = resolveOutcome(osmosis, { cLeft: 0, cRight: 2 });
    const b = resolveOutcome(osmosis, { cLeft: 2, cRight: 0 });
    expect(a).not.toBe(b);
  });

  test("returns null when no condition holds", () => {
    const narrow = SimSpec.parse({
      ...osmosis,
      predict: {
        prompt: "?",
        options: [
          { label: "A", when: "cLeft > 100", explain: "" },
          { label: "B", when: "cRight > 100", explain: "" },
        ],
      },
    });
    expect(resolveOutcome(narrow, { cLeft: 0, cRight: 0 })).toBeNull();
  });
});

describe("SIM_DOCS", () => {
  test("documents the shapes, the gate, and the derived-truth rule", () => {
    for (const s of ["rect", "circle", "line", "arrow", "repeat", "predict", "when"]) {
      expect(SIM_DOCS).toContain(s);
    }
    expect(SIM_DOCS).toContain("never asserted");
  });
});

describe("lenient input shapes", () => {
  // Each of these cost a repair round-trip in a live run before being coerced.
  test('dash accepts the string "true"', () => {
    const spec = SimSpec.parse({
      ...osmosis,
      scene: [{ shape: "line", x1: "0", y1: "0", x2: "10", y2: "10", stroke: "muted", dash: "true" }],
    });
    expect(spec.scene[0].dash).toBe(true);
    expect(validateSim(spec).ok).toBe(true);
  });

  test("dash still accepts a real boolean", () => {
    const spec = SimSpec.parse({
      ...osmosis,
      scene: [{ shape: "line", x1: "0", y1: "0", x2: "10", y2: "10", stroke: "muted", dash: false }],
    });
    expect(spec.scene[0].dash).toBe(false);
  });

  test("a numeric readout formula is normalised to a string", () => {
    const spec = SimSpec.parse({ ...osmosis, readouts: [{ label: "Constant", formula: 9.81 }] });
    expect(spec.readouts[0].formula).toBe("9.81");
  });
});
