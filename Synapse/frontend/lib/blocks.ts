// The pattern → React component map (ADR-009 / ADR-010 — frontend half of the seam).
//
// The backend Composer emits a `component_block` with a `pattern` string; this map resolves it
// to the React implementation in `components/library/`. The keys here MUST match the backend
// registry patterns in `backend/app/components/registry.py` (D-10) — all 14 are mapped.

import type { ComponentType } from "react";
import type { LibraryComponentProps } from "@/components/library/shared";

import AtomicStructureExplorer from "@/components/library/AtomicStructureExplorer";
import CircuitBuilderSandbox from "@/components/library/CircuitBuilderSandbox";
import ElectronBondingExplorer from "@/components/library/ElectronBondingExplorer";
import ForceMotionSim from "@/components/library/ForceMotionSim";
import GradientDiffusionSandbox from "@/components/library/GradientDiffusionSandbox";
import LabelledDiagramExplorer from "@/components/library/LabelledDiagramExplorer";
import MatchingPairs from "@/components/library/MatchingPairs";
import ProcessTimeline from "@/components/library/ProcessTimeline";
import PunnettSquareBuilder from "@/components/library/PunnettSquareBuilder";
import QuickCheckQuiz from "@/components/library/QuickCheckQuiz";
import ReactionLabSandbox from "@/components/library/ReactionLabSandbox";
import SignalPathwaySim from "@/components/library/SignalPathwaySim";
import StageSequencer from "@/components/library/StageSequencer";
import WaveOpticsSandbox from "@/components/library/WaveOpticsSandbox";

export type LibraryComponent = ComponentType<LibraryComponentProps>;

export const LIBRARY: Record<string, LibraryComponent> = {
  // Biology
  "gradient-diffusion-sandbox": GradientDiffusionSandbox,
  "process-timeline": ProcessTimeline,
  "stage-sequencer": StageSequencer,
  "labelled-diagram-explorer": LabelledDiagramExplorer,
  "matching-pairs": MatchingPairs,
  "punnett-square-builder": PunnettSquareBuilder,
  "signal-pathway-sim": SignalPathwaySim,
  // Chemistry
  "reaction-lab-sandbox": ReactionLabSandbox,
  "electron-bonding-explorer": ElectronBondingExplorer,
  "atomic-structure-explorer": AtomicStructureExplorer,
  // Physics
  "force-motion-sim": ForceMotionSim,
  "circuit-builder-sandbox": CircuitBuilderSandbox,
  "wave-optics-sandbox": WaveOpticsSandbox,
  // Cross-subject
  "quick-check-quiz": QuickCheckQuiz,
};

export function resolvePattern(pattern: string): LibraryComponent | null {
  return LIBRARY[pattern] ?? null;
}
