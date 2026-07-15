import { describe, expect, test } from "bun:test";
import { describeComponent, describeGenerated, describeSpec } from "../describe";
import type { UISpec } from "../uispec";

const pendulum: UISpec = {
  title: "Pendulum Lab",
  root: {
    type: "column",
    children: [
      { type: "text", text: "A pendulum swings." },
      {
        type: "sim",
        spec: {
          title: "Simple Pendulum",
          params: [
            { id: "length", label: "String length L", min: 0.2, max: 2, value: 1, unit: " m" },
            { id: "mass", label: "Bob mass", min: 0.05, max: 2, value: 1, unit: " kg" },
          ],
          state: { theta: "rad(15)", omega: "0" },
          step: {
            omega: "omega - (g/length) * sin(theta) * dt",
            theta: "theta + omega * dt",
          },
          scene: [{ shape: "circle", cx: "50", cy: "50", r: "4", fill: "phys" }],
          predict: {
            prompt: "Double the mass. What happens to the period?",
            options: [
              { label: "Increases", when: "mass > 99999", explain: "..." },
              { label: "Stays the same", when: "mass >= 0.05", explain: "Mass cancels." },
            ],
          },
        },
      },
    ],
  },
};

// The Guide runs as its own call and cannot see the lab. Everything it needs to
// avoid asking "what did you change?" has to be in here.
describe("describeSpec", () => {
  const text = describeSpec(pendulum);

  test("names the screen and the sim", () => {
    expect(text).toContain("Pendulum Lab");
    expect(text).toContain("Simple Pendulum");
  });

  test("lists the controls the student can actually drag, with ranges", () => {
    expect(text).toContain("length");
    expect(text).toContain("String length L");
    expect(text).toContain("0.2 to 2");
    expect(text).toContain("Bob mass");
  });

  test("hands over the physics the sim is really running", () => {
    expect(text).toContain("omega - (g/length) * sin(theta) * dt");
    expect(text).toContain("theta + omega * dt");
  });

  test("includes the prediction and each option's condition", () => {
    expect(text).toContain("Double the mass");
    expect(text).toContain("Stays the same");
    expect(text).toContain("mass >= 0.05");
  });

  test("survives a screen with no sim", () => {
    const bare: UISpec = { title: "Just words", root: { type: "column", children: [] } };
    expect(describeSpec(bare)).toContain("Just words");
  });

  test("survives a malformed sim rather than throwing", () => {
    const broken: UISpec = {
      title: "Broken",
      root: { type: "column", children: [{ type: "sim", spec: { nonsense: true } }] },
    };
    expect(() => describeSpec(broken)).not.toThrow();
  });

  test("finds a sim nested inside cards and rows", () => {
    const nested: UISpec = {
      title: "Nested",
      root: {
        type: "column",
        children: [
          {
            type: "card",
            children: [{ type: "row", children: [pendulum.root.children![1]] }],
          },
        ],
      },
    };
    expect(describeSpec(nested)).toContain("Simple Pendulum");
  });
});

describe("describeComponent", () => {
  test("describes a pre-built sim and the values it was given", () => {
    const text = describeComponent("concentration-gradient-sandbox", {
      left_concentration: 0,
      right_concentration: 1.5,
      solute: "sucrose",
    });
    expect(text).toContain("Concentration gradient sandbox");
    expect(text).toContain("right_concentration = 1.5");
    expect(text).toContain("solute");
  });

  test("does not leak the predict prompt into the setup line", () => {
    const text = describeComponent("motion-sandbox", {
      mass_kg: 2,
      predict_prompt: "What happens to the trolley?",
    });
    expect(text).toContain("mass_kg = 2");
    expect(text).not.toContain("What happens to the trolley?");
  });

  test("degrades on an unknown pattern rather than throwing", () => {
    expect(describeComponent("does-not-exist", {})).toContain("unknown");
  });
});

describe("describeGenerated", () => {
  const html = `<!DOCTYPE html><html><head><title>Fibre Optic Lab</title></head><body>
    <h1>Total Internal Reflection</h1><h2>Try it</h2>
    <label>Angle of incidence</label><label>Core index</label>
    <script>reportEvent("x",{})</script></body></html>`;

  test("pulls out the title, sections and controls", () => {
    const text = describeGenerated(html);
    expect(text).toContain("Fibre Optic Lab");
    expect(text).toContain("Total Internal Reflection");
    expect(text).toContain("Angle of incidence");
  });

  test("says plainly that the current state is not visible", () => {
    expect(describeGenerated(html)).toContain("cannot see its current state");
  });

  test("survives an empty document", () => {
    expect(() => describeGenerated("")).not.toThrow();
  });
});
