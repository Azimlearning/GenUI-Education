"""Build the router-distillation dataset.

Stage 1: generate diverse learner questions with the fast model (plus
deterministic non-science and gibberish injections so the student learns the
escape hatch).
Stage 2: label every query with the PRODUCTION router prompt, so the student
distills the exact deployed behavior, boundary examples included.

Outputs:
  dataset/raw/queries_<tag>.txt        stage-1 queries before labeling
  dataset/labeled/labeled_<tag>.jsonl  teacher-labeled rows

Then run prepare_dataset.py to clean/dedupe/split into dataset/clean/.

Usage (from this directory):
  ..\\..\\backend\\.venv\\Scripts\\python generate_dataset.py --n 500
  ..\\..\\backend\\.venv\\Scripts\\python generate_dataset.py --n 100 --tag dev

Costs tokens on the fast model only: roughly $0.001 per row all-in.
"""

import argparse
import asyncio
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent.parent / "backend"))

from graph.nodes.router import parse_intent  # noqa: E402
from services.llm import get_llm  # noqa: E402
from services.prompts import load_prompt  # noqa: E402
from config import get_settings  # noqa: E402

DOMAIN_TOPICS = {
    "physics": "motion, forces, energy, waves, electricity, magnetism, optics, orbits, heat",
    "chemistry": "reactions, acids and bases, bonding, states of matter, solutions, gases",
    "biology": "cells, genetics, evolution, ecosystems, human body, photosynthesis, microbes",
    "earth_space": "climate, weather, plate tectonics, oceans, the moon, planets, seasons",
    "math_adjacent": "growth and decay, probability, statistics in science, scaling, estimation",
}

# The escape hatch classes, injected deterministically (no LLM needed).
NON_SCIENCE = [
    "write me a poem about clouds",
    "what's the best pizza topping",
    "help me write a cover letter",
    "who won the world cup in 2022",
    "tell me a joke",
    "translate hello to spanish",
    "asdfghjkl",
    "qqqqqq wwww eeee",
    "hi",
    "can you fix my python code",
    "what should i name my dog",
    "plan my birthday party",
]

QUESTION_STYLES = [
    "a curious 12-year-old",
    "a high school student studying for an exam",
    "an adult who watched a documentary last night",
    "someone who wants to SEE the thing happen, using words like show me or simulate",
    "someone asking a quick factual lookup (a value, a date, a name)",
]

GEN_PROMPT = """Generate {k} distinct short science questions a learner might type into a chat app, about {domain} topics such as {topics}. Write them as {style}. One question per line, no numbering, no quotes. Mix lengths from 4 to 20 words. Do not repeat phrasings."""


async def generate_queries(n_llm: int) -> list[str]:
    settings = get_settings()
    llm = get_llm()
    per_batch = 20
    queries: list[str] = []
    domains = list(DOMAIN_TOPICS)
    batch = 0
    while len(queries) < n_llm:
        domain = domains[batch % len(domains)]
        style = QUESTION_STYLES[batch % len(QUESTION_STYLES)]
        batch += 1
        result = await llm.complete(
            model=settings.model_fast,
            system="You generate realistic user queries for a dataset. Output only the queries, one per line.",
            user=GEN_PROMPT.format(
                k=per_batch, domain=domain, topics=DOMAIN_TOPICS[domain], style=style
            ),
            max_tokens=1000,
        )
        for line in result.text.splitlines():
            line = line.strip().strip("-").strip()
            if 3 <= len(line.split()) <= 25:
                queries.append(line)
        print(f"  stage 1: {len(queries)}/{n_llm} queries", flush=True)
    return queries[:n_llm]


async def label_query(llm, settings, query: str) -> dict | None:
    try:
        result = await llm.complete(
            model=settings.model_fast,
            system=load_prompt("router"),
            user=query,
            max_tokens=256,
        )
        intent = parse_intent(result.text)
        return {
            "query": query,
            "artifact_type": intent.artifact_type,
            "domain": intent.domain,
            "complexity": intent.complexity,
        }
    except Exception as exc:
        print(f"  label failed ({exc}): {query[:60]!r}", flush=True)
        return None


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n", type=int, default=500, help="total rows to aim for")
    parser.add_argument("--tag", default="v1", help="suffix for output filenames")
    parser.add_argument("--concurrency", type=int, default=8)
    args = parser.parse_args()

    raw_dir = HERE / "dataset" / "raw"
    labeled_dir = HERE / "dataset" / "labeled"
    raw_dir.mkdir(parents=True, exist_ok=True)
    labeled_dir.mkdir(parents=True, exist_ok=True)

    settings = get_settings()
    if not settings.llm_enabled:
        raise SystemExit("ANTHROPIC_API_KEY required (see .env at repo root)")
    llm = get_llm()

    # ~12% escape-hatch rows, half of them deterministic injections.
    n_injected = max(len(NON_SCIENCE), args.n // 16)
    injected = [random.choice(NON_SCIENCE) for _ in range(n_injected)]
    n_llm = args.n - len(injected)

    print(f"stage 1: generating {n_llm} science queries with {settings.model_fast}")
    queries = await generate_queries(n_llm)
    queries += injected
    queries = list(dict.fromkeys(queries))  # dedupe, keep order
    random.shuffle(queries)
    (raw_dir / f"queries_{args.tag}.txt").write_text("\n".join(queries), encoding="utf-8")

    print(f"stage 2: labeling {len(queries)} queries with the production router prompt")
    semaphore = asyncio.Semaphore(args.concurrency)
    done = 0

    async def bounded(q: str) -> dict | None:
        nonlocal done
        async with semaphore:
            row = await label_query(llm, settings, q)
            done += 1
            if done % 50 == 0:
                print(f"  stage 2: {done}/{len(queries)} labeled", flush=True)
            return row

    rows = [r for r in await asyncio.gather(*(bounded(q) for q in queries)) if r]

    out = labeled_dir / f"labeled_{args.tag}.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    by_type: dict[str, int] = {}
    by_domain: dict[str, int] = {}
    for row in rows:
        by_type[row["artifact_type"]] = by_type.get(row["artifact_type"], 0) + 1
        by_domain[row["domain"]] = by_domain.get(row["domain"], 0) + 1
    print(f"\nwrote {len(rows)} rows to {out}")
    print("artifact_type distribution:", dict(sorted(by_type.items())))
    print("domain distribution:", dict(sorted(by_domain.items())))


if __name__ == "__main__":
    asyncio.run(main())
