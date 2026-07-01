// Frontend mirror of the backend SSE contract (ADR-010 / D-10).
// KEEP IN SYNC with `backend/app/models/schemas.py`. Treat a change to a wire type here and
// there as a single change.

export type AgentName =
  | "diagnostician"
  | "pedagogy_strategist"
  | "component_composer"
  | "tutor_loop";

export type AgentStatus = "thinking" | "done" | "skipped";

export type Technique =
  | "contrasting-cases"
  | "predict-observe-explain"
  | "worked-example-fading"
  | "retrieval-practice"
  | "labelled-exploration";

export interface AgentStep {
  type: "agent_step";
  agent: AgentName;
  status: AgentStatus;
  detail: string;
}

export interface BlockMeta {
  subject: string;
  form: number;
  topic: string;
  strategy: Technique;
  misconception_id: string | null;
}

export interface ComponentBlock {
  pattern: string;
  props: Record<string, unknown>;
  meta: BlockMeta;
}

export interface ComponentEvent {
  type: "component_block";
  block: ComponentBlock;
}

export interface DoneEvent {
  type: "done";
}

export interface ErrorEvent {
  type: "error";
  message: string;
}

export type SSEEvent = AgentStep | ComponentEvent | DoneEvent | ErrorEvent;

// Human-friendly labels for the visible pipeline UI.
export const AGENT_LABEL: Record<AgentName, string> = {
  diagnostician: "Diagnostician",
  pedagogy_strategist: "Pedagogy Strategist",
  component_composer: "Component Composer",
  tutor_loop: "Tutor Loop",
};
