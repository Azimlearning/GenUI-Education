/**
 * The single SSE reducer: events in, UI state out (TECHNICAL.md frontend
 * conventions). No component subscribes to raw SSE; the page dispatches
 * every stream event through here.
 */
import type { AxiomEvent, Meta } from "@/types/events";

export type ChatMessage =
  | { role: "user"; content: string }
  | { role: "assistant"; content: string; streaming: boolean; meta: Meta | null };

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
  | { type: "stream_closed" };

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
          { role: "assistant", content: "", streaming: true, meta: null },
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
        // Artifact and tutor events arrive in later phases; the protocol
        // already types them so ignoring is an explicit decision here.
        case "artifact_status":
        case "artifact_delta":
        case "artifact_done":
        case "artifact_failed":
        case "tutor_msg":
          return state;
      }
      return state;
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
