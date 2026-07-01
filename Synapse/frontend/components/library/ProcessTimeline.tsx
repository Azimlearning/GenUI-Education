"use client";

// Pattern: process-timeline (menstrual cycle & egg movement, cardiac cycle…).
// Drag the day slider across a 28-day cycle; the phase, key event, and hormone levels update.
// Faithful: menstruation days 1–5, ovulation ~day 14, luteal phase after; LH peaks just before
// ovulation, progesterone rises in the luteal phase.

import { useState } from "react";

import { PatternCard, type LibraryComponentProps } from "./shared";

type Stage = { from: number; to: number; title: string; blurb: string };

const DEFAULT_STAGES: Stage[] = [
  { from: 1, to: 5, title: "Menstruation", blurb: "The uterus lining breaks down and is shed." },
  { from: 6, to: 13, title: "Follicular phase", blurb: "FSH matures a follicle; oestrogen rises and rebuilds the lining." },
  { from: 14, to: 14, title: "Ovulation", blurb: "An LH surge releases the egg from the ovary (~day 14)." },
  { from: 15, to: 28, title: "Luteal phase", blurb: "The corpus luteum secretes progesterone to maintain the lining." },
];

export default function ProcessTimeline({ props, meta }: LibraryComponentProps) {
  const label = String(props.duration_label ?? "28-day cycle");
  const [day, setDay] = useState(14);
  const stage = DEFAULT_STAGES.find((s) => day >= s.from && day <= s.to) ?? DEFAULT_STAGES[0];

  // Rough, correct-shape hormone levels (0..1) for the current day.
  const oestrogen = day <= 13 ? day / 13 : day === 14 ? 1 : 0.4;
  const lh = day >= 13 && day <= 15 ? 1 : 0.15;
  const progesterone = day >= 15 ? Math.min(1, (day - 14) / 8) : 0.1;

  return (
    <PatternCard title={label} meta={meta}>
      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: "var(--slate)" }}>
        <span>Day 1</span><span style={{ fontWeight: 800, color: "var(--indigo)" }}>Day {day}</span><span>Day 28</span>
      </div>
      <input type="range" min={1} max={28} value={day} onChange={(e) => setDay(Number(e.target.value))} style={{ width: "100%" }} />

      <div style={{ marginTop: 8, padding: 12, borderRadius: 10, background: "var(--indigo-soft)" }}>
        <div style={{ fontWeight: 800, color: "var(--indigo)" }}>{stage.title}</div>
        <p style={{ margin: "4px 0 0", fontSize: 14 }}>{stage.blurb}</p>
      </div>

      <div style={{ marginTop: 10, display: "flex", flexDirection: "column", gap: 6 }}>
        <Bar label="Oestrogen" v={oestrogen} color="#0d9488" />
        <Bar label="LH" v={lh} color="#4f46e5" />
        <Bar label="Progesterone" v={progesterone} color="#d97706" />
      </div>
    </PatternCard>
  );
}

function Bar({ label, v, color }: { label: string; v: number; color: string }) {
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <span style={{ width: 96, fontSize: 12, color: "var(--slate)" }}>{label}</span>
      <div style={{ flex: 1, height: 10, background: "#f1f5f9", borderRadius: 6, overflow: "hidden" }}>
        <div style={{ width: `${Math.round(v * 100)}%`, height: "100%", background: color, transition: "width .2s" }} />
      </div>
    </div>
  );
}
