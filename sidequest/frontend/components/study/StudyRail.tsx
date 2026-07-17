"use client";

const STARTERS = [
  "Why does ice float?",
  "What happens when you mix an acid and a base?",
  "Show me how projectile motion works",
];

export function StudyRail({
  onPrompt,
  disabled,
}: {
  onPrompt: (prompt: string) => void;
  disabled: boolean;
}) {
  return (
    <aside className="hidden border-r px-5 py-7 xl:block" style={{ borderColor: "var(--rule)" }}>
      <div className="sticky top-0">
        <p className="study-kicker">AXIOM / STUDY STUDIO</p>
        <h1 className="mt-3 font-serif text-3xl leading-none">Make science stick.</h1>
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
      </div>
    </aside>
  );
}
