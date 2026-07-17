/**
 * The single SSE reducer: events in, UI state out (TECHNICAL.md frontend
 * conventions). No component subscribes to raw SSE; the page dispatches
 * every stream event through here.
 */
import type { AxiomEvent, Meta } from "@/types/events";

/** Artifact card state machine: discriminated union, not booleans
 *  (TECHNICAL.md frontend conventions). `crashed` is entered from the
 *  runtime side (watchdog timeout or axiom_error), not from SSE. */
export type ArtifactState =
  | { status: "none" }
  | { status: "building"; stage: string }
  | { status: "ready"; artifactId: string; title: string; html: string }
  | { status: "failed"; reason: string; detailUser: string; retryable: boolean }
  | { status: "crashed"; message: string };

export type ChatMessage =
  | { role: "user"; content: string }
  | {
      role: "assistant";
      content: string;
      streaming: boolean;
      meta: Meta | null;
      artifact: ArtifactState;
    };

export type ChatStatus = "idle" | "waiting" | "streaming" | "error";

export interface ChatState {
  messages: ChatMessage[];
  status: ChatStatus;
  error: string | null;
}

export const initialChatState: ChatState = {
  messages: [],
  status: "idle",
  error: null,
};

export type ChatAction =
  | { type: "user_sent"; message: string }
  | { type: "stream_event"; event: AxiomEvent }
  | { type: "stream_error"; message: string }
  | { type: "stream_closed" }
  | { type: "artifact_crashed"; index: number; message: string };

function updateLastAssistant(
  state: ChatState,
  update: (msg: Extract<ChatMessage, { role: "assistant" }>) => ChatMessage
): ChatState {
  const messages = [...state.messages];
  for (let i = messages.length - 1; i >= 0; i--) {
    const msg = messages[i];
    if (msg && msg.role === "assistant") {
      messages[i] = update(msg);
      return { ...state, messages };
    }
  }
  return state;
}

export function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case "user_sent":
      return {
        status: "waiting",
        error: null,
        messages: [
          ...state.messages,
          { role: "user", content: action.message },
          {
            role: "assistant",
            content: "",
            streaming: true,
            meta: null,
            artifact: { status: "none" },
          },
        ],
      };

    case "stream_event": {
      const event = action.event;
      switch (event.type) {
        case "meta":
          return updateLastAssistant({ ...state, status: "streaming" }, (msg) => ({
            ...msg,
            meta: event.data,
          }));
        case "text_delta":
          return updateLastAssistant(state, (msg) => ({
            ...msg,
            content: msg.content + event.data.chunk,
          }));
        case "text_done":
          return updateLastAssistant(state, (msg) => ({ ...msg, streaming: false }));
        case "done":
          return { ...state, status: "idle" };
        case "artifact_status":
          return updateLastAssistant(state, (msg) => ({
            ...msg,
            artifact: { status: "building", stage: event.data.stage },
          }));
        case "artifact_done":
          return updateLastAssistant(state, (msg) => ({
            ...msg,
            artifact: {
              status: "ready",
              artifactId: event.data.artifact_id,
              title: event.data.title,
              html: event.data.html,
            },
          }));
        case "artifact_failed":
          return updateLastAssistant(state, (msg) => ({
            ...msg,
            artifact: {
              status: "failed",
              reason: event.data.reason,
              detailUser: event.data.detail_user,
              retryable: event.data.retryable,
            },
          }));
        // Progressive code stream and tutor messages arrive in later phases;
        // the protocol already types them so ignoring is an explicit decision.
        case "artifact_delta":
        case "tutor_msg":
          return state;
      }
      return state;
    }

    case "artifact_crashed": {
      const messages = [...state.messages];
      const msg = messages[action.index];
      if (!msg || msg.role !== "assistant") return state;
      messages[action.index] = {
        ...msg,
        artifact: { status: "crashed", message: action.message },
      };
      return { ...state, messages };
    }

    case "stream_error":
      return {
        ...updateLastAssistant(state, (msg) => ({ ...msg, streaming: false })),
        status: "error",
        error: action.message,
      };

    case "stream_closed":
      // Normal completion already set idle via `done`; this catches aborts.
      return state.status === "idle"
        ? state
        : {
            ...updateLastAssistant(state, (msg) => ({ ...msg, streaming: false })),
            status: state.status === "error" ? "error" : "idle",
          };
  }
}
