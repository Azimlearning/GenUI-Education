"use client";

/**
 * The shell.
 *
 * ask -> brief (+ any contradiction) -> confirm -> build -> interact -> guide
 *
 * The confirm gate is the product decision that separates this from a chatbot:
 * we say what we're about to build, and if the student's own wording contradicts
 * the science we name that contradiction BEFORE the lab loads. They press the
 * button knowing what's coming, and knowing they were wrong.
 */

import { useCallback, useRef, useState } from "react";
import {
  type BriefEvent,
  type PipelineStepEvent,
  type Tier,
  type Turn,
  TIER_LABELS,
} from "@/lib/contract";
import type { UISpec } from "@/lib/uispec";
import { streamPipeline } from "@/lib/client";
import PipelinePanel from "@/components/PipelinePanel";
import { SpecRenderer, type InputValues } from "@/components/Renderer";
import { ScienceComponent } from "@/components/science";
import Sandbox from "@/components/Sandbox";

const EXAMPLES = [
  "Osmosis is when water moves to where there is more water, right?",
  "Why doesn't a heavy box move when I push it?",
  "Is HCl ionic or covalent?",
  "Build me a lab for total internal reflection in a fibre optic cable",
];

type Stage = "idle" | "briefing" | "gated" | "building" | "ready";

interface Built {
  tier: Tier;
  fellBackFrom: Tier | null;
  component?: { pattern: string; slots: Record<string, unknown> };
  spec?: UISpec;
  html?: string;
}

