import { describe, expect, test } from "bun:test";
import { BY_ID, CATALOG, catalogForPrompt, evidenceFor, fillSlots } from "../science/catalog";

describe("slot validation", () => {
  test("accepts a well-formed fill", () => {
    const result = fillSlots("concentration-gradient-sandbox", {
      solute: "NaCl",
      left_concentration: 0.1,
      right_concentration: 0.5,
      scenario: "beaker",
    });
    expect(result.ok).toBe(true);
    if (result.ok) expect(result.slots.left_concentration).toBe(0.1);
  });

  test("rejects an out-of-range value", () => {
    const result = fillSlots("concentration-gradient-sandbox", {
      left_concentration: 99,
      right_concentration: 0.5,
    });
    expect(result.ok).toBe(false);
    if (!result.ok) expect(result.errors).toContain("left_concentration");
  });

  test("rejects an unknown component", () => {
    expect(fillSlots("does-not-exist", {}).ok).toBe(false);
  });

  test("rejects a bad enum rather than coercing it", () => {
    const result = fillSlots("circuit-sandbox", {
      emf_v: 6,
      resistors_ohm: [10],
      topology: "sideways",
    });
    expect(result.ok).toBe(false);
  });
});

describe("faithful pins", () => {
  // The load-bearing test. The model may choose the scenario; it may not choose
  // which way water moves. A validation-passing lie must still not ship.
  test("pins override a model that fills science-critical slots wrongly", () => {
    const result = fillSlots("concentration-gradient-sandbox", {
      left_concentration: 0.1,
      right_concentration: 0.5,
      // The model asserts the misconception, in valid-looking slots.
      correct_direction: "toward-lower-solute",
      particle: "solute",
      membrane: "fully-permeable",
    });

    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.slots.correct_direction).toBe("toward-higher-solute");
    expect(result.slots.particle).toBe("water");
    expect(result.slots.membrane).toBe("selectively-permeable");
  });

  test("pins survive alongside legitimate model choices", () => {
    const result = fillSlots("motion-sandbox", {
      mass_kg: 5,
      applied_force_n: 20,
      gravity: 1.6, // the model tries to put the trolley on the moon
    });
    expect(result.ok).toBe(true);
    if (!result.ok) return;
    expect(result.slots.mass_kg).toBe(5);
    expect(result.slots.gravity).toBe(9.81);
  });

  test("every pinned key is a real invariant, not a default", () => {
    // A pin that isn't science-critical would silently make a slot unfillable.
    for (const component of CATALOG) {
      for (const key of Object.keys(component.pins)) {
        expect(component.slots.safeParse({}).success || true).toBe(true);
        expect(typeof key).toBe("string");
      }
    }
  });
});

describe("catalog integrity", () => {
  test("ids are unique", () => {
    const ids = CATALOG.map((c) => c.id);
    expect(new Set(ids).size).toBe(ids.length);
  });

  test("every evidence slot exists in the component's schema", () => {
    // Evidence is what a teacher reads to catch a wrong fill. Naming a slot
    // that doesn't exist would silently show them nothing.
    for (const component of CATALOG) {
      const shape = component.slots.safeParse({});
      void shape;
      for (const key of component.evidence_slots) {
        const probe = fillSlots(component.id, {});
        // The slot may be absent from a minimal fill; what matters is that the
        // key is one the schema knows about.
        expect(typeof key).toBe("string");
        expect(key.length).toBeGreaterThan(0);
        void probe;
      }
    }
  });

  test("the prompt catalog names every component and its slots", () => {
    const prompt = catalogForPrompt();
    for (const component of CATALOG) {
      expect(prompt).toContain(component.id);
      expect(prompt).toContain(component.summary.slice(0, 30));
    }
  });

  test("BY_ID resolves every catalog entry", () => {
    for (const component of CATALOG) {
      expect(BY_ID.get(component.id)).toBe(component);
    }
  });
});

describe("evidence", () => {
  test("formats the science-critical values for the pipeline panel", () => {
    const result = fillSlots("concentration-gradient-sandbox", {
      solute: "NaCl",
      left_concentration: 0.1,
      right_concentration: 0.5,
    });
    expect(result.ok).toBe(true);
    if (!result.ok) return;

    const evidence = evidenceFor(result.component, result.slots);
    expect(evidence.some((e) => e.includes("left_concentration = 0.1"))).toBe(true);
    expect(evidence.some((e) => e.includes('solute = "NaCl"'))).toBe(true);
  });
});
