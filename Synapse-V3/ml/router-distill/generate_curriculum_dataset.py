"""Generate a KSSM-curriculum-scoped, style-diverse labeled dataset.

Difference from generate_dataset.py: queries are generated PER TOPIC from
kssm_topics.py, in five deliberately varied phrasing styles (one per
artifact_type). This fixes the class imbalance seen in the v1 generic run
(virtual_experiment had only 3/458 rows) by making sure the input queries
actually span all five intended experiences, rather than leaving the
distribution to chance. The labels themselves still come from the real,
unmodified production Router prompt: we are diversifying the INPUT
distribution, not the teacher's decisions.

Each row gets curriculum_topic (subject_formN_topicslug) alongside the
standard routing labels, so the classifier's core heads
(artifact_type/domain/complexity) stay compatible with the production Router
schema (backend/schemas/intent.py) per the "keep generic domains, add
curriculum tag alongside" decision.

Retrieval-anchored generation (2026-07-18, ml/IMPLEMENTATION_PLAN.md Phase
3): before generating queries for a topic, one real passage is retrieved
from ml/rag's index (if built) and included in the generation prompt, so
questions echo the actual textbook's register and vocabulary instead of
generic international-English science phrasing. Falls back to topic-only
generation (the v1/kssm1 method) if the RAG index is missing or empty for
that subject/form, so this never hard-fails a run.

Usage (from this directory):
  ..\\..\\backend\\.venv\\Scripts\\python generate_curriculum_dataset.py --tag kssm2 --per-style 6
  ..\\..\\backend\\.venv\\Scripts\\python generate_curriculum_dataset.py --tag dev --topics-limit 4
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "backend"))
sys.path.insert(0, str(HERE.parent / "rag"))

from graph.nodes.router import parse_intent  # noqa: E402
from services.llm import get_llm  # noqa: E402
from services.prompts import load_prompt  # noqa: E402
from config import get_settings  # noqa: E402
from kssm_topics import all_topics  # noqa: E402

try:
    from retrieve import load_index as rag_load_index  # noqa: E402
    from retrieve import search as rag_search  # noqa: E402
except ImportError:
    rag_load_index = None
    rag_search = None

DOMAIN_BY_SUBJECT = {
    "biology": "biology",
    "chemistry": "chemistry",
    "physics": "physics",
}

# One style per artifact_type, so generation deliberately covers all five,
# instead of leaving the distribution to whatever the model produces
# unprompted (the cause of v1's virtual_experiment scarcity).
STYLES = [
    (
        "text_only",
        "quick factual lookup questions (a definition, a value, a name, a date) "
        "about {topic}, the kind a student asks while doing homework, e.g. "
        "'what is the definition of X' or 'what is the value of Y'",
    ),
    (
        "simulation",
        "questions asking to SEE a continuous process happen, using words like "
        "show me, simulate, animate, or watch, about {topic}, e.g. "
        "'show me how X happens' or 'simulate the process of Y'",
    ),
    (
        "virtual_experiment",
        "questions asking to run a trial and take a measurement, or describing "
        "a hands-on procedure, about {topic}, e.g. 'what happens when you titrate X "
        "with Y' or 'how does changing X affect the measured Y, test it' or "
        "'run an experiment to find out...'",
    ),
    (
        "explorable_diagram",
        "questions asking to understand a labeled structure or a staged mechanism, "
        "about {topic}, e.g. 'explain the stages of X' or 'walk me through the parts "
        "of Y' or 'what does the diagram of Z look like'",
    ),
    (
        "data_visualization",
        "questions asking to compare curves, trends, or distributions driven by a "
        "parameter, about {topic}, e.g. 'compare X and Y over time' or "
        "'how does changing X affect the trend in Y'",
    ),
]

GEN_PROMPT = """Generate {k} distinct short questions a Malaysian secondary school student ({form_label}) might type into a science chat app about this specific topic: {topic_label} ({hint}).
{grounding_block}
Style: {style_desc}

