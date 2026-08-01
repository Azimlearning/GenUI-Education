# Codex Hackathon KL 2026 — Submission Form Draft

Draft answers for the submission form, generated from `docs/HACKATHON_CONTEXT.md`,
`docs/SECURITY.md`, and `docs/DEV.md`. Copy into the form; fill remaining
`[PLACEHOLDER]`s before submitting.

---

### Project title *

**Synapse**

(This repo's internal engineering codename is "Synapse" — use "Synapse" on all
Codex-facing materials, since that's the name registered with Codex Community
Malaysia. Team name: **Team Dang Wangi**, not "EduNova".)

---

### One-line pitch *

Turn a Malaysian SPM student's science question into a verified, interactive
lab experiment instead of another wall of chatbot text.

---

### Problem and target user *

Malaysian Form 4-5 KSSM SPM science students (Physics, Chemistry, Biology) —
particularly in B40 and rural schools without functioning physical labs — end
up memorising static textbook diagrams instead of building real experimental
intuition. Generic AI chatbots compensate for the missing lab by producing
more text, which caps how much understanding a wall of words can build.
Synapse's target user is this student (and, secondarily, their teacher):
someone who needs to *see and manipulate* a phenomenon — projectile motion,
buoyancy, pH titration, wave interference — not read another paragraph about it.

---

### Product description *

Synapse is a generative-UI science tutor. A student asks a question in a chat
interface; the backend pipeline (FastAPI + LangGraph + Postgres) routes the
query, plans a specific interactive artifact (simulation, explorable diagram,
or experiment), generates it as self-contained HTML/JS (p5.js, Matter.js,
Three.js, Chart.js, D3, or vanilla JS/canvas), and independently verifies it
for scientific correctness and safety before it ever reaches the browser. The
verified artifact renders in a sandboxed iframe (`sandbox="allow-scripts"`
only — no same-origin access) so the student can drag, adjust, and observe the
simulation directly, alongside a streamed text explanation.

Key architectural points worth calling out to judges:
- **Router → Planner → Generator → Verifier** pipeline: no unverified artifact
  can structurally reach the client (the delivery function's type signature
  requires proof of a passed verification).
- **No predefined component library** — every artifact is generated fresh
  against the question, or the system degrades to a text-only answer rather
  than faking interactivity.
- **Grounded in the real KSSM Form 4/5 Bio/Chem/Physics syllabus**, with a
  parallel ML track (router-distill classifier, curriculum RAG) in progress.
- Vendored libraries served same-origin (`/vendor/*`), no runtime CDN fetches.

---

### Team members *

Names and emails, from the Team Dang Wangi registration record in
`docs/HACKATHON_CONTEXT.md` (roles only recorded for the lead there):

| Name | Role | Email |
|---|---|---|
| Fakhrul Azim Bin Ahmed Mardzukie (Lead) | AI/ML, prompting/agent workflows, backend | fakhrulazim.am@gmail.com |
| Abdul Hafiz Bin Mohd Noor Azman | `[PLACEHOLDER: role]` | `[PLACEHOLDER: email]` |
| Nur Alia Syahira Binti Nor Azam | `[PLACEHOLDER: role]` | `[PLACEHOLDER: email]` |
| Nur Farah Binti Ahmad Nazri | `[PLACEHOLDER: role]` | `[PLACEHOLDER: email]` |
| Por Jie Hao | `[PLACEHOLDER: role]` | `[PLACEHOLDER: email]` |

`[PLACEHOLDER: fill in the four missing emails and roles — not recorded
anywhere in the repo, only the lead's own email is known]`

---

### GitHub repository URL *

https://github.com/Azimlearning/GenUI-Education

`[PLACEHOLDER: confirm this repo is set to Public, or that judges have been
explicitly granted access — the confirmation checkbox at the bottom of this
form asserts this]`

---

### Live project URL

`[PLACEHOLDER: deployment URL]`

Per `docs/HACKATHON_CONTEXT.md`, the choice between (a) a public URL judges
can access independently vs. (b) a local laptop demo with a recorded backup
video was still an open decision as of 2026-07-13. Resolve this before
submitting — if going with (a), fill in the deployed URL here; if going with
(b), leave this blank and make sure the YouTube demo below is a full,
self-contained run-through.

---

### YouTube demo URL *

`[PLACEHOLDER: record and upload, target ≤ 4 minutes]`

Suggested structure given the pipeline above:
1. (~20s) Problem framing — B40/rural student, no lab, static diagrams.
2. (~30s) Ask a real SPM question in the chat UI.
3. (~90s) Streamed explanation + artifact build (staged progress card),
   landing on the sandboxed interactive simulation — show it being
   manipulated live.
