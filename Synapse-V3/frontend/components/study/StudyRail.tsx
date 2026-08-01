"use client";

import type { SavedLab } from "@/lib/labLibrary";

const STARTERS = [
  "Why does ice float?",
  "What happens when you mix an acid and a base?",
  "Show me how projectile motion works",
];

export function StudyRail({
  onPrompt,
  disabled,
  savedLabs,
  onOpenSaved,
  onDeleteSaved,
}: {
  onPrompt: (prompt: string) => void;
  disabled: boolean;
  savedLabs: SavedLab[];
  onOpenSaved: (lab: SavedLab) => void;
  onDeleteSaved: (id: string) => void;
}) {
  return (
    <aside className="hidden border-r px-5 py-7 xl:block" style={{ borderColor: "var(--rule)" }}>
      <div className="sticky top-0">
        <h1 className="font-serif text-3xl leading-none">Make science stick.</h1>
        <p className="mt-3 text-sm leading-relaxed" style={{ color: "var(--ink-dim)" }}>
          Start with a question, then test the idea in your lab pane.
        </p>

        <section className="study-card mt-8 p-4">
          <p className="study-kicker">TODAY&apos;S FLOW</p>
          <ol className="mt-4 space-y-4 text-sm">
            <li className="flex gap-3"><span className="study-step">1</span><span><b>Ask</b><br /><em>Start with the thing that feels fuzzy.</em></span></li>
            <li className="flex gap-3"><span className="study-step">2</span><span><b>See the idea</b><br /><em>Keep the explanation short and useful.</em></span></li>
            <li className="flex gap-3"><span className="study-step">3</span><span><b>Try it</b><br /><em>Use the lab, change a variable, notice the result.</em></span></li>
          </ol>
        </section>

        <section className="mt-8">
          <p className="study-kicker">QUICK STARTS</p>
          <div className="mt-3 space-y-2">
            {STARTERS.map((prompt) => (
              <button
                key={prompt}
                type="button"
                disabled={disabled}
                onClick={() => onPrompt(prompt)}
                className="study-starter w-full text-left disabled:opacity-40"
              >
                {prompt}
              </button>
            ))}
          </div>
        </section>

        {savedLabs.length > 0 ? (
          <section className="mt-8">
            <p className="study-kicker">SAVED LABS</p>
            <div className="mt-3 space-y-2">
              {savedLabs.map((lab) => (
                <div key={lab.id} className="study-starter flex w-full items-center gap-2">
                  <button
                    type="button"
                    onClick={() => onOpenSaved(lab)}
                    className="min-w-0 flex-1 text-left"
                    title={lab.question || lab.title}
                  >
                    <span className="block truncate font-semibold" style={{ color: "var(--ink)" }}>
                      {lab.title}
                    </span>
                    {lab.meta ? (
                      <span className="mt-0.5 block text-[11px] capitalize" style={{ color: "var(--ink-faint)" }}>
                        {lab.meta.intent.domain.replace("_", " ")} · {lab.meta.intent.artifact_type.replace(/_/g, " ")}
                      </span>
                    ) : null}
                  </button>
                  <button
                    type="button"
                    onClick={() => onDeleteSaved(lab.id)}
                    aria-label={`Delete saved lab: ${lab.title}`}
                    className="shrink-0 rounded-full px-1.5 text-base leading-none"
                    style={{ color: "var(--ink-faint)" }}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </section>
        ) : null}
      </div>
    </aside>
  );
}
