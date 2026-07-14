import { describe, expect, test } from "bun:test";
import { UISpecSchema, inspectSpec, tierBSystemPrompt } from "../uispec";
import type { UINode } from "../uispec";

const column = (children: UINode[]): UINode => ({ type: "column", children });

describe("UISpecSchema", () => {
  test("accepts a column root", () => {
    expect(UISpecSchema.safeParse({ title: "x", root: column([]) }).success).toBe(true);
  });

  test("rejects a non-column root", () => {
    expect(UISpecSchema.safeParse({ root: { type: "card" } }).success).toBe(false);
  });

  test("rejects a missing root", () => {
    expect(UISpecSchema.safeParse({ title: "x" }).success).toBe(false);
  });
});

describe("inspectSpec", () => {
  test("collects input ids", () => {
    const report = inspectSpec({
      root: column([
        { type: "slider", id: "mass", label: "Mass", min: 0, max: 10, value: 1 },
        { type: "input", id: "name", label: "Name" },
      ]),
    });
    expect(report.ok).toBe(true);
    expect(report.inputIds).toEqual(["mass", "name"]);
  });

  test("catches duplicate input ids", () => {
    // Two nodes sharing an id means one silently shadows the other's value,
    // and any formula referencing it reads the wrong number.
    const report = inspectSpec({
      root: column([
        { type: "slider", id: "v", label: "A", min: 0, max: 1, value: 0 },
        { type: "slider", id: "v", label: "B", min: 0, max: 1, value: 0 },
      ]),
    });
    expect(report.ok).toBe(false);
    expect(report.errors.some((e) => e.includes("duplicate"))).toBe(true);
  });

  test("enforces the depth cap", () => {
    let node: UINode = { type: "text", text: "deep" };
    for (let i = 0; i < 10; i++) node = column([node]);
    expect(inspectSpec({ root: node }).ok).toBe(false);
  });

  test("enforces the node cap", () => {
    const many = Array.from({ length: 100 }, (_, i) => ({ type: "text", text: `${i}` }));
    expect(inspectSpec({ root: column(many) }).ok).toBe(false);
  });

  test("accepts a science node naming a real component", () => {
    const report = inspectSpec({
      root: column([{ type: "science", pattern: "motion-sandbox", slots: {} }]),
    });
    expect(report.ok).toBe(true);
  });

  test("rejects a science node naming a component that does not exist", () => {
    const report = inspectSpec({
      root: column([{ type: "science", pattern: "warp-drive-sandbox", slots: {} }]),
    });
    expect(report.ok).toBe(false);
    expect(report.errors.some((e) => e.includes("warp-drive"))).toBe(true);
  });

  test("survives a malformed child without throwing", () => {
    const report = inspectSpec({
      root: column([null as unknown as UINode, { type: "text", text: "ok" }]),
    });
    expect(report.errors.length).toBeGreaterThan(0);
  });
});

describe("tierBSystemPrompt", () => {
  test("documents the vocabulary, the formulas and the real catalog", () => {
    const prompt = tierBSystemPrompt();
    for (const node of ["column", "callout", "computed", "formulaChart", "science", "barChart"]) {
      expect(prompt).toContain(`"${node}"`);
    }
    expect(prompt).toContain("motion-sandbox");
    expect(prompt).toContain("g = 9.81");
  });
});
