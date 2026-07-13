# Generative UI — Full Research Analysis

> **Date:** 2026-07-06 · **Author:** research pass by Claude Code for Team EduNova
> **Purpose:** Establish the state of the art in Generative UI (GenUI), map every major
> implementation and protocol, identify the open gaps, and define the technical path from the
> current Synapse proof-of-concept (constrained component composition) to a **fully generative
> UI output**.
>
> Every factual claim in this document carries a reference. Vendor self-reported claims are
> explicitly marked as such. All sources were accessed 2026-07-06.

---

## 1. Problem statement

Most AI chat products render every answer in one fixed form: a markdown text stream. The output
*content* adapts to the query; the output *form* does not. A recipe, a physics explanation, a
budget comparison, and an itinerary all arrive as the same wall of text.

**Generative UI** is the counter-thesis: the model should decide not only *what* to say but *how
to present it* — generating (or assembling) the interface itself per response, so the form fits
the content: a chart for data, a simulator for a physical system, a form for a decision, a game
for practice.

This is now a validated research direction, not a vibe:

- Google Research's blind evaluation ranked generated interfaces at **ELO 1736.2** — preferred
  over every other response format (raw text, markdown, standard LLM output) except pages built
  by human experts [[G1]](#references), [[G2]](#references).
- The independent academic work "Generative Interfaces for Language Models" measured **up to 72%
  improvement in human preference** for generative interfaces over conversational (chat) output
  across diverse tasks [[A1]](#references).

---

## 2. Taxonomy: the three levels of Generative UI

Every shipping system falls on a three-level ladder. The levels trade **expressiveness** against
**speed, safety, and reliability**. This taxonomy is synthesized from the systems surveyed in
§3–§4; the level names are ours.

### Level 1 — Tool-call → pre-built component (constrained composition)

The model selects a component from a fixed catalog and fills its props. The client maps a type
tag to a real component and hydrates it.

- **Canonical implementation:** Vercel AI SDK `streamUI` / RSC generative UI — tool calls are
  mapped to React Server Components streamed to the client [[V1]](#references), [[V2]](#references).
- **Properties:** fastest, safest, pixel-perfect, domain-faithful. The model can only express
  what the catalog anticipated.
- **This is what Synapse does today** (typed `{pattern, props, meta}` blocks over SSE; backend
  never generates UI from scratch — Synapse constraint D-01).

### Level 2 — Declarative UI specification (DSL / UI-as-data)

The model generates a *description* of an arbitrary novel interface — layout tree, inputs,
charts, buttons, actions — as structured data. A runtime renders it with native components.

- **Canonical implementations:**
  - **Thesys C1** — an OpenAI-compatible API that returns a JSON-based UI DSL instead of text;
    the React SDK (`<C1Component>`, `<C1Chat>`) renders it and routes form submissions back to
    the model as tool calls [[T1]](#references), [[T2]](#references).
  - **Google A2UI** — an open protocol where agents "speak UI" by emitting declarative JSON
    specs, rendered natively by Angular/Flutter/Lit clients. Security is the design center:
    **UI is data, not code**, so no arbitrary code executes [[P3]](#references), [[P4]](#references).
  - **OpenUI (Thesys, open source)** — a compact streaming-first UI language + React runtime;
    the project claims ~**67% better token efficiency than JSON** for the same UI (vendor
    claim, unverified independently) [[T3]](#references).
- **Properties:** novel screens from a bounded vocabulary; streams progressively; cannot emit
  broken/malicious code; but capped at the renderer's component vocabulary — it cannot invent a
  new *kind* of interactive (e.g., a bespoke physics sandbox).

### Level 3 — Fully generative code (the model writes the interface)

The model writes actual executable UI code (self-contained HTML/JS, or JSX) per response,
rendered in a sandbox.

- **Canonical implementations:**
  - **Google Gemini "Dynamic View" / "Visual Layout"** — Gemini 3 Pro designs and codes a fully
    customized interactive response per prompt, shipped in the Gemini app and Google Search AI
    Mode [[G1]](#references), [[G3]](#references).
  - **Claude Artifacts** (Anthropic) — generated HTML/React rendered in an isolated pane;
    open-source re-implementations exist (see §4).
- **Properties:** unbounded expressiveness — bespoke simulations, tools, games for any prompt.
  Costs: latency (Google reports "a minute or more" [[G1]](#references)), occasional factual/code
  errors, and a hard sandboxing requirement.

**Key architectural insight:** these are not competing philosophies but tiers of one system. The
strongest products escalate: Level 1 when a catalog component fits (fast, faithful), Level 2/3
when nothing fits (expressive). Google's own stack spans the ladder (A2UI at Level 2, Dynamic
View at Level 3).

---

## 3. Primary research literature

### 3.1 "Generative UI: LLMs are Effective UI Generators" (Google, arXiv 2604.09577)

The paper behind Gemini's Dynamic View [[G2]](#references), with the companion Google Research
blog post [[G1]](#references) and project site [[G4]](#references).

**Architecture (as disclosed):** a frontier model (Gemini 3 Pro) plus three load-bearing
components:

1. **Tool access** — image generation and web search, so generated pages can include real
   assets and grounded facts [[G1]](#references).
2. **Detailed system instructions** — covering the goal, planning steps, worked examples,
   technical/formatting specifications, tool manuals, and explicit guidance for avoiding
   known common mistakes [[G1]](#references).
3. **Post-processors** — automated repair of "potential common issues" in generated output
   before rendering [[G1]](#references).

**Evaluation:** the paper introduces **PAGEN**, a dataset of expert-crafted web pages as a
gold-standard comparison set [[G2]](#references). Findings:

- Human evaluators **overwhelmingly prefer** generated UIs to markdown text [[G2]](#references).
- Generated UIs reach **approximate parity with human expert pages in ~half of test cases**,
  and remain below experts overall [[G2]](#references).
- Blind-ranking ELO: generative UI **1736.2**, second only to human experts, with a
  "substantial gap" down to standard LLM output / markdown / raw text [[G1]](#references).
- The capability is **emergent**: quality jumps substantially with newer models — older models
  cannot do this reliably at all [[G2]](#references). Performance "strongly depends on the
  underlying model" [[G1]](#references).

**Acknowledged limitations:** generation latency ("a minute or more") and occasional
inaccuracies in generated content; both flagged as open research areas [[G1]](#references).

**Implication for us:** the recipe is *not* exotic. It is prompt engineering depth + tools +
output repair on a frontier model. This is reproducible at hackathon scale with Claude. The
latency problem is real and must be designed around (see §6.1).

### 3.2 "Generative Interfaces for Language Models" (arXiv 2508.19227)

Independent academic treatment of the same thesis [[A1]](#references).

- **Framework:** given a query, the system generates a UI via **structured interface-specific
  representations** and **iterative refinement** — the interface is treated as an artifact to be
  refined against a reward, not a one-shot completion.
- **Evaluation:** a multidimensional framework scoring **functional, interactive, and
  emotional** dimensions of interface quality across diverse tasks.
- **Result:** generative interfaces consistently beat conversational ones, **up to +72% human
  preference** [[A1]](#references).

**Implication for us:** a generate → self-critique → refine loop measurably improves quality.
Even one refinement pass (render → screenshot/validate → fix) is worth budgeting for.

### 3.3 Adjacent academic work

- **LLM-driven accessible interfaces via model-based approaches** (arXiv 2601.06616) — applies
  model-based UI abstraction so LLM-generated interfaces stay accessible [[A2]](#references).
  Relevant to §7 gap G7 (accessibility is mostly unsolved in GenUI).

---

## 4. Industry implementations survey

| System | Level | Mechanism | Status | Ref |
|---|---|---|---|---|
| Gemini Dynamic View / Visual Layout | 3 | Model codes full interactive page per prompt; agentic coding + tools | Shipping (Gemini app, Search AI Mode) | [[G1]](#references), [[G3]](#references) |
| Claude Artifacts | 3 | Generated HTML/React in isolated pane | Shipping | [[O2]](#references) (OSS clone) |
| Vercel AI SDK (`streamUI`, RSC) | 1 | Tool calls → streamed React Server Components | Shipping, mature OSS | [[V1]](#references), [[V2]](#references) |
| Thesys C1 | 2 | OpenAI-compatible API returns UI DSL; React SDK renders | Commercial API | [[T1]](#references), [[T2]](#references) |
| OpenUI (Thesys) | 2 | Open spec: streaming-first UI language + React runtime | OSS | [[T3]](#references) |
| Google A2UI | 2 | Declarative JSON UI protocol, multi-framework renderers | OSS protocol (early) | [[P3]](#references), [[P4]](#references) |
| CopilotKit OpenGenerativeUI | 3 | Streams HTML → morphs into preview iframe (Idiomorph) → final sandboxed iframe with injected design-system CSS + CDN importmap | OSS | [[O1]](#references) |
| Renderify | 3 | In-browser transpile + sandbox + render of LLM-generated JSX/TSX, zero build step | OSS | [[O3]](#references) |
| LibreChat Artifacts | 3 | Sandpack (CodeSandbox) for secure rendering of generated HTML/JS | OSS | [[O4]](#references) |
| Anilturaga/Generative-UI | 3 | OSS "Imagine with Claude" clone; `srcdoc` iframes, provisional windows while args stream | OSS | [[O2]](#references) |
| Flutter GenUI SDK (Google) | 2 | LLM-driven adaptive interfaces in Flutter apps | SDK | [[S1]](#references) |

### Protocols / standards layer

Three complementary protocols have emerged; they answer different questions [[P1]](#references), [[P5]](#references):

- **MCP** (Anthropic) — how agents get *context and tools*.
- **A2A** — how agents talk to *other agents*.
- **AG-UI** (CopilotKit) — how agents talk to *applications and users*: an open, event-based
  protocol over SSE carrying the bidirectional stream between an agentic backend and a
  user-facing app (state sync, tool progress, user input, generative UI events)
  [[P1]](#references), [[P2]](#references). Adopted by Microsoft Agent Framework
  [[P6]](#references).
- **A2UI** (Google) — *what the user touches*: the declarative spec for the UI itself
  [[P3]](#references). Oracle/CopilotKit have demonstrated A2UI payloads carried over AG-UI —
  i.e., the two compose rather than compete [[P5]](#references).

**Implication for us:** Synapse's SSE typed-block contract is a home-grown mini-AG-UI. If the
project outgrows the hackathon, aligning the event contract with AG-UI (and the block schema
with A2UI concepts) buys interop for free. Not a hackathon priority.

---

## 5. Why users prefer it — and where it fails

**Validated upside:**
- Form-fits-content beats markdown in every eval surveyed (ELO ranking [[G1]](#references);
  +72% preference [[A1]](#references); "overwhelming" preference over markdown
  [[G2]](#references)).
- Interactivity converts passive reading into manipulation — the pedagogical case for Synapse
  specifically (predict-observe-explain requires an interface, not prose).

**Validated failure modes (design constraints, not footnotes):**

1. **Latency.** Level-3 generation takes ~a minute on Google's own stack [[G1]](#references).
   Unmitigated, this kills chat UX.
2. **Accuracy.** Generated interfaces sometimes present wrong content [[G1]](#references),
   [[G2]](#references). For education this is disqualifying unless mitigated (grounding,
   post-validation, or constrained composition for the science-critical core).
3. **Consistency.** Raw generation produces a different look every response; products solve
   this by injecting a design system into the sandbox (OpenGenerativeUI injects shared CSS +
   importmap [[O1]](#references)).
4. **Security.** Executing model-written code requires real isolation (§6.2). A2UI exists
   precisely because some environments cannot accept generated code at all
   [[P3]](#references).
5. **Model dependence.** The capability is emergent; on weaker/cheaper models Level 3 degrades
   sharply [[G2]](#references). Cost/latency vs. quality is a live tradeoff.

---

## 6. The four engineering problems and their known solutions

### 6.1 Latency → progressive streaming

- Stream the generated HTML token-by-token and render partials, morphing each update into the
  live DOM so nothing flickers — OpenGenerativeUI does this with **Idiomorph** before booting
  the final sandboxed iframe [[O1]](#references).
- Render provisional/skeleton UI the instant generation starts (provisional windows in
  [[O2]](#references)).
- Two-stage generation: fast model plans layout / streams shell, strong model fills it.
  (Speculative RSC streaming is being explored in the Vercel AI SDK community
  [[V3]](#references).)
- Level-1/2 fast path for anything the catalog or DSL can express; reserve Level 3 for what
  they can't.

### 6.2 Safety → sandboxed rendering

Non-negotiable rule across every surveyed implementation: **never inject generated code into
the host DOM.**

- **Sandboxed iframe via `srcdoc`** with restrictive `sandbox` attributes + CSP; no network
  access, no parent-DOM access ([[O1]](#references), [[O2]](#references)).
- Or **Sandpack** (CodeSandbox's bundler-in-browser) as LibreChat does [[O4]](#references).
- Or side-step entirely with UI-as-data (Level 2 / A2UI) [[P3]](#references).

### 6.3 Design consistency → injected design system

- Inject the product's design-system CSS and a pinned CDN importmap into every sandbox, and
  encode hard design rules in the system prompt ([[O1]](#references); consistent with Google's
  "detailed technical specifications" in system instructions [[G1]](#references)).
- Result: novel structure per response, but always *your product's* look, light/dark aware.

### 6.4 Interactivity round-trip → event bridge

A generated UI is agent-useless if user actions vanish inside the iframe.

- Inject a tiny SDK into the sandbox (`reportEvent(...)`) that forwards interactions to the
  host via `postMessage`; host forwards to the agent loop.
- This is exactly the layer AG-UI standardizes (bidirectional agent↔app events over SSE)
  [[P1]](#references), [[P2]](#references); C1 does the equivalent by wiring generated form
  submissions back to the model as tool calls [[T2]](#references).
- For Synapse: this is how the **Tutor Loop keeps receiving interaction events** (predictions,
  slider moves, sim results) even from fully generated interactives — the learner-model loop
  survives the jump to Level 3.

### 6.5 Reliability → repair + fallback

- Post-processors that fix known common defects before render [[G1]](#references).
- Iterative refinement against explicit quality criteria [[A1]](#references).
- Always keep a graceful fallback chain: Level 3 → Level 1 component → markdown. The demo never
  dies.

---

## 7. Gap analysis — what nobody has solved (the opportunity space)

**G1 — The "when and what form" decision policy is unstudied.**
Every system surveyed generates UI *when asked* or *always*. No published system has a
principled policy for *choosing the form* — when is text right, when a chart, when a full
interactive? The academic framework [[A1]](#references) refines a UI once committed; it does not
model the commitment decision. **A pedagogically-grounded form-selection policy (Synapse's
Strategist) is a genuine novelty claim.**

**G2 — Generation is intent-driven, not user-model-driven.**
Gemini Dynamic View is stateless per prompt: it adapts to the *query*, not to a persistent model
of the *user* (history, misconception trajectory, what representations worked before). Synapse's
learner store + spaced repetition addressing this is a differentiator no surveyed system has.

**G3 — Domain faithfulness of generated interactives is unvalidated.**
Google measures *preference* (ELO, PAGEN parity) — not *correctness* of an interactive's
underlying model (is the physics right? does the titration curve obey chemistry?). Known
inaccuracy is an admitted limitation [[G1]](#references). Nobody has published a
faithfulness-validation pipeline for generated simulations. A hybrid (faithful Level-1 core +
generated Level-3 shell) or a science-check refinement pass is open ground.

**G4 — Latency remains open even at Google scale** [[G1]](#references). Streaming mitigations
(§6.1) are engineering patches, not solutions. Anything that makes Level 3 *feel* instant
(speculative generation, aggressive skeletons, tiered escalation) is differentiating.

**G5 — Evaluation of outcomes, not preference.**
All published evals measure whether users *like* the interface ([[G1]](#references),
[[A1]](#references)). None measure whether it changes the *outcome* — for education: did the
student actually learn more? A pre/post concept-check across text vs. generated-interactive
conditions would be a publishable result even at small n.

**G6 — Process opacity.** Dynamic View shows a finished page; the reasoning that produced it is
hidden. Synapse's visible-agent-pipeline is the direct counter — and remains unique among the
systems surveyed.

**G7 — Accessibility of generated UIs is nearly untouched** (early work only
[[A2]](#references)). Generated interactives that are screen-reader-correct by construction is
an open problem.

**G8 — Cross-session state.** Generated interfaces are ephemeral: nothing persists a generated
tool the user liked, or re-generates it consistently later. (OpenUI's token-efficient re-render
[[T3]](#references) helps re-emit, not persist.) A "remembered interactive" tied to spaced
repetition (re-summon the same sim at review time) would be novel.

---

## 8. Where Synapse sits, and the recommended path to "fully generative"

### 8.1 Current position

Synapse is a strong **Level 1** system with the two rarest assets already built: a
**form-selection policy** (Diagnostician → Strategist decides *what kind* of experience is
pedagogically correct — gap G1) and a **persistent learner model** (gap G2), plus visible
reasoning (gap G6). What it lacks is expressiveness: 12 concepts ↔ ~14 patterns, and nothing
outside the catalog can render.

### 8.2 Recommended architecture: the three-tier escalation ladder

Keep the pedagogy pipeline untouched. Change what happens downstream of the Composer:

```
Diagnostician → Strategist ──► Composer decides tier:
                                 ├─ Tier 1 (exists): catalog pattern fits → typed block → library component
                                 └─ Tier 3 (new):    nothing fits → RENDERER AGENT
                                                       │ writes self-contained HTML/JS interactive
                                                       │ to the Strategist's pedagogical spec
                                                       ▼
                                     stream → morphing preview (Idiomorph-style)
                                            → final sandboxed iframe (srcdoc, CSP, no network)
                                            → injected Synapse design-system CSS
                                            → injected event-bridge SDK (postMessage)
                                                       │
                                                       ▼
                                     interaction events → Tutor Loop (learner model unchanged)
```

Fallback chain: Tier 3 failure → nearest Tier 1 component → markdown explanation. Demo never
dies.

**Design decisions this implies (log as ADRs):**
1. **Relax constraint D-01** ("agents never generate UI from scratch") — deliberately, with the
   escalation policy preserving the faithfulness story: *library first because it's faithful;
   generate only when the library cannot express the pedagogy.*
2. Renderer runs on the strongest available model (capability is emergent [[G2]](#references));
   everything else stays on cheap/fast models.
3. Renderer system prompt follows the Google recipe [[G1]](#references): goal + planning +
   examples + technical spec + common-mistakes list; add one refinement pass per
   [[A1]](#references) if latency budget allows.
4. Science-critical numerics can be **hybrid**: the generated shell imports a small vetted JS
   physics/chemistry helper injected alongside the design system (addresses G3).

### 8.3 Reference implementations to study before building

1. **OpenGenerativeUI** [[O1]](#references) — the closest end-to-end blueprint (streaming →
   morph → sandbox → design-system injection).
2. **Anilturaga/Generative-UI** [[O2]](#references) — minimal `srcdoc` + provisional-window
   streaming pattern.
3. **LibreChat Artifacts** [[O4]](#references) — Sandpack isolation alternative.
4. **thesysdev/openui** [[T3]](#references) — if a Level-2 DSL middle tier ever becomes
   attractive (token efficiency, zero code-safety surface).
5. **Renderify** [[O3]](#references) — if generating JSX instead of vanilla HTML.

### 8.4 De-risking order

1. Standalone spike: stream Claude-generated HTML into a sandboxed iframe with design CSS +
   postMessage bridge (no Synapse integration). Proves the whole risky surface in isolation.
2. Wire the spike in as the Composer's Tier-3 branch behind a flag.
3. Add the fallback chain + post-processing repair.
4. (Stretch) one refinement pass; (stretch) hybrid vetted-numerics injection.

---

## 9. Pitch-ready facts (all sourced)

- Users prefer generated interfaces to markdown "overwhelmingly"; ELO 1736.2, second only to
  human experts [[G1]](#references), [[G2]](#references).
- Up to +72% human preference vs. chat in independent academic evaluation [[A1]](#references).
- The capability is emergent on frontier models — this product category is months old, not
  years [[G2]](#references).
- Google ships it (Dynamic View) but stateless, opaque, and generic [[G1]](#references),
  [[G3]](#references) — Synapse's pedagogy-driven, learner-model-driven, visible-reasoning
  generation addresses exactly the published gaps (G1, G2, G5, G6).

---

## References

**Google research line**
- **[G1]** Google Research Blog — *Generative UI: A rich, custom, visual interactive user experience for any prompt* — https://research.google/blog/generative-ui-a-rich-custom-visual-interactive-user-experience-for-any-prompt/
- **[G2]** Leviathan, Valevski, et al. — *Generative UI: LLMs are Effective UI Generators* — arXiv:2604.09577 — https://arxiv.org/abs/2604.09577 (PDF: https://generativeui.github.io/static/pdfs/paper.pdf)
- **[G3]** Awesome Generative UI — *Google Gemini 3 — Dynamic View & Visual Layout* (case study) — https://awesomegenerativeui.com/cases/google-gemini-dynamic-view
- **[G4]** Generative UI project site — https://generativeui.github.io/

**Academic**
- **[A1]** *Generative Interfaces for Language Models* — arXiv:2508.19227 — https://arxiv.org/abs/2508.19227
- **[A2]** *LLM-Driven Accessible Interface: A Model-Based Approach* — arXiv:2601.06616 — https://arxiv.org/pdf/2601.06616

**Vercel AI SDK (Level 1)**
- **[V1]** Vercel — *Introducing AI SDK 3.0 with Generative UI support* — https://vercel.com/blog/ai-sdk-3-generative-ui
- **[V2]** Vercel Academy — *Multi-Step & Generative UI* — https://vercel.com/academy/ai-sdk/multi-step-and-generative-ui
- **[V3]** vercel/ai issue #13469 — *Speculative RSC Streaming (Zero-Latency Generative UI)* — https://github.com/vercel/ai/issues/13469

**Thesys (Level 2)**
- **[T1]** Thesys — *The Generative UI Company* — https://www.thesys.dev/
- **[T2]** Thesys docs — *How C1 Works* — https://docs.thesys.dev/guides/how-c1-works
- **[T3]** thesysdev/openui — *The Open Standard for Generative UI* — https://github.com/thesysdev/openui (announcement: https://www.thesys.dev/blogs/openui)

**Protocols**
- **[P1]** AG-UI docs — *Agent User Interaction Protocol* — https://docs.ag-ui.com/
- **[P2]** ag-ui-protocol/ag-ui (GitHub) — https://github.com/ag-ui-protocol/ag-ui
- **[P3]** Google Developers Blog — *Introducing A2UI: An open project for agent-driven interfaces* — https://developers.googleblog.com/introducing-a2ui-an-open-project-for-agent-driven-interfaces/
- **[P4]** google/A2UI (GitHub) — https://github.com/google/A2UI · a2ui.org — https://a2ui.org/introduction/what-is-a2ui/
- **[P5]** Oracle AI & Data Science blog — *Reusable Agents Meet Generative UIs: Agent Spec for A2UI through CopilotKit AG-UI* — https://blogs.oracle.com/ai-and-datascience/announcing-agent-spec-for-a2ui-copilotkit-ag-ui
- **[P6]** Microsoft Learn — *AG-UI Integration with Agent Framework* — https://learn.microsoft.com/en-us/agent-framework/integrations/ag-ui/

**Open-source Level-3 implementations**
- **[O1]** CopilotKit/OpenGenerativeUI — https://github.com/CopilotKit/OpenGenerativeUI
- **[O2]** Anilturaga/Generative-UI — open implementation of "Imagine with Claude" — https://github.com/Anilturaga/Generative-UI
- **[O3]** Renderify — *A Runtime Engine for Rendering LLM-Generated UI Instantly in the Browser* — https://dev.to/unadlib/renderify-a-runtime-engine-for-rendering-llm-generated-ui-instantly-in-the-browser-1amf
- **[O4]** LibreChat — *Artifacts (Generative UI)* — https://www.librechat.ai/docs/features/artifacts

**Other**
- **[S1]** Medium (Akshay Chame) — *The Complete Guide to Generative UI Frameworks in 2026* (survey incl. Flutter GenUI SDK) — https://medium.com/@akshaychame2/the-complete-guide-to-generative-ui-frameworks-in-2026-fde71c4fa8cc

---

*Verification note: [G1], [A1], [G2]-abstract were fetched and read directly on 2026-07-06.
Remaining sources were verified to exist via web search on the same date; claims drawn from
search-result summaries of those pages are attributed to the page cited. The OpenUI 67%
token-efficiency figure and all Thesys C1 capability descriptions are vendor claims.*
