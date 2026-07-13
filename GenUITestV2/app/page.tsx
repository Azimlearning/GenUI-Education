"use client";

import { useState } from "react";
import { RenderNode, type InputValues } from "@/components/Renderer";
import type { UISpec } from "@/lib/uispec";

interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

interface LogEntry {
  time: string;
  text: string;
}

const EXAMPLE_PROMPTS = [
  "Compare renting vs buying a car in Malaysia",
  "Teach me how osmosis works, then quiz me",
  "Help me plan a monthly budget on a RM3200 salary",
  "Explain the difference between speed and velocity",
];

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [history, setHistory] = useState<ChatMessage[]>([]);
  const [spec, setSpec] = useState<UISpec | null>(null);
  const [values, setValues] = useState<InputValues>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showRaw, setShowRaw] = useState(false);
  const [log, setLog] = useState<LogEntry[]>([]);

  const addLog = (text: string) =>
    setLog((prev) => [{ time: new Date().toLocaleTimeString(), text }, ...prev].slice(0, 50));

  async function generate(messages: ChatMessage[]) {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? `HTTP ${res.status}`);

      const newSpec = data.spec as UISpec;
      setSpec(newSpec);
      setValues({});
      setHistory([...messages, { role: "assistant", content: JSON.stringify(newSpec) }]);
      addLog(`spec received from ${data.model} (${JSON.stringify(newSpec).length} chars)`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }

  function submitPrompt(text: string) {
    const trimmed = text.trim();
    if (!trimmed || loading) return;
    setPrompt("");
    addLog(`prompt: "${trimmed}"`);
    // A fresh prompt starts a fresh conversation; actions continue the current one.
    void generate([{ role: "user", content: trimmed }]);
  }

  function handleAction(action: string, label: string) {
    if (loading) return;
    addLog(`action: "${action}" with values ${JSON.stringify(values)}`);
    const interaction = `The user pressed the button "${label}" (action: "${action}"). Current input values: ${JSON.stringify(
      values,
    )}. Generate the next state of the interface.`;
    void generate([...history, { role: "user", content: interaction }]);
  }

  return (
    <main className="app">
      <header className="app-header">
        <div>
          <h1>GenUI test v2</h1>
          <p className="g-muted">
            Level 2 generative UI — the model returns a declarative JSON spec, this page renders
            it. Nothing below is hardcoded.
          </p>
        </div>
        {spec ? (
          <button className="g-button g-button-secondary" onClick={() => setShowRaw(!showRaw)}>
            {showRaw ? "Rendered view" : "View raw spec"}
          </button>
        ) : null}
      </header>

      <form
        className="prompt-bar"
        onSubmit={(e) => {
          e.preventDefault();
          submitPrompt(prompt);
        }}
      >
        <input
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Ask anything — the interface is generated to fit the answer…"
          disabled={loading}
        />
        <button className="g-button g-button-primary" type="submit" disabled={loading}>
          {loading ? "Generating…" : "Generate"}
        </button>
      </form>

      <div className="chips">
        {EXAMPLE_PROMPTS.map((p) => (
          <button key={p} className="chip" onClick={() => submitPrompt(p)} disabled={loading}>
            {p}
          </button>
        ))}
      </div>

      {error ? <div className="g-callout g-tone-danger">{error}</div> : null}

      <div className="stage">
        {loading ? (
          <div className="skeleton">
            <div className="skeleton-bar" style={{ width: "40%" }} />
            <div className="skeleton-bar" style={{ width: "90%" }} />
            <div className="skeleton-bar" style={{ width: "75%" }} />
            <div className="skeleton-bar" style={{ width: "85%" }} />
            <p className="g-muted">Designing an interface for this answer…</p>
          </div>
        ) : spec ? (
          showRaw ? (
            <pre className="raw-spec">{JSON.stringify(spec, null, 2)}</pre>
          ) : (
            <div className="generated">
              {spec.title ? <div className="generated-title">{spec.title}</div> : null}
              <RenderNode
                node={spec.root}
                ctx={{
                  values,
                  setValue: (id, v) => setValues((prev) => ({ ...prev, [id]: v })),
                  onAction: handleAction,
                }}
              />
            </div>
          )
        ) : (
          <div className="empty g-muted">
            Ask a question above. A comparison should come back as a table, metrics as stats, a
            lesson as an interactive explainer — same model, different form every time.
          </div>
        )}
      </div>

      {log.length > 0 ? (
        <details className="event-log" open>
          <summary>Event log ({log.length})</summary>
          <ul>
            {log.map((entry, i) => (
              <li key={i}>
                <span className="g-muted">{entry.time}</span> {entry.text}
              </li>
            ))}
          </ul>
        </details>
      ) : null}
    </main>
  );
}
