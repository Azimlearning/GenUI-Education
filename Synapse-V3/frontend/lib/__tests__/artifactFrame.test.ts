import { describe, expect, it } from "vitest";

import { fitArtifactToFrame } from "@/lib/artifactFrame";

describe("fitArtifactToFrame", () => {
  it("adds a no-scroll, viewport-fitting layer to generated documents", () => {
    const html = "<!doctype html><html><head></head><body><main>lab</main></body></html>";
    const result = fitArtifactToFrame(html);

    expect(result).toContain("overflow: hidden !important");
    expect(result).toContain("--synapse-fit-scale");
    expect(result).toContain("fitArtifact");
  });

  it("does not inject the fitter twice", () => {
    const once = fitArtifactToFrame("<html><head></head><body></body></html>");
    expect(fitArtifactToFrame(once)).toBe(once);
  });
});
