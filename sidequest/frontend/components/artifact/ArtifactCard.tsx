"use client";

import type { ArtifactState } from "@/lib/reducer";
import { DegradedCard } from "@/components/artifact/DegradedCard";
import { ProgressStages } from "@/components/artifact/ProgressStages";
import { SandboxFrame } from "@/components/artifact/SandboxFrame";

/** State machine renderer: loading(stage) -> ready | degraded (TECHNICAL.md). */
export function ArtifactCard({
  artifact,
  onRetry,
  onCrash,
}: {
  artifact: ArtifactState;
  onRetry: () => void;
  onCrash: (message: string) => void;
}) {
  switch (artifact.status) {
    case "none":
      return null;
    case "building":
      return <ProgressStages stage={artifact.stage} codePreview={artifact.codePreview} />;
    case "ready":
      return (
        <SandboxFrame html={artifact.html} title={artifact.title} onCrash={onCrash} />
      );
    case "failed":
      return (
        <DegradedCard
          detail={artifact.detailUser}
          retryable={artifact.retryable}
          onRetry={onRetry}
        />
      );
    case "crashed":
      return (
        <DegradedCard
          detail="The interactive piece stopped working, so I took it down."
          retryable
          onRetry={onRetry}
        />
      );
    case "flagged":
      return (
        <DegradedCard
          detail="This interactive was flagged and is hidden while a new version is prepared."
          retryable
          onRetry={onRetry}
        />
      );
  }
}
