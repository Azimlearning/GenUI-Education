# Synapse, Project Video Script (target 8 minutes)

> hackAstone deliverable. Shot-by-shot script for the submission video. Record with a real
> ANTHROPIC_API_KEY set so the agent reasoning is genuinely live. The single strongest 10 seconds
> is the osmosis "aha" (marked HOOK) at 1:30; lead the trailer/thumbnail with it.

## Beat sheet

| Time | Beat | On screen |
|---|---|---|
| 0:00 | The Malaysian problem + user | Talking head + b-roll |
| 1:00 | The wedge vs generic GenUI | The "How Synapse is different" explainer |
| 1:30 | LIVE DEMO: the osmosis aha (HOOK) | Screen capture, live agents |
| 4:30 | Breadth across subjects | Flash 2 to 3 more concepts |
| 5:30 | Teacher view + how it scales | `/teacher` dashboard |
| 6:30 | Pedagogy + evaluation plan | Slides + KB citations |
| 7:15 | Commercial path + team + close | Slides |

---

## Script

### 0:00 to 1:00, the problem and the user

"Meet a Form 4 SPM student in a school with one shared science lab and forty students to a class.
She can recite that osmosis is 'water moving across a membrane', but on the exam she writes that
water moves to where there is more water. It is the wrong idea, and no one has the lab time to show
her why. That gap, between reciting and understanding, is what fails students, especially in B40
and rural schools where practical work is hardest to deliver."

Show: student b-roll, a crowded lab, an SPM paper.

### 1:00 to 1:30, the wedge

"Generic AI tutors generate an answer or a one-shot 'dynamic view'. They hide their reasoning and
they make up the interface on the fly, which risks getting the science wrong. Synapse does the
opposite. It diagnoses the specific misconception, decides the pedagogically correct move, and
composes a pre-built, science-faithful experiment. And it does all of that where you can watch it."

Show: the "How Synapse is different" explainer expanded on the landing page.

### 1:30 to 4:30, LIVE DEMO (HOOK at the osmosis contradiction)

Type the osmosis misconception into the prompt: "osmosis is when water moves to where there's more
water."

Narrate as the pipeline streams live:
- "The Diagnostician doesn't guess. It matches against a sourced misconception library and finds
  osmosis-inverted-gradient."
- "The Strategist names the learning-science move on screen: this is a misconception, not a gap,
  so predict-observe-explain, make her commit before revealing."
- "The Composer selects the gradient-diffusion sandbox and configures it. It never draws UI; it
  configures a component whose physics we pinned in code."

Then the interactive: "She predicts water moves toward more water." Click that prediction. Run it.

**HOOK (the aha):** the water visibly moves the other way, toward the higher-solute side. "The
simulation contradicts her. That contradiction is the teaching moment, and it is faithful: water
moves down the water-potential gradient, toward more solute, every time."

Then the loop closes: "The Tutor Loop logs the misconception and schedules a review. Watch her
progress panel update." Show the mastery bar and the tracked misconception.

### 4:30 to 5:30, breadth

"The same agents, the same pattern library, serve every subject." Flash quickly:
- Forces and motion: predict whether the trolley accelerates; watch it obey F = ma with a live
  velocity-time graph derived from the sim.
- Bonding: metal plus non-metal, electrons transfer, ionic; non-metal plus non-metal, electrons
  share, covalent. Encoded, not guessed.

"Twelve concepts across Physics, Chemistry and Biology, from fourteen interaction patterns."

### 5:30 to 6:30, teacher view and scale

Open `/teacher`. "This is why schools adopt it. A teacher sees the whole class as a heatmap: who
holds which misconception, mastery per topic, what is due for review. New topics are configuration,
not new code, so this scales across the whole KSSM syllabus."

### 6:30 to 7:15, pedagogy and evaluation

"Every diagnosis is grounded in a citable misconception library, with real sources: Odom and
Barrow on osmosis, Taber on bonding, Clement and Halloun-Hestenes on force." Show the KB and the
sources. "And we have a concrete evaluation plan: a pre/post two-tier diagnostic on the flagship
misconceptions, with a one-week retention test."

### 7:15 to 8:00, commercial path, team, close

"Free for students, a teacher dashboard that pulls schools in, licences at school and district
scale, and a B40 lab-access story that aligns with the Ministry's equity goals." Team card: Team
Dang Wangi, UTP. "Synapse: pedagogy-driven, science-faithful, and you can watch it think. Thank
you."

Show: live URL (once deployed), repo link.

---

## Recording notes

- Set a real ANTHROPIC_API_KEY in `backend/.env` so the agent steps are genuinely live, not
  scripted, for the recording.
- Do a dry run of the osmosis path so the HOOK lands cleanly in one take.
- Keep total runtime at or under 8 minutes; the breadth section is the first place to trim.
