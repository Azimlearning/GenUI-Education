// The pattern → React component map (ADR-009 / ADR-010 — frontend half of the seam).
//
// The backend Composer emits a `component_block` with a `pattern` string; this map resolves it
// to the React implementation in `components/library/`. The set of keys here MUST match the
// backend registry patterns in `backend/app/components/registry.py` (D-10).

import type { ComponentType } from "react";
import type { LibraryComponentProps } from "@/components/library/shared";

import ContrastingPairWalkthrough from "@/components/library/ContrastingPairWalkthrough";
import ForceMotionSim from "@/components/library/ForceMotionSim";
import GradientDiffusionSandbox from "@/components/library/GradientDiffusionSandbox";
import LabelledDiagramExplorer from "@/components/library/LabelledDiagramExplorer";
import QuickCheckQuiz from "@/components/library/QuickCheckQuiz";
import TitrationSandbox from "@/components/library/TitrationSandbox";

export type LibraryComponent = ComponentType<LibraryComponentProps>;

export const LIBRARY: Record<string, LibraryComponent> = {
  "gradient-diffusion-sandbox": GradientDiffusionSandbox,
  "contrasting-pair-walkthrough": ContrastingPairWalkthrough,
  "labelled-diagram-explorer": LabelledDiagramExplorer,
  "quick-check-quiz": QuickCheckQuiz,
  "force-motion-sim": ForceMotionSim,
  "titration-sandbox": TitrationSandbox,
};

export function resolvePattern(pattern: string): LibraryComponent | null {
  return LIBRARY[pattern] ?? null;
}
