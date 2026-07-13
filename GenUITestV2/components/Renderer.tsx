"use client";

import type { UINode } from "@/lib/uispec";

export type InputValues = Record<string, string | number>;

interface RenderCtx {
  values: InputValues;
  setValue: (id: string, value: string | number) => void;
  onAction: (action: string, label: string) => void;
}

interface NodeProps {
  node: UINode;
  ctx: RenderCtx;
}

function Children({ node, ctx }: NodeProps) {
  if (!Array.isArray(node.children)) return null;
  return (
    <>
      {node.children.map((child, i) => (
        <RenderNode key={i} node={child} ctx={ctx} />
      ))}
    </>
  );
}

const str = (v: unknown, fallback = ""): string =>
  typeof v === "string" ? v : typeof v === "number" ? String(v) : fallback;
const num = (v: unknown, fallback = 0): number =>
  typeof v === "number" && Number.isFinite(v) ? v : fallback;

export function RenderNode({ node, ctx }: NodeProps) {
  if (!node || typeof node !== "object" || typeof node.type !== "string") {
    return <div className="g-unknown">Invalid node</div>;
  }

  switch (node.type) {
    case "column":
      return (
        <div className="g-column" style={{ gap: num(node.gap, 12) }}>
          <Children node={node} ctx={ctx} />
        </div>
      );

    case "row":
      return (
        <div className="g-row" style={{ gap: num(node.gap, 12) }}>
          <Children node={node} ctx={ctx} />
        </div>
      );

    case "card":
      return (
        <section className="g-card">
          {node.title ? <div className="g-card-title">{str(node.title)}</div> : null}
          <div className="g-column" style={{ gap: 10 }}>
            <Children node={node} ctx={ctx} />
          </div>
        </section>
      );

    case "divider":
      return <hr className="g-divider" />;

    case "heading": {
      const level = num(node.level, 2);
      const Tag = level === 1 ? "h1" : level === 3 ? "h3" : "h2";
      return <Tag className={`g-heading g-h${level}`}>{str(node.text)}</Tag>;
    }

    case "text":
      return <p className={node.muted ? "g-text g-muted" : "g-text"}>{str(node.text)}</p>;

    case "callout": {
      const tone = str(node.tone, "info");
      return (
        <div className={`g-callout g-tone-${tone}`}>
          {node.title ? <div className="g-callout-title">{str(node.title)}</div> : null}
          <div>{str(node.text)}</div>
        </div>
      );
    }

    case "badge":
      return <span className={`g-badge g-tone-${str(node.tone, "info")}`}>{str(node.text)}</span>;

    case "stat": {
      const tone = str(node.tone, "neutral");
      return (
        <div className="g-stat">
          <div className="g-stat-label">{str(node.label)}</div>
          <div className="g-stat-value">{str(node.value)}</div>
          {node.delta ? <div className={`g-stat-delta g-tone-${tone}`}>{str(node.delta)}</div> : null}
        </div>
      );
    }

    case "list": {
      const items = Array.isArray(node.items) ? node.items.map((i) => str(i)) : [];
      const ListTag = node.ordered ? "ol" : "ul";
      return (
        <ListTag className="g-list">
          {items.map((item, i) => (
            <li key={i}>{item}</li>
          ))}
        </ListTag>
      );
    }

    case "table": {
      const columns = Array.isArray(node.columns) ? node.columns.map((c) => str(c)) : [];
      const rows = Array.isArray(node.rows) ? node.rows : [];
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
              {rows.map((row, ri) => (
                <tr key={ri}>
                  {(Array.isArray(row) ? row : []).map((cell, ci) => (
                    <td key={ci}>{str(cell)}</td>
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
          <div className="g-progress-head">
            <span>{str(node.label)}</span>
            <span className="g-muted">{value}%</span>
          </div>
          <div className="g-progress-track">
            <div className="g-progress-fill" style={{ width: `${value}%` }} />
          </div>
        </div>
      );
    }

    case "barChart": {
      const items = (Array.isArray(node.items) ? node.items : []).filter(
        (i): i is { label?: unknown; value?: unknown; suffix?: unknown } =>
          !!i && typeof i === "object",
      );
      const max = Math.max(...items.map((i) => num(i.value)), 1);
      return (
        <div className="g-chart">
          {node.title ? <div className="g-chart-title">{str(node.title)}</div> : null}
          {items.map((item, i) => (
            <div key={i} className="g-bar-row">
              <div className="g-bar-label">{str(item.label)}</div>
              <div className="g-bar-track">
                <div
                  className="g-bar-fill"
                  style={{ width: `${(num(item.value) / max) * 100}%` }}
                />
              </div>
              <div className="g-bar-value">
                {num(item.value).toLocaleString()}
                {str(item.suffix)}
              </div>
            </div>
          ))}
        </div>
      );
    }

    case "slider": {
      const id = str(node.id);
      const min = num(node.min, 0);
      const max = num(node.max, 100);
      const current = num(ctx.values[id], num(node.value, min));
      return (
        <div className="g-field">
          <div className="g-progress-head">
            <label htmlFor={id}>{str(node.label)}</label>
            <span className="g-slider-value">
              {current.toLocaleString()}
              {str(node.suffix)}
            </span>
          </div>
          <input
            id={id}
            type="range"
            min={min}
            max={max}
            step={num(node.step, 1)}
            value={current}
            onChange={(e) => ctx.setValue(id, Number(e.target.value))}
          />
        </div>
      );
    }

    case "input": {
      const id = str(node.id);
      const current = ctx.values[id] ?? str(node.value);
      return (
        <div className="g-field">
          <label htmlFor={id}>{str(node.label)}</label>
          <input
            id={id}
            type="text"
            placeholder={str(node.placeholder)}
            value={String(current)}
            onChange={(e) => ctx.setValue(id, e.target.value)}
          />
        </div>
      );
    }

    case "select": {
      const id = str(node.id);
      const options = Array.isArray(node.options) ? node.options.map((o) => str(o)) : [];
      const current = str(ctx.values[id] ?? node.value, options[0] ?? "");
      return (
        <div className="g-field">
          <label htmlFor={id}>{str(node.label)}</label>
          <select id={id} value={current} onChange={(e) => ctx.setValue(id, e.target.value)}>
            {options.map((o, i) => (
              <option key={i} value={o}>
                {o}
              </option>
            ))}
          </select>
        </div>
      );
    }

    case "button": {
      const variant = str(node.variant, "primary");
      const label = str(node.label, "Submit");
      return (
        <button
          className={`g-button g-button-${variant}`}
          onClick={() => ctx.onAction(str(node.action, label), label)}
        >
          {label}
        </button>
      );
    }

    default:
      return <div className="g-unknown">Unknown component type: “{node.type}”</div>;
  }
}
