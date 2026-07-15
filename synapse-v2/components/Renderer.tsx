"use client";

/**
 * The Tier B runtime.
 *
 * Recursive, one component per node type. Ported from GenUITestV2 and extended
 * with the two nodes that make Tier B more than a document: "science" (a real
 * sim embedded in a generated screen) and "computed"/"formulaChart" (model-
 * written formulas, evaluated by lib/expr.ts).
 *
 * Rule inherited from the PoC and worth keeping: an unknown node type degrades
 * to a visible placeholder. It never crashes the page.
 */

import { useMemo } from "react";
import type { UINode } from "@/lib/uispec";
import { evaluate } from "@/lib/expr";
import { SimSpec } from "@/lib/sim";
import { ScienceComponent } from "./science";
import GenerativeSim from "./science/GenerativeSim";

export type InputValues = Record<string, string | number>;

interface RenderCtx {
  values: InputValues;
  setValue: (id: string, value: string | number) => void;
  /** Bulk-set, for a sim sharing its sliders with the rest of the screen. */
  publishValues: (values: Record<string, number>) => void;
  onAction: (action: string, label: string) => void;
  onScienceInteraction: (action: string, values: Record<string, string | number | boolean>) => void;
}

const str = (v: unknown, fallback = ""): string =>
  typeof v === "string" ? v : typeof v === "number" ? String(v) : fallback;
const num = (v: unknown, fallback = 0): number =>
  typeof v === "number" && Number.isFinite(v) ? v : fallback;

/** Formula scope: every input id whose current value reads as a number. */
function numericScope(values: InputValues): Record<string, number> {
  const scope: Record<string, number> = {};
  for (const [k, v] of Object.entries(values)) {
    const n = typeof v === "number" ? v : Number(v);
    if (Number.isFinite(n)) scope[k] = n;
  }
  return scope;
}

