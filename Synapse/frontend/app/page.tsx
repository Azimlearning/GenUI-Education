"use client";

import { useRef, useState } from "react";
import type { CSSProperties } from "react";

import AgentPipeline from "@/components/AgentPipeline";
import BlockRenderer from "@/components/library/BlockRenderer";
import { ask, fetchProfile, postInteraction, type LearnerProfile } from "@/lib/client";
import type { AgentStep, ComponentBlock } from "@/lib/types";

const CHIPS: { label: string; q: string }[] = [
  { label: `"osmosis is when water moves to where there's more water"`, q: "osmosis is when water moves to where there's more water" },
  { label: `"a moving trolley needs a constant force to keep moving"`, q: "why does a moving object need a force to keep moving?" },
  { label: `"I don't understand ionic vs covalent bonding"`, q: "I don't understand ionic vs covalent bonding" },
  { label: `"how do I balance H2 + O2 → H2O?"`, q: "how do I balance this equation? H2 + O2 -> H2O" },
];

// A stable per-browser student id so the Tutor Loop has a profile to write to.
const STUDENT_ID = "demo-student";

export default function Home() {
  const [question, setQuestion] = useState("");
  const [steps, setSteps] = useState<AgentStep[]>([]);
  const [block, setBlock] = useState<ComponentBlock | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [profile, setProfile] = useState<LearnerProfile | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const blockRef = useRef<ComponentBlock | null>(null);

  function handleInteraction(ev: { correct: boolean }) {
    const b = blockRef.current;
    if (!b) return;
    void postInteraction({
      student_id: STUDENT_ID,
      topic: b.meta.topic,
      correct: ev.correct,
      misconception_id: b.meta.misconception_id,
      pattern: b.pattern,
    }).then((p) => {
      if (p) setProfile(p);
    });
  }

  function run(q: string) {
    const text = q.trim();
    if (!text || busy) return;

    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;

    setQuestion(text);
    setSteps([]);
    setBlock(null);
    setError(null);
    setBusy(true);

    void ask(
      text,
      STUDENT_ID,
      {
        onEvent: (ev) => {
          if (ev.type === "agent_step") setSteps((prev) => [...prev, ev]);
          else if (ev.type === "component_block") {
            setBlock(ev.block);
            blockRef.current = ev.block;
          } else if (ev.type === "error") setError(ev.message);
        },
        onError: (err) => {
          setError(err.message);
          setBusy(false);
        },
        onClose: () => {
          setBusy(false);
          void fetchProfile(STUDENT_ID).then((p) => p && setProfile(p));
        },
      },
      controller.signal,
    );
  }

  return (
    <>
      {/* ── Top bar ── */}
      <header style={topbar}>
        <LogoMark />
        <div style={{ fontSize: 20, fontWeight: 800, letterSpacing: "-0.5px", color: "var(--indigo)" }}>
          Synap<span style={{ color: "var(--teal)" }}>se</span>
        </div>
        <div style={tag}>KSSM · Form 4–5 Science</div>
      </header>

      <main style={wrap}>
        {/* ── Hero ── */}
        <div style={{ textAlign: "center", marginBottom: 30 }}>
          <h1 style={{ fontSize: 30, fontWeight: 800, letterSpacing: "-0.6px", margin: "0 0 8px" }}>
            Ask anything in <span style={grad}>Physics, Biology, or Chemistry</span>
          </h1>
          <p style={{ color: "var(--slate)", fontSize: 15, maxWidth: 520, margin: "0 auto" }}>
            Type a question in your own words. Synapse diagnoses what you need and builds the right
            interactive way to learn it — and you can watch its agents decide.
          </p>
        </div>

        {/* ── Prompt ── */}
        <form
          style={promptCard}
          onSubmit={(e) => {
            e.preventDefault();
            run(question);
          }}
        >
          <input
            style={input}
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g. explain osmosis to me"
            autoComplete="off"
          />
          <button type="submit" style={askBtn} disabled={busy}>
            {busy ? "Thinking…" : "Ask Synapse"}
          </button>
        </form>

        <div style={chipsLabel}>Try one of these</div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8, justifyContent: "center" }}>
          {CHIPS.map((c) => (
            <button key={c.q} style={chip} onClick={() => run(c.q)} disabled={busy}>
              {c.label}
            </button>
          ))}
        </div>

        {/* ── Streamed reasoning + composed component ── */}
        {error && (
          <div style={errorBox}>
            {error}
            <div style={{ fontSize: 12, marginTop: 4, opacity: 0.8 }}>
              Is the backend running on <code>NEXT_PUBLIC_API_BASE</code>? See README → Run locally.
            </div>
          </div>
        )}

        <AgentPipeline steps={steps} />

        {block && (
          <div style={{ marginTop: 20 }}>
            <BlockRenderer block={block} onInteraction={handleInteraction} />
          </div>
        )}

        {profile && Object.keys(profile.mastery).length > 0 && (
          <ProgressPanel profile={profile} />
        )}

        <p style={footnote}>
          The agent pipeline is streamed live from the FastAPI + LangGraph backend over SSE. It
          runs on scripted logic with no API key, and on live Claude when one is set. Every
          interactive is a pre-built, KSSM-faithful component the agents select and configure.
        </p>
      </main>
    </>
  );
}