4. (~30s) Call out the Verifier gate / sandbox explicitly ("this is why it's
   safe to run untrusted generated code") — direct hit on judging criterion 4
   (Responsible AI).
5. (~30s) Close on the KSSM grounding and continuation plan (FYP, open-source).

---

### Databricks evidence

Not applicable — this project does not use Databricks. Persistence is
Postgres via SQLAlchemy/Alembic; no Databricks app, workspace, pipeline, or
governance feature is part of the current build. Leave blank or mark N/A on
the form.

`[PLACEHOLDER: confirm no team member used Databricks elsewhere in the stack
before submitting this as N/A]`

---

### ElevenLabs evidence

Not applicable — no voice UX or ElevenLabs integration exists in this build
(text/visual artifact only, no TTS/STT). Leave blank or mark N/A on the form.

`[PLACEHOLDER: confirm no team member used ElevenLabs elsewhere before
submitting this as N/A]`

---

### Responsible AI notes *

Responsible AI is judging criterion 4, and it's structurally load-bearing in
this build rather than a bolt-on:

- **No unverified artifact can reach the client.** `backend/services/delivery.py`
  is the only function that can emit a completed artifact, and its signature
  requires a `PassedVerifierReport` object whose constructor is private to
  the verifier module. An unverified artifact reaching the client is a type
  error, not a policy that can be silently skipped.
- **Sandboxed execution.** Every generated artifact runs in an iframe with
  `sandbox="allow-scripts"` only — never `allow-same-origin` — giving it an
  opaque origin. It cannot read the parent page's cookies, localStorage, or
  DOM, and cannot navigate the parent window.
- **Two independent safety enforcers.** A forbidden-API deny list (fetch,
  XHR, WebSocket, eval, cookies, storage, navigation, etc.) is checked both
  semantically by the LLM Verifier (catches obfuscation like string-built API
  names) and deterministically by a static scan in `postprocess.py`. A hit
  from either is a hard reject, never a silent auto-strip.
- **No runtime CDN dependencies.** All third-party libraries (p5, Matter.js,
  Three.js, Chart.js, D3, KaTeX) are vendored, pinned, and checksum-verified
  in CI, served same-origin — no arbitrary external script execution surface.
- **Prompt-injection resistance.** The Generator never sees the raw student
  question — only a structured `ArtifactPlan` produced by the Planner, which
  bounds what free text can smuggle into generated code. The Verifier runs in
  a fresh context and is explicitly instructed to treat any instruction-like
  content inside generated code comments as untrusted and reportable, not
  actionable.
- **"Wrong science as harm" is treated as a first-class risk**, not just a
  security bug: a confidently-wrong simulation can teach a wrong mental
  model. Mitigated via verifier science spot-checks, a flag/evict path for
  bad cached artifacts, and weekly manual audits.
- **Privacy by default.** Sessions are anonymous — no accounts, no emails, no
  names, no PII columns in the schema. Interaction events aggregate-and-delete
  after 30 days. No user-specific data is ever embedded in cached artifact HTML.
- **Cost and abuse controls.** Rate limits (cookie + IP) and a hard per-run
  cost ceiling (`MAX_RUN_COST_USD`) fail loudly rather than allowing runaway
  spend from scripted abuse.

Known accepted limitation, stated plainly rather than hidden: the Verifier is
probabilistic (an LLM judging an LLM's output), so it is backstopped by the
deterministic postprocess scan for safety-critical checks, and residual
science-correctness risk is monitored via the flag/evict loop and manual
audits rather than assumed away.

---

### Setup instructions *

```
# 1. Configure
cp .env.example .env
# edit .env: set ANTHROPIC_API_KEY=sk-ant-...

# 2. Backend (terminal 1)
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements-dev.txt
.venv\Scripts\python -m uvicorn main:app --port 8000 --reload
# sanity check: curl http://localhost:8000/api/health -> {"status":"ok","llm":"live"}

# 3. Frontend (terminal 2)
cd frontend
npm install
npm run dev
# open http://localhost:3000 and ask a science question
```

Notes for judges: the app runs fully without Docker or Postgres — persistence
(sessions/messages/trace rows) is fire-and-forget and only needed for
long-term history, not for chat or artifact generation to work. Without an
API key the app runs in "echo mode" (streams the plumbing, makes no model
calls, builds no artifacts) — a real `ANTHROPIC_API_KEY` is required to see
generated interactive artifacts. First artifact typically takes 1.5–4 minutes
to generate (provider first-token variance); this is expected, not a hang.

Canonical Docker path (if available): `make dev` then `make migrate`.

---

### Submission confirmation *

These are attestations only the team can make — action items, not draftable:

- [ ] Confirm the GitHub repository (`Azimlearning/GenUI-Education`) is
      public or judges have explicit access.
- [ ] Confirm the YouTube demo link works (unlisted/public, not private).
- [ ] Confirm this is the final submission before checking the box.
