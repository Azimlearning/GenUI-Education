"use client";

/**
 * The runtime for a model-designed experiment.
 *
 * It knows nothing about osmosis, or forces, or bonding. It knows how to hold
 * state, step it with the model's formulas, and draw shapes whose coordinates
 * are expressions. Every experiment the model can imagine renders through this
 * one component — which is the whole point: the lab is authored per question,
 * not chosen from a shelf.
 */

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { evaluate } from "@/lib/expr";
import { initialState, resolveOutcome, type SceneNode, type SimSpec } from "@/lib/sim";
import { Predict, Verdict } from "./shared";

type Phase = "predict" | "running" | "done";

interface Props {
  spec: SimSpec;
  onInteraction?: (action: string, values: Record<string, string | number | boolean>) => void;
  /**
   * Publishes the sim's slider values to the surrounding screen, so a chart or
   * a computed readout next to the sim can read them by id and track the
   * student's hand. Without it the model's natural instinct — reference
   * `length` in a chart beside the pendulum — renders as an error.
   */
  onPublish?: (values: Record<string, number>) => void;
}

export default function GenerativeSim({ spec, onInteraction, onPublish }: Props) {
  const [params, setParams] = useState<Record<string, number>>(() =>
    Object.fromEntries(spec.params.map((p) => [p.id, p.value])),
  );
  const [state, setState] = useState<Record<string, number>>(() =>
    initialState(spec, Object.fromEntries(spec.params.map((p) => [p.id, p.value]))),
  );
  const [t, setT] = useState(0);
  const [phase, setPhase] = useState<Phase>(spec.predict ? "predict" : "running");
  const [guess, setGuess] = useState<number | null>(null);
  const [broken, setBroken] = useState<string | null>(null);

  // Share the sliders with the surrounding screen.
  useEffect(() => {
    onPublish?.(params);
    // onPublish is a fresh closure each render; params is the real trigger.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [params]);

  /** params + state + t, before derived. The base every formula sees. */
  const baseScope = useMemo(
    () => ({ ...params, ...state, t, dt: 1 / 60 }),
    [params, state, t],
  );

  /** Derived resolve in order, each able to use the ones before it. */
  const scope = useMemo(() => {
    const s: Record<string, number> = { ...baseScope };
    for (const [key, formula] of Object.entries(spec.derived)) {
      const r = evaluate(formula, s);
      s[key] = r.ok ? r.value : 0;
    }
    return s;
  }, [baseScope, spec.derived]);

  /** What the physics says, for the student's current values. Not the model's opinion. */
  const outcome = useMemo(() => resolveOutcome(spec, scope), [spec, scope]);

  const reset = useCallback(() => {
    setState(initialState(spec, params));
    setT(0);
    setPhase(spec.predict ? "predict" : "running");
    setGuess(null);
  }, [spec, params]);

  // The integration loop. Fixed step so the physics is frame-rate independent.
  const raf = useRef<number | null>(null);
  const live = useRef({ state: {} as Record<string, number>, t: 0 });

  useEffect(() => {
    if (phase !== "running") return;
    live.current = { state: initialState(spec, params), t: 0 };
    const DT = 1 / 60;
    let acc = 0;
    let last: number | null = null;
    let failed: string | null = null;

    const frame = (ts: number) => {
      if (last === null) last = ts;
      acc += Math.min(0.1, (ts - last) / 1000);
      last = ts;

      while (acc >= DT) {
        const cur = live.current;
        const s: Record<string, number> = { ...params, ...cur.state, t: cur.t, dt: DT };
        for (const [key, formula] of Object.entries(spec.derived)) {
          const r = evaluate(formula, s);
          s[key] = r.ok ? r.value : 0;
        }

        // Step reads the whole pre-step scope, so updates are simultaneous
        // rather than order-dependent — v can use x and x can use v.
        const next: Record<string, number> = { ...cur.state };
        for (const [key, formula] of Object.entries(spec.step)) {
          const r = evaluate(formula, s);
          if (!r.ok) {
            failed ??= `${key}: ${r.error}`;
          } else {
            next[key] = r.value;
          }
        }

        live.current = { state: next, t: cur.t + DT };
        acc -= DT;
      }

      setState({ ...live.current.state });
      setT(live.current.t);

      if (failed) {
        setBroken(failed);
        setPhase("done");
        return;
      }
      if (live.current.t >= spec.duration) setPhase("done");
      else raf.current = requestAnimationFrame(frame);
    };

    raf.current = requestAnimationFrame(frame);
    return () => {
      if (raf.current !== null) cancelAnimationFrame(raf.current);
    };
  }, [phase, params, spec]);

  const run = () => {
    if (spec.predict && guess === null) return;
    setPhase("running");
    const values: Record<string, string | number | boolean> = { ...params };
    if (spec.predict && guess !== null) {
      values.predicted = spec.predict.options[guess].label;
      values.actual = outcome !== null ? spec.predict.options[outcome].label : "undetermined";
      values.correct = guess === outcome;
    }
    onInteraction?.(`ran the ${spec.title} simulation`, values);
  };

  return (
    <section className="sci" data-subject="generated">
      <header className="sci-head">
        <span className="sci-dot" />
        <h3>{spec.title}</h3>
        <span className="sci-badge">designed for this question</span>
      </header>

      <Stage spec={spec} scope={scope} />
      {spec.caption ? <p className="sim-caption">{spec.caption}</p> : null}

      {spec.readouts.length ? (
        <div className="readouts">
          {spec.readouts.map((r, i) => {
            const result = evaluate(r.formula, scope);
            return (
              <div className="readout" key={i}>
                <span className="readout-label">{r.label}</span>
                <span className="readout-value">
                  {result.ok ? result.value.toFixed(r.precision ?? 2) : "—"}
                  {r.unit ? <em>{r.unit}</em> : null}
                </span>
              </div>
            );
          })}
        </div>
      ) : null}

      {spec.params.length ? (
        <div className="sci-controls">
          {spec.params.map((p) => (
            <label className="ctl" key={p.id}>
              <span className="ctl-label">
                {p.label}
                <b>
                  {params[p.id]}
                  {p.unit ?? ""}
                </b>
              </span>
              <input
                type="range"
                min={p.min}
                max={p.max}
                step={p.step ?? (p.max - p.min) / 100}
                value={params[p.id]}
                disabled={phase === "running"}
                onChange={(e) => {
                  setParams((prev) => ({ ...prev, [p.id]: Number(e.target.value) }));
                  reset();
                }}
              />
            </label>
          ))}
        </div>
      ) : null}

      {broken ? (
        <div className="callout is-danger">
          This generated simulation has a broken formula (<code>{broken}</code>). The pipeline panel
          shows what was built.
        </div>
      ) : null}

      {phase === "predict" && spec.predict ? (
        <>
          <Predict
            prompt={spec.predict.prompt}
            options={spec.predict.options.map((o, i) => ({ id: String(i), label: o.label }))}
            chosen={guess === null ? null : String(guess)}
            onChoose={(id) => setGuess(Number(id))}
          />
          <button className="btn-primary" disabled={guess === null} onClick={run}>
            {guess === null ? "Predict first, then run" : "Run the experiment"}
          </button>
        </>
      ) : null}

      {phase === "running" ? <p className="sci-status">Running…</p> : null}

      {phase === "done" && spec.predict ? (
        <>
          <Verdict correct={guess === outcome}>
            {outcome === null
              ? "The conditions you set don't match any of the predicted outcomes — try moving a slider further."
              : spec.predict.options[outcome].explain}
          </Verdict>
          <button className="btn-secondary" onClick={reset}>
            Change something and try again
          </button>
        </>
      ) : null}

      {phase === "done" && !spec.predict ? (
        <button className="btn-secondary" onClick={reset}>
          Run again
        </button>
      ) : null}
    </section>
  );
}

/* ------------------------------------------------------------------ stage */

function Stage({ spec, scope }: { spec: SimSpec; scope: Record<string, number> }) {
  const nodes: React.ReactNode[] = [];

  spec.scene.forEach((node, i) => {
    if (node.repeat) {
      for (let k = 0; k < node.repeat.count; k++) {
        nodes.push(
          <Shape
            key={`${i}-${k}`}
            node={node}
            scope={{ ...scope, [node.repeat.as]: k }}
            id={`${i}-${k}`}
          />,
        );
      }
    } else {
      nodes.push(<Shape key={i} node={node} scope={scope} id={String(i)} />);
    }
  });

  return (
    <div className="sim-stage">
      <svg
        viewBox={`0 0 ${spec.width} ${spec.height}`}
        className="sim-svg"
        role="img"
        aria-label={spec.title}
      >
        <defs>
          <marker
            id="sim-arrow"
            viewBox="0 0 10 10"
            refX="9"
            refY="5"
            markerWidth="4"
            markerHeight="4"
            orient="auto-start-reverse"
          >
            <path d="M 0 0 L 10 5 L 0 10 z" fill="currentColor" />
          </marker>
        </defs>
        {nodes}
      </svg>
    </div>
  );
}

function Shape({
  node,
  scope,
  id,
}: {
  node: SceneNode;
  scope: Record<string, number>;
  id: string;
}) {
  // A formula that fails resolves to 0 rather than throwing. One bad shape
  // should cost you that shape, not the whole lab.
  const f = (src: string | undefined, fallback = 0): number => {
    if (typeof src !== "string") return fallback;
    const r = evaluate(src, scope);
    return r.ok ? r.value : fallback;
  };

  const fill = node.fill ? `var(--${node.fill})` : "none";
  const stroke = node.stroke ? `var(--${node.stroke})` : "none";
  const opacity = node.opacity ? f(node.opacity, 1) : 1;

  switch (node.shape) {
    case "rect":
      return (
        <rect
          x={f(node.x)}
          y={f(node.y)}
          width={Math.max(0, f(node.w))}
          height={Math.max(0, f(node.h))}
          rx={f(node.rx)}
          fill={fill}
          opacity={opacity}
        />
      );

    case "circle":
      return (
        <circle
          cx={f(node.cx)}
          cy={f(node.cy)}
          r={Math.max(0, f(node.r, 1))}
          fill={fill}
          opacity={opacity}
        />
      );

    case "line":
      return (
        <line
          x1={f(node.x1)}
          y1={f(node.y1)}
          x2={f(node.x2)}
          y2={f(node.y2)}
          stroke={stroke}
          strokeWidth={f(node.width, 1)}
          strokeDasharray={node.dash ? "3 3" : undefined}
          opacity={opacity}
        />
      );

    case "arrow":
      return (
        <line
          x1={f(node.x1)}
          y1={f(node.y1)}
          x2={f(node.x2)}
          y2={f(node.y2)}
          stroke={stroke}
          strokeWidth={f(node.width, 1.5)}
          markerEnd="url(#sim-arrow)"
          style={{ color: stroke }}
          opacity={opacity}
        />
      );

    case "text":
      return (
        <text
          x={f(node.x)}
          y={f(node.y)}
          fontSize={f(node.size, 6)}
          fill={node.fill ? `var(--${node.fill})` : "var(--text)"}
          textAnchor={node.anchor ?? "start"}
          opacity={opacity}
        >
          {node.text}
        </text>
      );

    case "path":
      return <path d={node.d} fill={fill} stroke={stroke} opacity={opacity} key={id} />;

    default:
      return null;
  }
}