function LogoMark() {
  return (
    <svg viewBox="0 0 40 40" fill="none" width={34} height={34} aria-hidden>
      <circle cx="10" cy="13" r="4" fill="#3730A3" />
      <circle cx="30" cy="10" r="4" fill="#4F46E5" />
      <circle cx="20" cy="26" r="4.5" fill="#0D9488" />
      <circle cx="32" cy="30" r="3.5" fill="#0D9488" />
      <circle cx="8" cy="30" r="3.5" fill="#4F46E5" />
      <line x1="10" y1="13" x2="20" y2="26" stroke="#94A3B8" strokeWidth="1.5" />
      <line x1="30" y1="10" x2="20" y2="26" stroke="#94A3B8" strokeWidth="1.5" />
      <line x1="20" y1="26" x2="32" y2="30" stroke="#94A3B8" strokeWidth="1.5" />
      <line x1="20" y1="26" x2="8" y2="30" stroke="#94A3B8" strokeWidth="1.5" />
      <line x1="10" y1="13" x2="30" y2="10" stroke="#CBD5E1" strokeWidth="1.2" />
    </svg>
  );
}

function ProgressPanel({ profile }: { profile: LearnerProfile }) {
  const topics = Object.entries(profile.mastery);
  return (
    <div style={{ marginTop: 20, background: "var(--white)", border: "1px solid var(--line)", borderRadius: 16, boxShadow: "var(--shadow)", padding: 20 }}>
      <div style={{ fontSize: 15, fontWeight: 800, color: "var(--indigo)", marginBottom: 4 }}>Your progress</div>
      <div style={{ fontSize: 12.5, color: "var(--slate)", marginBottom: 12 }}>
        The tutor loop updates this from how you did. It informs what Synapse composes next time.
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {topics.map(([topic, m]) => (
          <div key={topic} style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ width: 150, fontSize: 12.5, color: "var(--ink)", textTransform: "capitalize" }}>{topic}</span>
            <div style={{ flex: 1, height: 10, background: "#f1f5f9", borderRadius: 6, overflow: "hidden" }}>
              <div style={{ width: `${Math.round(m * 100)}%`, height: "100%", background: "var(--teal)", transition: "width .3s" }} />
            </div>
            <span style={{ width: 40, textAlign: "right", fontSize: 12, color: "var(--slate)" }}>{Math.round(m * 100)}%</span>
          </div>
        ))}
      </div>
      {profile.misconceptions.length > 0 && (
        <div style={{ marginTop: 12, fontSize: 12.5, color: "var(--slate)" }}>
          Tracking:{" "}
          {profile.misconceptions.map((mc) => (
            <span key={mc.misconception_id} style={{ display: "inline-block", margin: "2px 4px 2px 0", padding: "3px 9px", borderRadius: 20, background: mc.resolved ? "var(--teal-soft)" : "var(--indigo-soft)", color: mc.resolved ? "var(--teal)" : "var(--indigo)" }}>
              {mc.topic} {mc.resolved ? "✓ cleared" : "· in review"}
            </span>
          ))}
          {profile.due_now.length > 0 && (
            <div style={{ marginTop: 6, color: "var(--amber)" }}>Due for review now: {profile.due_now.join(", ")}</div>
          )}
        </div>
      )}
    </div>
  );
}

// ── inline styles (ported from ../Synapse_Demo.html) ──
const topbar: CSSProperties = {
  background: "var(--white)",
  borderBottom: "1px solid var(--line)",
  padding: "14px 28px",
  display: "flex",
  alignItems: "center",
  gap: 12,
  position: "sticky",
  top: 0,
  zIndex: 50,
};
const tag: CSSProperties = {
  marginLeft: "auto",
  fontSize: 12,
  color: "var(--slate)",
  background: "var(--indigo-soft)",
  padding: "5px 12px",
  borderRadius: 20,
  fontWeight: 600,
};
const wrap: CSSProperties = { maxWidth: 920, margin: "0 auto", padding: "36px 24px 80px" };
const grad: CSSProperties = {
  background: "linear-gradient(100deg, var(--indigo-2), var(--teal))",
  WebkitBackgroundClip: "text",
  backgroundClip: "text",
  WebkitTextFillColor: "transparent",
};
const promptCard: CSSProperties = {
  background: "var(--white)",
  border: "1px solid var(--line)",
  borderRadius: 18,
  boxShadow: "var(--shadow)",
  padding: "10px 10px 10px 18px",
  display: "flex",
  alignItems: "center",
  gap: 10,
  marginBottom: 16,
};
const input: CSSProperties = {
  flex: 1,
  border: "none",
  outline: "none",
  fontSize: 16,
  color: "var(--ink)",
  background: "transparent",
  fontFamily: "inherit",
};
const askBtn: CSSProperties = {
  background: "var(--indigo)",
  color: "#fff",
  border: "none",
  padding: "12px 22px",
  borderRadius: 12,
  fontSize: 15,
  fontWeight: 700,
  cursor: "pointer",
  fontFamily: "inherit",
  whiteSpace: "nowrap",
};
const chipsLabel: CSSProperties = {
  textAlign: "center",
  fontSize: 12,
  color: "#94a3b8",
  margin: "18px 0 10px",
  textTransform: "uppercase",
  letterSpacing: 1,
};
const chip: CSSProperties = {
  background: "var(--white)",
  border: "1px solid var(--line)",
  color: "var(--slate)",
  fontSize: 13,
  padding: "7px 14px",
  borderRadius: 20,
  cursor: "pointer",
  fontFamily: "inherit",
};
const footnote: CSSProperties = {
  marginTop: 40,
  paddingTop: 16,
  borderTop: "1px solid var(--line)",
  fontSize: 12.5,
  color: "var(--slate)",
  textAlign: "center",
};
const errorBox: CSSProperties = {
  marginTop: 20,
  border: "1px solid var(--rose)",
  background: "#fff1f2",
  color: "var(--rose)",
  borderRadius: 12,
  padding: 16,
  fontSize: 14,
};