export function RenderNode({ node, ctx }: { node: UINode; ctx: RenderCtx }) {
  if (!node || typeof node !== "object" || typeof node.type !== "string") {
    return <div className="g-unknown">Invalid node</div>;
  }

  const kids = Array.isArray(node.children) ? node.children : [];
  const children = kids.map((child, i) => <RenderNode key={i} node={child} ctx={ctx} />);

  switch (node.type) {
    case "column":
      return (
        <div className="g-column" style={{ gap: num(node.gap, 12) }}>
          {children}
        </div>
      );

    case "row":
      return (
        <div className="g-row" style={{ gap: num(node.gap, 12) }}>
          {children}
        </div>
      );

    case "card":
      return (
        <section className="g-card">
          {node.title ? <div className="g-card-title">{str(node.title)}</div> : null}
          <div className="g-column" style={{ gap: 10 }}>
            {children}
          </div>
        </section>
      );

    case "divider":
      return <hr className="g-divider" />;

    case "heading": {
      const level = num(node.level, 2);
      const Tag = (level === 1 ? "h2" : level === 3 ? "h4" : "h3") as "h2" | "h3" | "h4";
      return <Tag className="g-heading">{str(node.text)}</Tag>;
    }

    case "text":
      return <p className={`g-text${node.muted ? " is-muted" : ""}`}>{str(node.text)}</p>;

    case "callout":
      return (
        <div className={`callout is-${str(node.tone, "info")}`}>
          {node.title ? <strong>{str(node.title)}</strong> : null}
          <span>{str(node.text)}</span>
        </div>
      );

    case "badge":
      return <span className={`g-badge is-${str(node.tone, "info")}`}>{str(node.text)}</span>;

    case "stat":
      return (
        <div className="g-stat">
          <span className="g-stat-label">{str(node.label)}</span>
          <span className={`g-stat-value is-${str(node.tone, "neutral")}`}>
            {str(node.value)}
            {node.delta ? <em className="g-stat-delta">{str(node.delta)}</em> : null}
          </span>
        </div>
      );

    case "list": {
      const items = Array.isArray(node.items) ? node.items.map((i) => str(i)) : [];
      const Tag = node.ordered ? "ol" : "ul";
      return (
        <Tag className="g-list">
          {items.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </Tag>
      );
    }

    case "table": {
      const columns = Array.isArray(node.columns) ? node.columns.map((c) => str(c)) : [];
      const rows = Array.isArray(node.rows) ? (node.rows as unknown[]) : [];
      return (
        <div className="g-table-wrap">
          <table className="g-table">
            <thead>
              <tr>
                {columns.map((c, i) => (
                  <th key={i}>{c}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rows.map((row, i) => (
                <tr key={i}>
                  {(Array.isArray(row) ? row : []).map((cell, j) => (
                    <td key={j}>{str(cell)}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      );
    }

    case "progress": {
      const value = Math.max(0, Math.min(100, num(node.value)));
      return (
        <div className="g-progress">
          <span className="g-progress-label">
            {str(node.label)} <b>{value.toFixed(0)}%</b>
          </span>
          <div className="g-progress-track">
            <div className="g-progress-fill" style={{ width: `${value}%` }} />
          </div>
        </div>
      );
    }

    case "equation":
      return (
        <div className="g-equation">
          <code>{str(node.text, str(node.latex))}</code>
          {node.caption ? <span>{str(node.caption)}</span> : null}
        </div>
      );

    case "barChart": {
      const items = (Array.isArray(node.items) ? node.items : []) as {
        label?: unknown;
        value?: unknown;
        suffix?: unknown;
      }[];
      const max = Math.max(1, ...items.map((i) => Math.abs(num(i.value))));
      return (
        <figure className="g-chart">
          {node.title ? <figcaption>{str(node.title)}</figcaption> : null}
          {items.map((item, i) => (
            <div className="g-bar-row" key={i}>
              <span className="g-bar-label">{str(item.label)}</span>
              <div className="g-bar-track">
                <div className="g-bar-fill" style={{ width: `${(Math.abs(num(item.value)) / max) * 100}%` }} />
              </div>
              <span className="g-bar-value">
                {num(item.value)}
                {str(item.suffix)}
              </span>
            </div>
          ))}
        </figure>
      );
    }

    case "slider": {
      const id = str(node.id);
      const value = num(ctx.values[id], num(node.value));
      return (
        <label className="ctl">
          <span className="ctl-label">
            {str(node.label)}
            <b>
              {value}
              {str(node.suffix)}
            </b>
          </span>
          <input
            type="range"
            min={num(node.min)}
            max={num(node.max, 100)}
            step={num(node.step, 1)}
            value={value}
            onChange={(e) => ctx.setValue(id, Number(e.target.value))}
          />
        </label>
      );
    }

    case "input": {
      const id = str(node.id);
      return (
        <label className="ctl">
          <span className="ctl-label">{str(node.label)}</span>
          <input
            className="g-input"
            placeholder={str(node.placeholder)}
            value={str(ctx.values[id], str(node.value))}
            onChange={(e) => ctx.setValue(id, e.target.value)}
          />
        </label>
      );
    }

    case "select": {
      const id = str(node.id);
      const options = Array.isArray(node.options) ? node.options.map((o) => str(o)) : [];
      return (
        <label className="ctl">
          <span className="ctl-label">{str(node.label)}</span>
          <select
            className="g-input"
            value={str(ctx.values[id], str(node.value, options[0]))}
            onChange={(e) => ctx.setValue(id, e.target.value)}
          >
            {options.map((o, i) => (
              <option key={i} value={o}>
                {o}
              </option>
            ))}
          </select>
        </label>
      );
    }

    case "button":
      return (
        <button
          className={str(node.variant) === "secondary" ? "btn-secondary" : "btn-primary"}
          onClick={() => ctx.onAction(str(node.action, "pressed"), str(node.label))}
        >
          {str(node.label)}
        </button>
      );

    case "computed":
      return <Computed node={node} ctx={ctx} />;

    case "formulaChart":
      return <FormulaChart node={node} ctx={ctx} />;

    case "science":
      return (
        <ScienceComponent
          pattern={str(node.pattern)}
          slots={(node.slots ?? {}) as Record<string, unknown>}
          onInteraction={ctx.onScienceInteraction}
        />
      );

    case "sim":
      return <SimNode node={node} ctx={ctx} />;

    default:
      // Degrade visibly. A screen with one unknown node is still a useful screen.
      return <div className="g-unknown">Unsupported node: {node.type}</div>;
  }
}

/**
 * A model-designed experiment.
 *
 * Re-parsed here rather than trusted: the spec was validated server-side, but
 * this node arrives inside a free-form tree and a malformed one should cost a
 * placeholder, not the screen.
 */
function SimNode({ node, ctx }: { node: UINode; ctx: RenderCtx }) {
  const parsed = useMemo(() => SimSpec.safeParse(node.spec), [node.spec]);
  if (!parsed.success) {
    return (
      <div className="g-unknown">
        Generated simulation was malformed:{" "}
        {parsed.error.issues.map((i) => `${i.path.join(".")}: ${i.message}`).join("; ")}
      </div>
    );
  }
  return (
    <GenerativeSim
      spec={parsed.data}
      onInteraction={ctx.onScienceInteraction}
      onPublish={ctx.publishValues}
    />
  );
}

/** A model-written formula, recomputed on every input change. */
function Computed({ node, ctx }: { node: UINode; ctx: RenderCtx }) {
  const formula = str(node.formula);
  const result = useMemo(
    () => evaluate(formula, numericScope(ctx.values)),
    [formula, ctx.values],
  );

  if (!result.ok) {
    return (
      <div className="g-stat is-broken" title={formula}>
        <span className="g-stat-label">{str(node.label)}</span>
        <span className="g-stat-value">
          — <em className="g-formula-error">{result.error}</em>
        </span>
      </div>
    );
  }

  const precision = num(node.precision, 2);
  return (
    <div className="g-stat">
      <span className="g-stat-label">
        {str(node.label)}
        <code className="g-formula" title="The formula driving this value">
          {formula}
        </code>
      </span>
      <span className={`g-stat-value is-${str(node.tone, "neutral")}`}>
        {result.value.toFixed(precision)}
        {str(node.suffix)}
      </span>
    </div>
  );
}

/** Plots a formula as one variable sweeps a range. */
function FormulaChart({ node, ctx }: { node: UINode; ctx: RenderCtx }) {
  const formula = str(node.formula);
  const variable = str(node.variable);
  const min = num(node.min);
  const max = num(node.max, 10);
  const steps = Math.max(2, Math.min(120, num(node.steps, 60)));

  const series = useMemo(() => {
    const base = numericScope(ctx.values);
    const points: { x: number; y: number }[] = [];
    for (let i = 0; i <= steps; i++) {
      const x = min + ((max - min) * i) / steps;
      const result = evaluate(formula, { ...base, [variable]: x });
      if (result.ok) points.push({ x, y: result.value });
    }
    return points;
  }, [formula, variable, min, max, steps, ctx.values]);

  if (series.length < 2) {
    return <div className="g-unknown">Could not plot: {formula}</div>;
  }

  const W = 320;
  const H = 130;
  const ys = series.map((p) => p.y);
  const yMin = Math.min(...ys);
  const yMax = Math.max(...ys);
  const span = yMax - yMin || 1;

  const path = series
    .map((p, i) => {
      const x = ((p.x - min) / (max - min || 1)) * W;
      const y = H - 8 - ((p.y - yMin) / span) * (H - 20);
      return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");

  return (
    <figure className="graph">
      <figcaption>
        {str(node.title, formula)}
        <code className="g-formula">{formula}</code>
      </figcaption>
      <svg viewBox={`0 0 ${W} ${H}`} className="graph-svg" role="img" aria-label={str(node.title, formula)}>
        <line x1="0" y1={H - 6} x2={W} y2={H - 6} className="axis" />
        <line x1="0" y1="0" x2="0" y2={H} className="axis" />
        <path d={path} className="trace" fill="none" />
      </svg>
      <div className="graph-axes">
        <span>
          {variable} = {min}
        </span>
        <span>
          {yMin.toFixed(1)}–{yMax.toFixed(1)}
          {str(node.suffix)}
        </span>
        <span>{max}</span>
      </div>
    </figure>
  );
}

export function SpecRenderer({
  root,
  ctx,
}: {
  root: UINode;
  ctx: RenderCtx;
}) {
  return <RenderNode node={root} ctx={ctx} />;
}
