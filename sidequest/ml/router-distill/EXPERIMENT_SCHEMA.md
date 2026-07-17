# Experiment Record Schema

**Status: schema defined, NOT yet populated.** What actually exists in
`dataset/labeled/*.jsonl` today is lighter-weight: routing labels
(`artifact_type`, `domain`, `complexity`) plus curriculum tagging
(`curriculum_topic`, `curriculum_subject`, `curriculum_form`) from
`kssm_topics.py`. The full Experiment Record below (`apparatus`,
`hypothesis`, `procedure`, ...) requires a `generate_experiments.py` script
that calls the Planner per sampled query — that script has not been written
and no such calls have been made. This document is the target schema for
that future work, kept here so the design is settled before spending on it.

Every artifact Axiom builds IS a scientific experiment: a question, a testable
model, an apparatus (the interactive), a procedure (what the learner does), and
an expected result. This document defines the full record we capture per
query and how it maps onto the scientific method and the classroom.

## Why this exists

The router-distill dataset started as bare routing labels
(`query -> artifact_type, domain, complexity`). That is enough to train a
classifier, but it throws away everything that makes an artifact pedagogically
real. This schema restores that: for a sample of artifact-bound queries, we
call the production Planner (the same LLM node the live pipeline uses,
`backend/prompts/planner.md`) and derive the full record below. It becomes:

1. A human-inspectable corpus for reviewing what "good" looks like per domain.
2. A regression/few-shot corpus for tuning the live Planner prompt.
3. Training data for the ONE new classifier head that is genuinely
   closed-vocabulary and learnable from text alone: `library` (which
   vendored apparatus the artifact should be built with).
4. A seed corpus for a future generative model, IF the project ever commits to
   fine-tuning one (see README "not in scope").

## What a tiny text classifier can and cannot learn

Read this before assuming the model "learns" a hypothesis or a procedure.

| Field | Learnable by the classifier? | Why |
|---|---|---|
| `artifact_type`, `domain`, `complexity` | yes | closed label sets, this is the router-distill core |
| `library` (apparatus class) | yes | closed label set (6 values), added as a 4th head here |
| `hypothesis`, `procedure_steps`, `expected_outcome`, `user_interaction`, `learning_objective` | **no** | open-ended free text; needs a generative model, which is what the LLM Planner already is |

The classifier answers "what kind of experiment and with what apparatus."
The Planner answers "what exactly is the experiment." Distilling the second
one into a small offline model is a materially bigger project (sequence
generation, thousands of examples, a real quality bar) and is tracked as
future work, not built here.

## The Experiment Record

One record per sampled artifact-bound query, in
`dataset/labeled/experiments_<tag>.jsonl`:

```jsonc
{
  "query": "why does ice float?",
  "routing": {                       // from the Router (routing labels)
    "artifact_type": "simulation",
    "domain": "chemistry",
    "complexity": 2
  },
  "apparatus": {                     // what the learner manipulates
    "library": "p5",                 // classifier-learnable
    "controls": [                    // = plan.variables, the physical "knobs"
      { "name": "water_temperature", "unit": "C", "min": 0, "max": 30, "default": 20 },
      { "name": "salinity",          "unit": "g/kg", "min": 0, "max": 40, "default": 0 }
    ]
  },
  "hypothesis": {                    // the testable claim, derived from governing_model
    "statement": "Ice floats because rho_ice (0.917 g/cm^3) < rho_water (~1.0 g/cm^3); the submerged fraction equals rho_ice / rho_water.",
    "governing_model": "submerged_fraction = rho_ice(T) / rho_water(T, salinity)"
  },
  "procedure": {                     // scientific-method steps, derived from the plan
    "setup": "Load the default scene: an ice cube in water at 20 C, 0 g/kg salinity.",
    "steps": [
      "Observe the default submerged fraction readout.",
      "Adjust water_temperature and note whether the readout changes (it should not, to first order).",
      "Adjust salinity upward and observe the cube ride higher (denser water).",
      "Predict the submerged fraction at a chosen salinity before checking the readout."
    ],
    "measurement": "submerged_fraction readout, percent"
  },
  "expected_outcome": [              // = plan.expected_behaviors
    "the cube never fully sinks at any control setting",
    "submerged fraction rises as salinity increases",
    "submerged fraction stays within 1-2% of rho_ice/rho_water at any temperature"
  ],
  "user_interaction": {              // = plan.layout_notes + the artifact's try-this hint
    "try_this": "crank salinity up to 35 g/kg and watch the ice ride higher",
    "layout_notes": "tank canvas on top, temperature and salinity sliders below, submerged-fraction readout beside the tank, reset button"
  },
  "learning_objective": "Understand that ice floats because solid water is less dense than liquid water, and that the submerged fraction is a direct, predictable ratio of densities.",
  "relation_to_curriculum": {
    "domain": "chemistry",
    "concept_tag": "density_and_buoyancy",     // derived from plan.title, snake_case
    "prerequisite_concepts": ["density", "states of matter"],
    "typical_grade_band": "middle to high school"
  },
  "scientific_method_stage_map": {   // explicit mapping, for anyone reading the record
    "question": "query",
    "hypothesis": "hypothesis.statement",
    "apparatus": "apparatus",
    "procedure": "procedure.steps",
    "prediction": "expected_outcome",
    "observation": "left to the learner, inside the live artifact",
    "conclusion": "left to the learner, prompted by user_interaction.try_this"
  },
  "provenance": {
    "planner_model": "claude-sonnet-5",
    "planner_prompt_version": "planner-v2",
    "generated_at": "2026-07-18T00:00:00Z"
  }
}
```

Field-to-plan mapping (so the schema stays traceable to `backend/schemas/plan.py`):

| Experiment Record field | Source |
|---|---|
| `apparatus.controls` | `ArtifactPlan.variables` verbatim |
| `apparatus.library` | `ArtifactPlan.library` |
| `hypothesis.governing_model` | `ArtifactPlan.governing_model` |
| `hypothesis.statement` | derived: one-sentence paraphrase of the governing model, LLM-written during the same call |
| `procedure.steps` | derived: an ordered manipulate-and-observe sequence over `variables`, LLM-written |
| `expected_outcome` | `ArtifactPlan.expected_behaviors` verbatim |
| `user_interaction.layout_notes` | `ArtifactPlan.layout_notes` |
| `user_interaction.try_this` | derived: one sentence, same style as the artifact's own "Try this:" hint |
| `learning_objective` | `ArtifactPlan.learning_objective` |
| `relation_to_curriculum.concept_tag` | derived: snake_case of `ArtifactPlan.title` |

## Not derived by a second free-standing prompt

To keep cost and complexity bounded, `hypothesis.statement`,
`procedure.steps`, `user_interaction.try_this`, and
`relation_to_curriculum.*` are produced in the SAME structured tool call as
the plan itself (one extended schema, one Planner call per sampled query),
not a second LLM round trip. See `generate_experiments.py`.
