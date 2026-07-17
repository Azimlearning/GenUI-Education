import { describe, expect, test } from "bun:test";
import { evaluate } from "../expr";

const ok = (src: string, scope: Record<string, number> = {}) => {
  const result = evaluate(src, scope);
  if (!result.ok) throw new Error(`expected ok, got: ${result.error}`);
  return result.value;
};

describe("arithmetic", () => {
  test("respects precedence", () => {
    expect(ok("1 + 2 * 3")).toBe(7);
    expect(ok("(1 + 2) * 3")).toBe(9);
  });

  test("power is right associative", () => {
    expect(ok("2 ^ 3 ^ 2")).toBe(512);
  });

  test("handles unary minus and exponent notation", () => {
    expect(ok("-4 + 2")).toBe(-2);
    expect(ok("1.5e3")).toBe(1500);
  });
});

describe("science formulas", () => {
  test("resolves input ids from scope", () => {
    expect(ok("force / mass", { force: 18, mass: 2 })).toBe(9);
  });

  test("kinetic energy", () => {
    expect(ok("0.5 * m * v^2", { m: 4, v: 3 })).toBe(18);
  });

  test("Snell's law", () => {
    expect(ok("n1 * sin(rad(theta)) / n2", { n1: 1, n2: 1.33, theta: 30 })).toBeCloseTo(0.376, 3);
  });

  test("g resolves to the real constant", () => {
    expect(ok("g")).toBe(9.81);
  });

  test("degrees convert", () => {
    expect(ok("sin(rad(90))")).toBe(1);
  });

  test("ternary picks a branch", () => {
    expect(ok("v > 5 ? 1 : 0", { v: 9 })).toBe(1);
    expect(ok("v > 5 ? 1 : 0", { v: 2 })).toBe(0);
  });

  test("clamp bounds a value", () => {
    expect(ok("clamp(15, 0, 10)")).toBe(10);
  });
});

// The evaluator's whole purpose is running model-written text safely. These are
// the tests that matter.
describe("containment", () => {
  const rejected = [
    ["globals", "window"],
    ["arbitrary calls", "alert(1)"],
    ["property access", "x.y"],
    ["constructor escape", "constructor"],
    ["unknown identifiers", "unknownvar + 1"],
    ["unknown functions", "exfiltrate(1)"],
    ["assignment", "x = 1"],
    ["semicolon sequencing", "1; 2"],
    ["trailing junk", "1 + 1 garbage"],
    ["non-finite results", "1/0"],
    ["empty input", ""],
  ] as const;

  for (const [label, src] of rejected) {
    test(`rejects ${label}`, () => {
      expect(evaluate(src, { x: 1 }).ok).toBe(false);
    });
  }

  test("rejects an over-long formula", () => {
    expect(evaluate("1+".repeat(400) + "1", {}).ok).toBe(false);
  });

  test("rejects an over-complex expression", () => {
    expect(evaluate("(".repeat(150) + "1" + ")".repeat(150), {}).ok).toBe(false);
  });

  test("never throws, whatever it is handed", () => {
    for (const junk of ["((((", "*/*", "?:", "()", "1 ? 2", "min(", ",,,"]) {
      expect(() => evaluate(junk, {})).not.toThrow();
      expect(evaluate(junk, {}).ok).toBe(false);
    }
  });
});
