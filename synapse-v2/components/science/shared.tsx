"use client";

/** Shared shell and controls for the Tier A science components. */

import type { ReactNode } from "react";
import type { Subject } from "@/lib/science/catalog";

/** Every science component takes this. Uniform, so the renderer stays dumb. */
export interface ScienceProps {
  slots: Record<string, unknown>;
  onInteraction?: (action: string, values: Record<string, string | number | boolean>) => void;
}

/* Slot readers. The slots are validated server-side, but a component that
   crashes on a surprise value takes the whole demo down, so read defensively. */

export const slotNum = (slots: Record<string, unknown>, key: string, fallback: number): number =>
  typeof slots[key] === "number" && Number.isFinite(slots[key]) ? (slots[key] as number) : fallback;

export const slotStr = (slots: Record<string, unknown>, key: string, fallback: string): string =>
  typeof slots[key] === "string" && slots[key] ? (slots[key] as string) : fallback;

export const slotBool = (slots: Record<string, unknown>, key: string, fallback: boolean): boolean =>
  typeof slots[key] === "boolean" ? (slots[key] as boolean) : fallback;

export function slotArr<T>(slots: Record<string, unknown>, key: string, fallback: T[]): T[] {
  const value = slots[key];
  return Array.isArray(value) && value.length > 0 ? (value as T[]) : fallback;
}

export function SciencePanel({
  title,
  subject,
  badge,
  children,
}: {
  title: string;
  subject: Subject;
  badge?: string;
  children: ReactNode;
}) {
  return (
    <section className="sci" data-subject={subject}>
      <header className="sci-head">
        <span className="sci-dot" />
        <h3>{title}</h3>
        {badge ? <span className="sci-badge">{badge}</span> : null}
      </header>
      {children}
    </section>
  );
}

export function Control({
  label,
  value,
  min,
  max,
  step = 0.1,
  suffix = "",
  disabled,
  onChange,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  suffix?: string;
  disabled?: boolean;
  onChange: (v: number) => void;
}) {
  return (
    <label className="ctl">
      <span className="ctl-label">
        {label}
        <b>
          {Number.isInteger(value) ? value : value.toFixed(2)}
          {suffix}
        </b>
      </span>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        disabled={disabled}
        onChange={(e) => onChange(Number(e.target.value))}
      />
    </label>
  );
}

/**
 * Predict-observe-explain gate.
 *
 * The student commits to a prediction before they may run the sim. This is the
 * whole pedagogical point: a misconception only breaks if you've staked
 * something on it first.
 */
export function Predict({
  prompt,
  options,
  chosen,
  onChoose,
}: {
  prompt: string;
  options: { id: string; label: string }[];
  chosen: string | null;
  onChoose: (id: string) => void;
}) {
  return (
    <div className="predict">
      <p className="predict-q">{prompt}</p>
      <div className="predict-opts">
        {options.map((o) => (
          <button
            key={o.id}
            className={`predict-opt${chosen === o.id ? " is-chosen" : ""}`}
            onClick={() => onChoose(o.id)}
          >
            {o.label}
          </button>
        ))}
      </div>
    </div>
  );
}

export function Verdict({ correct, children }: { correct: boolean; children: ReactNode }) {
  return (
    <div className={`verdict ${correct ? "is-right" : "is-wrong"}`}>
      <strong>{correct ? "Your prediction held up." : "That's the misconception."}</strong>
      <p>{children}</p>
    </div>
  );
}