export default function Home() {
  const [prompt, setPrompt] = useState("");
  const [asked, setAsked] = useState("");
  const [stage, setStage] = useState<Stage>("idle");
  const [steps, setSteps] = useState<PipelineStepEvent[]>([]);
  const [brief, setBrief] = useState<BriefEvent | null>(null);
  const [built, setBuilt] = useState<Built | null>(null);
  const [guidance, setGuidance] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [values, setValues] = useState<InputValues>({});
  const [streamingHtml, setStreamingHtml] = useState("");
  const [ms, setMs] = useState<number | null>(null);

  const history = useRef<Turn[]>([]);
  const abort = useRef<AbortController | null>(null);

  const reset = () => {
    abort.current?.abort();
    setSteps([]);
    setBrief(null);
    setBuilt(null);
    setGuidance([]);
    setError(null);
    setValues({});
    setStreamingHtml("");
    setMs(null);
  };

  /** One stream, one place that interprets events. */
  const run = useCallback(
    async (
      body: Parameters<typeof streamPipeline>[0],
      opts: { building: boolean },
    ) => {
      abort.current?.abort();
      const controller = new AbortController();
      abort.current = controller;

      let html = "";
      setStage(opts.building ? "building" : "briefing");
      setError(null);

      try {
        await streamPipeline(
          body,
          (event) => {
            switch (event.type) {
              case "pipeline_step":
                setSteps((prev) => [...prev, event]);
                break;

              case "brief":
                setBrief(event);
                break;

              case "component":
                setBuilt({ tier: "A", fellBackFrom: null, component: { pattern: event.pattern, slots: event.slots } });
                break;

              case "ui_spec":
                setBuilt({ tier: "B", fellBackFrom: null, spec: event.spec as UISpec });
                setValues({});
                break;

              case "generated_code":
                if (event.done) {
                  setBuilt({ tier: "C", fellBackFrom: null, html });
                } else {
                  html += event.chunk;
                  setStreamingHtml(html);
                }
                break;

              case "guidance":
                setGuidance((prev) => [...prev, event.text]);
                break;

              case "done":
                setMs(event.ms);
                if (event.fell_back_from) {
                  setBuilt((prev) => (prev ? { ...prev, fellBackFrom: event.fell_back_from } : prev));
                }
                break;

              case "error":
                setError(event.message);
                break;
            }
          },
          controller.signal,
        );
      } catch (err) {
        if (!controller.signal.aborted) {
          setError(err instanceof Error ? err.message : "Something went wrong");
        }
      }
    },
    [],
  );

  const ask = async () => {
    const text = prompt.trim();
    if (!text) return;
    reset();
    setAsked(text);
    setPrompt("");
    await run({ prompt: text, history: history.current, confirmed: false, plan: null, interaction: null }, { building: false });
    // The stream decides where we land: if the generator ran (explicit request),
    // something got built; otherwise we're at the gate.
    setStage((prev) => (prev === "building" ? "ready" : "gated"));
  };

  const generate = async () => {
    if (!brief) return;
    setStage("building");
    setStreamingHtml("");
    await run(
      {
        prompt: asked,
        history: history.current,
        confirmed: true,
        plan: { tier: brief.tier, pattern: null, title: brief.title, description: brief.description },
        interaction: null,
      },
      { building: true },
    );
    setStage("ready");
  };

  const onInteraction = useCallback(
    async (action: string, vals: Record<string, string | number | boolean>) => {
      const turns: Turn[] = [
        ...history.current,
        { role: "user", content: asked },
        { role: "assistant", content: `Built: ${brief?.title ?? "an experiment"}` },
      ];
      history.current = turns.slice(-6);

      await run(
        {
          prompt: asked,
          history: history.current,
          confirmed: false,
          plan: null,
          interaction: { source: built?.tier === "C" ? "sandbox" : "component", action, values: vals },
        },
        { building: false },
      );
      setStage("ready");
    },
    [asked, brief, built, run],
  );

  const onSpecAction = useCallback(
    (action: string) => {
      const vals: Record<string, string | number | boolean> = {};
      for (const [k, v] of Object.entries(values)) vals[k] = v;
      void onInteraction(action, vals);
    },
    [values, onInteraction],
  );

  const busy = stage === "briefing" || stage === "building";

  return (
    <main className="app">
      <header className="app-header">
        <div>
          <h1>
            Synapse <span className="wordmark">v2</span>
          </h1>
          <p className="muted">
            Ask a Form 4–5 science question. Get a lab you can run, not a wall of text.
          </p>
        </div>
        {ms !== null ? <span className="timing">{(ms / 1000).toFixed(1)}s</span> : null}
      </header>

      <div className="prompt-bar">
        <input
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && !busy && ask()}
          placeholder="e.g. Osmosis is when water moves to where there is more water, right?"
          disabled={busy}
          aria-label="Your question"
        />
        <button className="btn-primary" onClick={ask} disabled={busy || !prompt.trim()}>
          {busy ? "Thinking…" : "Ask"}
        </button>
      </div>

      {stage === "idle" ? (
        <div className="examples">
          {EXAMPLES.map((e) => (
            <button key={e} className="example" onClick={() => setPrompt(e)}>
              {e}
            </button>
          ))}
        </div>
      ) : null}

      {error ? <div className="callout is-danger">{error}</div> : null}

      <div className="stage">
        <div className="stage-main">
          {asked && stage !== "idle" ? <p className="asked">“{asked}”</p> : null}

          {brief ? (
            <section className="brief">
              {brief.contradiction ? (
                <div className="contradiction">
                  <span className="contradiction-tag">Before we build this</span>
                  <p className="contradiction-claim">
                    You said: <em>{brief.contradiction.student_claim}</em>
                  </p>
                  <p className="contradiction-fix">{brief.contradiction.correction}</p>
                </div>
              ) : null}

              <h2>{brief.title}</h2>
              <p>{brief.description}</p>

              {brief.manipulables.length ? (
                <ul className="manipulables">
                  {brief.manipulables.map((m, i) => (
                    <li key={i}>{m}</li>
                  ))}
                </ul>
              ) : null}

              <footer className="brief-foot">
                <span className="tier-tag">{TIER_LABELS[brief.tier]}</span>
                {stage === "gated" ? (
                  <button className="btn-primary" onClick={generate}>
                    Generate Experiment
                  </button>
                ) : null}
              </footer>
            </section>
          ) : null}

          {stage === "building" && brief?.tier === "C" ? (
            <Sandbox html={streamingHtml} streaming onInteraction={onInteraction} />
          ) : null}

          {stage === "building" && brief?.tier !== "C" && !built ? (
            <div className="building">
              <span className="pulse" />
              Building your lab…
            </div>
          ) : null}

          {built?.fellBackFrom ? (
            <div className="callout is-warning">
              Tier {built.fellBackFrom} didn't land, so this is the tier {built.tier} version. The
              fallback is deliberate: you always get something that works.
            </div>
          ) : null}

          {built?.component ? (
            <ScienceComponent
              pattern={built.component.pattern}
              slots={built.component.slots}
              onInteraction={onInteraction}
            />
          ) : null}

          {built?.spec ? (
            <div className="spec">
              <SpecRenderer
                root={built.spec.root}
                ctx={{
                  values,
                  setValue: (id, value) => setValues((prev) => ({ ...prev, [id]: value })),
                  onAction: onSpecAction,
                  onScienceInteraction: onInteraction,
                }}
              />
            </div>
          ) : null}

          {built?.html ? (
            <Sandbox html={built.html} streaming={false} onInteraction={onInteraction} />
          ) : null}

          {guidance.map((text, i) => (
            <div className="guidance" key={i}>
              <span className="guidance-tag">Guide</span>
              <p>{text}</p>
            </div>
          ))}
        </div>

        <PipelinePanel steps={steps} />
      </div>
    </main>
  );
}
