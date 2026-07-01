"use client";

// Pattern: quick-check-quiz (retrieval practice across any topic).
// Instant client-side feedback. Supports mcq, numeric, and coefficient (equation-balancing)
// answer types. The `correct` prop is checked locally so the reveal is immediate.

import { useState } from "react";
import type { CSSProperties } from "react";

import { PatternCard, type LibraryComponentProps } from "./shared";

export default function QuickCheckQuiz({ props, meta }: LibraryComponentProps) {
  const prompt = String(props.prompt ?? "Quick check");
  const answerType = String(props.answer_type ?? "mcq");
  const options = Array.isArray(props.options) ? (props.options as unknown[]).map(String) : [];
  const correct = props.correct;

  const [choice, setChoice] = useState<string>("");
  const [checked, setChecked] = useState(false);

  const isCorrect = checked && matches(choice, correct, answerType);

  return (
    <PatternCard title="Quick check" meta={meta}>
      <p style={{ fontSize: 15, fontWeight: 700, margin: "0 0 12px", fontFamily: "ui-monospace, monospace" }}>{prompt}</p>

      {answerType === "mcq" && options.length > 0 ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {options.map((o) => (
            <button key={o} disabled={checked} onClick={() => setChoice(o)}
              style={{ ...optBtn, border: choice === o ? "2px solid var(--indigo-2)" : "1px solid var(--line)", background: choice === o ? "var(--indigo-soft)" : "var(--white)" }}>
              {o}
            </button>
          ))}
        </div>
      ) : (
        <input value={choice} disabled={checked} onChange={(e) => setChoice(e.target.value)}
          placeholder={answerType === "coefficients" ? "e.g. 2,1,2" : "your answer"}
          style={{ width: "100%", padding: "10px 12px", borderRadius: 10, border: "1px solid var(--line)", fontSize: 14, fontFamily: "inherit" }} />
      )}

      {!checked ? (
        <button style={{ ...runBtn, opacity: choice ? 1 : 0.5, cursor: choice ? "pointer" : "not-allowed" }} disabled={!choice} onClick={() => setChecked(true)}>
          Check answer
        </button>
      ) : (
        <div style={{ marginTop: 12, borderRadius: 12, padding: 12, background: isCorrect ? "var(--teal-soft)" : "#fff7ed", border: `1px solid ${isCorrect ? "var(--teal)" : "#fed7aa"}`, animation: "fade .3s" }}>
          <strong style={{ color: isCorrect ? "var(--teal)" : "var(--amber)" }}>
            {isCorrect ? "Correct." : `Not quite. Correct answer: ${formatCorrect(correct)}`}
          </strong>
          <div><button style={retryBtn} onClick={() => { setChecked(false); setChoice(""); }}>Try again</button></div>
        </div>
      )}
    </PatternCard>
  );
}

function matches(choice: string, correct: unknown, type: string): boolean {
  if (type === "coefficients" && Array.isArray(correct)) {
    const got = choice.split(/[,\s]+/).filter(Boolean).map(Number);
    return got.length === correct.length && got.every((n, i) => n === Number(correct[i]));
  }
  if (type === "numeric") return Number(choice) === Number(correct);
  return choice.trim().toLowerCase() === String(correct).trim().toLowerCase();
}

function formatCorrect(correct: unknown): string {
  return Array.isArray(correct) ? correct.join(", ") : String(correct);
}

const optBtn: CSSProperties = { textAlign: "left", padding: "10px 12px", borderRadius: 10, fontSize: 14, fontFamily: "inherit", cursor: "pointer", color: "var(--ink)" };
const runBtn: CSSProperties = { marginTop: 12, background: "var(--indigo)", color: "#fff", border: "none", padding: "10px 18px", borderRadius: 10, fontSize: 14, fontWeight: 700, fontFamily: "inherit" };
const retryBtn: CSSProperties = { marginTop: 8, background: "var(--white)", border: "1px solid var(--line)", color: "var(--slate)", padding: "6px 12px", borderRadius: 8, fontSize: 12.5, fontFamily: "inherit", cursor: "pointer" };