Write in natural student phrasing, mixing formal and casual tone. One question per line, no numbering, no quotes, 4 to 20 words each. Do not repeat phrasings. Do not explicitly mention "Form 4" or "Form 5" in the question text; just ask the science question."""

GROUNDING_BLOCK_TEMPLATE = """
Real textbook excerpt for this topic (match this vocabulary and register, do not quote it directly):
\"\"\"{excerpt}\"\"\"
"""

_RAG_INDEX = None  # lazy-loaded once, reused across all topics


def _rag_index():
    global _RAG_INDEX
    if _RAG_INDEX is not None:
        return _RAG_INDEX
    if rag_load_index is None:
        _RAG_INDEX = False
        return False
    try:
        _RAG_INDEX = rag_load_index()
    except SystemExit:
        # ml/rag/index/ not built yet; degrade to topic-only generation
        # rather than hard-failing the whole run.
        _RAG_INDEX = False
    return _RAG_INDEX


def grounding_excerpt(topic: dict, max_chars: int = 500) -> str | None:
    """One real passage for this topic's subject/form, or None if the RAG
    index is unavailable or has nothing relevant. Best-effort only: retrieval
    quality varies by subject/form (see ml/rag/README.md "Status"), so a
    weak or missing excerpt just means plain topic-only generation for that
    row, never a crash."""
    index = _rag_index()
    if not index:
        return None
    passages, vectors, embedder = index
    query = f"{topic['label']} {topic['hint']}"
    results = rag_search(
        query, passages, vectors, embedder, k=1, subject=topic["subject"], form=topic["form"]
    )
    if not results:
        return None
    return results[0]["text"][:max_chars]


async def generate_for_topic_style(
    llm, settings, topic: dict, artifact_type: str, style_desc: str, k: int, excerpt: str | None
) -> list[str]:
    form_label = f"Form {topic['form']}"
    grounding_block = (
        GROUNDING_BLOCK_TEMPLATE.format(excerpt=excerpt) if excerpt else ""
    )
    result = await llm.complete(
        model=settings.model_fast,
        system="You generate realistic student science questions for a training dataset. Output only the questions, one per line.",
        user=GEN_PROMPT.format(
            k=k,
            form_label=form_label,
            topic_label=topic["label"],
            hint=topic["hint"],
            grounding_block=grounding_block,
            style_desc=style_desc.format(topic=topic["label"]),
        ),
        max_tokens=700,
    )
    queries = []
    for line in result.text.splitlines():
        line = line.strip().strip("-").strip()
        if 3 <= len(line.split()) <= 25:
            queries.append(line)
    return queries


async def label_query(llm, settings, query: str) -> dict | None:
    try:
        result = await llm.complete(
            model=settings.model_fast, system=load_prompt("router"), user=query, max_tokens=256
        )
        intent = parse_intent(result.text)
        return {
            "artifact_type": intent.artifact_type,
            "domain": intent.domain,
            "complexity": intent.complexity,
        }
    except Exception as exc:
        print(f"  label failed ({exc}): {query[:60]!r}", flush=True)
        return None


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tag", default="kssm2")
    parser.add_argument(
        "--per-style", type=int, default=6, help="queries per (topic, style) pair"
    )
    parser.add_argument("--topics-limit", type=int, default=None, help="cap topics, for a cheap test run")
    parser.add_argument(
        "--topics-contains",
        default=None,
        help="only generate for topics whose curriculum_topic contains this substring "
        "(comma-separated for multiple), for a targeted top-up round",
    )
    parser.add_argument("--concurrency", type=int, default=8)
    parser.add_argument(
        "--no-grounding", action="store_true", help="skip RAG retrieval, topic-only generation"
    )
    args = parser.parse_args()

    settings = get_settings()
    if not settings.llm_enabled:
        raise SystemExit("ANTHROPIC_API_KEY required (see .env at repo root)")
    llm = get_llm()

    topics = all_topics()
    if args.topics_contains:
        needles = [s.strip() for s in args.topics_contains.split(",") if s.strip()]
        topics = [t for t in topics if any(n in t["curriculum_topic"] for n in needles)]
        if not topics:
            raise SystemExit(f"no topics matched --topics-contains {args.topics_contains!r}")
    if args.topics_limit:
        topics = topics[: args.topics_limit]

    n_expected = len(topics) * len(STYLES) * args.per_style
    print(
        f"generating for {len(topics)} topics x {len(STYLES)} styles x "
        f"{args.per_style} = ~{n_expected} queries"
    )

    # One retrieval per topic (not per style): reused across all 5 styles.
    excerpts: dict[str, str | None] = {}
    if not args.no_grounding:
        for topic in topics:
            excerpts[topic["curriculum_topic"]] = grounding_excerpt(topic)
        n_grounded = sum(1 for v in excerpts.values() if v)
        print(f"grounding: {n_grounded}/{len(topics)} topics matched a real passage")
    else:
        print("grounding: disabled (--no-grounding)")

    # Stage 1: generate queries, one task per (topic, style).
    gen_semaphore = asyncio.Semaphore(args.concurrency)
    pending_rows: list[dict] = []  # {query, curriculum_topic, intended_style}

    async def gen_one(topic: dict, artifact_type: str, style_desc: str):
        async with gen_semaphore:
            queries = await generate_for_topic_style(
                llm,
                settings,
                topic,
                artifact_type,
                style_desc,
                args.per_style,
                excerpts.get(topic["curriculum_topic"]),
            )
            for q in queries:
                pending_rows.append(
                    {
                        "query": q,
                        "curriculum_topic": topic["curriculum_topic"],
                        "curriculum_subject": topic["subject"],
                        "curriculum_form": topic["form"],
                        "intended_style": artifact_type,
                    }
                )

    tasks = [
        gen_one(topic, artifact_type, style_desc)
        for topic in topics
        for artifact_type, style_desc in STYLES
    ]
    done = 0
    for coro in asyncio.as_completed(tasks):
        await coro
        done += 1
        if done % 25 == 0:
            print(f"  stage 1: {done}/{len(tasks)} (topic,style) batches done, {len(pending_rows)} queries so far", flush=True)

    # Dedupe by query text, keep first curriculum tag seen.
    seen = {}
    for row in pending_rows:
        seen.setdefault(row["query"], row)
    rows = list(seen.values())
    print(f"stage 1 complete: {len(rows)} unique queries")

    # Stage 2: label with the real production router prompt.
    print(f"stage 2: labeling {len(rows)} queries with the production router prompt")
    label_semaphore = asyncio.Semaphore(args.concurrency)
    labeled_count = 0

    async def label_one(row: dict) -> dict | None:
        nonlocal labeled_count
        async with label_semaphore:
            labels = await label_query(llm, settings, row["query"])
            labeled_count += 1
            if labeled_count % 50 == 0:
                print(f"  stage 2: {labeled_count}/{len(rows)} labeled", flush=True)
            if labels is None:
                return None
            return {**row, **labels}

    final_rows = [r for r in await asyncio.gather(*(label_one(r) for r in rows)) if r]

    out_dir = HERE / "dataset" / "labeled"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"labeled_{args.tag}.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for row in final_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    by_type: dict[str, int] = {}
    by_topic_combo: dict[str, int] = {}
    style_match = 0
    for row in final_rows:
        by_type[row["artifact_type"]] = by_type.get(row["artifact_type"], 0) + 1
        combo = f"{row['curriculum_subject']}_form{row['curriculum_form']}"
        by_topic_combo[combo] = by_topic_combo.get(combo, 0) + 1
        if row["artifact_type"] == row["intended_style"]:
            style_match += 1

    print(f"\nwrote {len(final_rows)} rows to {out}")
    print("artifact_type distribution:", dict(sorted(by_type.items())))
    print("subject/form distribution:", dict(sorted(by_topic_combo.items())))
    print(
        f"teacher agreed with intended style on {style_match}/{len(final_rows)} "
        f"({100 * style_match / len(final_rows):.0f}%) -- disagreement is expected "
        "and fine, it reflects genuine router judgment, not generation noise"
    )


if __name__ == "__main__":
    asyncio.run(main())
