# Demo Day playbook — 18 July 2026, Sunway University

Closes the two risks left open in
[`../Codex hackathon/codex-project-scope.md`](../Codex%20hackathon/codex-project-scope.md) §10:
the deployment decision, and what happens when a generated interactive misbehaves live.

---

## 1. Deployment: do both

**Deploy to Vercel _and_ record a backup video.** These were framed as alternatives; they aren't,
and picking one is what makes the risk real.

Ship a public URL so judges can open it themselves (that independently addresses "Usefulness of
Working Demo" better than any narration), and hold a recorded run of the full flagship script in
case the venue wifi is the venue wifi.

### Deploy

```bash
cd synapse-v2
vercel --prod
```

Then set `ANTHROPIC_API_KEY` in the Vercel project's environment variables (Settings →
Environment Variables). `OPENAI_API_KEY` is optional and enables the router's fallback leg — worth
adding, since the fallback is part of the responsible-AI story.

Two settings that already matter, both in [`vercel.json`](vercel.json):

- **`"regions": ["sin1"]`** — Singapore. The default is US East, which would add roughly 200ms to
  every round trip of a demo happening in Petaling Jaya. Free to fix, embarrassing not to.
- **`maxDuration: 300`** — Tier C can legitimately run ~60s. The Hobby plan's ceiling is 300s with
  fluid compute (on by default), so this fits without a paid plan.

### Before you leave for the venue

- [ ] Open the production URL on the **presenting laptop, on the venue wifi**, and run one prompt
      of each tier. A cold serverless start is not the moment to discover a missing env var.
- [ ] Record the backup video from the production URL, not localhost. If it's shown, it should be
      the real thing.
- [ ] Tether a phone as wifi backup. Conference wifi at a 150-person event is a coin flip.

---

## 2. The script

Roughly 5 minutes. The order is deliberate: it opens on the strongest moment rather than building
to it, because a judge's attention is never higher than in the first thirty seconds.

### Beat 1 — the misconception (Tier A, ~8s) — **the money shot**

> Type: **"Osmosis is when water moves to where there is more water, right?"**

This is the whole pitch in one prompt. Land these three things, in this order:

1. **The Checker names the contradiction _before anything is built._** Read it off the screen.
   "It hasn't answered yet. It's told the student their premise is backwards, and it did that
   before generating anything."
2. **Press "Generate Experiment".** Point at the pipeline panel: chosen tier, and the actual slot
   values it filled. "That's a teacher's-eye view. If it filled a wrong concentration, you'd see it
   there, not discover it later."
3. **Predict the wrong answer on purpose.** Choose "water moves left" (toward the dilute side), run
   it, and let the sim contradict you visibly. "A chatbot tells you you're wrong. This makes you
   watch yourself be wrong. That's the difference in one screen."

The line to say out loud while it runs: **the model chose the scenario, but it did not get a vote
on which way the water moves.** That's the pinning mechanism, and it's the answer to "how do you
know the AI isn't teaching them nonsense?"

### Beat 2 — specificity (Tier A, ~8s)

> Type: **"Show me 0.5 M NaCl against 0.1 M across a plant cell membrane at 37°C"**

Same component, different lab. "Same pre-built machinery, specialised to their question. The
student brings the specifics; the science stays ours."

Then interact once and let the **Guide** respond to what was actually done. That's the "guidance,
not a toy" claim, demonstrated instead of asserted.

### Beat 3 — the bet (Tier C, ~40s) — **the ambitious moment**

> Type: **"Build me a lab for total internal reflection in a fibre optic cable"**

The 40 seconds are the risk and also the show. Do not fill them with silence, and do not apologise
for them. Talk over the streaming preview:

> "It's writing this from scratch right now. No component in our library does fibre optics. It's
> deciding what the apparatus is, writing the geometry, writing the interaction. It runs in a
> sandbox with no network and no access to the page — because we're not going to promise you a
> model never writes something stupid. We're going to make sure it can't matter."

If it lands: interact with it, and point out that a fully generated lab still reports back to the
Guide.

### Beat 4 — close (30s)

Fastest honest framing for the marketability criterion:

> "Every Form 4 student in a school without a lab has the same syllabus and none of the equipment.
> This runs on a phone browser. It continues as an FYP at UTP with an evaluation study; open-source
> for schools, licensed to tuition centres — that's the split we'd test first."

---

## 3. When it breaks

The fallback chain is **C → B → A → plain explanation**. It's real and it's tested — but rehearse
saying it out loud, because the fallback is a better story than the success if you narrate it as
one and a worse one if you look surprised.

| What you see | What it is | Say this |
|---|---|---|
| Yellow "Tier C didn't land, so this is the tier B version" | The generated lab failed its safety check or the model errored. It degraded automatically. | "That's the safety net doing its job. It tried to write one from scratch, the output didn't pass, so it dropped to a composed screen. The student still gets a lab. On stage that's a good look, not a save." |
| Pipeline step goes red, then continues | A validation failure and its repair round-trip. | "It just caught its own bad output and fixed it. That step is visible on purpose." |
| Nothing for >20s on Tier A/B | Provider slow, or falling through the router chain. | Keep talking. If >45s, refresh and use Beat 2's prompt — Tier A is the fast path. |
| Red "Component drift" box | Pipeline asked for a component this build doesn't have. Should not happen; the registry is checked at load. | Move on to the next beat. Don't debug live. |
| Page errors out entirely | Network or a dead API key. | Switch to the recorded video. Don't troubleshoot on stage. |

**The one rule: never say "it usually works."** Every failure mode above is either a designed
behaviour you can narrate, or a reason to cut to the video. There is no third option worth taking
in front of judges.

---

## 4. Answers to the questions you'll actually get

**"How do you know the AI isn't teaching them wrong science?"**
Three layers, and say all three. Science-critical values are pinned — the model fills the scenario,
but `correct_direction: "toward-higher-solute"` is merged over whatever it proposed, so a model
asserting the misconception still ships the correct sim (there's a test for exactly that). Every
slot value is schema-validated before render. And the filled values are on screen in the pipeline
panel, so a teacher can catch a bad fill rather than trust us.

**"Isn't this just ChatGPT with extra steps?"**
Ask a chatbot about osmosis and you get a wall of text you can nod along to while still holding the
misconception. Here you have to commit to a prediction, and then watch it fail. The output format
is the pedagogy.

**"What if the model writes malicious code in Tier C?"**
It runs in an iframe with `allow-scripts` and deliberately *without* `allow-same-origin`, so it has
an opaque origin and no reach into the page, our cookies, or storage. CSP is `default-src 'none'`
with no `connect-src`, so no network egress. Generated code never touches the host DOM. That's the
same rule every surveyed production system converged on.

**"Why not just generate everything from scratch?"** (the sharp one)
Because faithfulness and expressiveness trade off, and pretending they don't is how you demo a sim
that teaches the wrong thing. Model freedom is spent on composition and specificity; it isn't spent
re-deriving physics we already have correct. The ladder is the product decision, not a limitation.

**"Who pays for this?"**
Don't oversell. FYP continuation at UTP with a 10–15 participant evaluation study is the concrete
next step; open-source for public schools with licensing to tuition centres is the hypothesis to
test, not a plan we've validated.

---

## 5. Housekeeping

- **Team name is "Dang Wangi"**, not EduNova, in every Codex-facing surface: the submission form,
  the deck, and the demo intro. That's the registration record the judges see.
- Have the repo open in a second tab. "Technical Execution" is a judged criterion and the tier
  ladder reads well.
- Say **Codex accelerated the build**, not that it's in the runtime. It's the build tool. The
  runtime is Claude via the provider router.
