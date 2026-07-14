"use client";

/**
 * Pattern -> component resolution.
 *
 * The registry and lib/science/catalog.ts are two halves of one contract: the
 * catalog tells the model what exists, this maps what it chose to real code. v1
 * let these drift (the registry advertised slots no component read) and nothing
 * caught it, so the seam the whole architecture rests on was quietly broken.
 *
 * Two guards: the ids are checked against the catalog at module load, and an
 * unresolvable pattern renders a visible notice instead of throwing.
 */

import { BY_ID } from "@/lib/science/catalog";
import type { ScienceProps } from "./shared";
import OsmosisSandbox from "./OsmosisSandbox";
import MotionSandbox from "./MotionSandbox";
import BondingExplorer from "./BondingExplorer";
import CircuitSandbox from "./CircuitSandbox";
import RefractionSandbox from "./RefractionSandbox";

const REGISTRY: Record<string, React.ComponentType<ScienceProps>> = {
  "concentration-gradient-sandbox": OsmosisSandbox,
  "motion-sandbox": MotionSandbox,
  "bonding-explorer": BondingExplorer,
  "circuit-sandbox": CircuitSandbox,
  "refraction-sandbox": RefractionSandbox,
};

// Catch drift at load, in dev, rather than on stage.
if (process.env.NODE_ENV !== "production") {
  for (const id of BY_ID.keys()) {
    if (!REGISTRY[id]) console.warn(`[synapse] catalog advertises "${id}" with no component`);
  }
  for (const id of Object.keys(REGISTRY)) {
    if (!BY_ID.has(id)) console.warn(`[synapse] component "${id}" is not in the catalog`);
  }
}

export function ScienceComponent({
  pattern,
  slots,
  onInteraction,
}: { pattern: string } & ScienceProps) {
  const Component = REGISTRY[pattern];

  if (!Component) {
    return (
      <div className="drift">
        <strong>Component drift.</strong> The pipeline asked for <code>{pattern}</code>, which this
        build does not have. This notice exists so the mismatch is visible rather than silent.
      </div>
    );
  }

  return <Component slots={slots} onInteraction={onInteraction} />;
}
