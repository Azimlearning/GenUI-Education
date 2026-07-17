"""Learning-curve study: train on 25/50/75/100% of the training set, same
architecture, no hyperparameter changes, and report held-out accuracy at
each size. Answers the question ml/IMPLEMENTATION_PLAN.md Phase 3 poses:
is data volume still the lever, or has the architecture become the ceiling?

Rising accuracy at 100% => more data still helps, gather another round.
Flat curve well below target => architecture is now the bottleneck.

Usage: python learning_curve.py
Output: out/learning_curve.json, printed table
"""

import json
import random
from pathlib import Path

from train_local import ARTIFACT_TYPES, COMPLEXITIES, DOMAINS, build_model, load_rows

HERE = Path(__file__).resolve().parent


def main() -> None:
    import numpy as np
    import tensorflow as tf

    train_all = load_rows(HERE / "dataset" / "clean" / "train.jsonl")
    test = load_rows(HERE / "dataset" / "clean" / "test.jsonl")

    def xy(subset):
        x = np.array([r["query"] for r in subset], dtype=object)
        y = {
            "artifact_type": np.array(
                [ARTIFACT_TYPES.index(r["artifact_type"]) for r in subset]
            ),
            "domain": np.array([DOMAINS.index(r["domain"]) for r in subset]),
            "complexity": np.array([COMPLEXITIES.index(r["complexity"]) for r in subset]),
        }
        return x, y

    x_test, y_test = xy(test)

    random.Random(7).shuffle(train_all)
    results = []
    for frac in (0.25, 0.5, 0.75, 1.0):
        n = int(len(train_all) * frac)
        subset = train_all[:n]
        x_train, y_train = xy(subset)

        model = build_model(x_train)
        model.fit(
            x_train,
            y_train,
            validation_split=0.1,
            epochs=40,
            batch_size=32,
            verbose=0,
            callbacks=[
                tf.keras.callbacks.EarlyStopping(
                    monitor="val_loss", patience=6, restore_best_weights=True
                )
            ],
        )
        eval_results = model.evaluate(x_test, y_test, verbose=0, return_dict=True)
        row = {
            "train_fraction": frac,
            "train_n": n,
            "artifact_type_acc": round(eval_results["artifact_type_accuracy"], 4),
            "domain_acc": round(eval_results["domain_accuracy"], 4),
            "complexity_acc": round(eval_results["complexity_accuracy"], 4),
        }
        results.append(row)
        print(
            f"n={n:5d} ({frac:.0%})  artifact_type={row['artifact_type_acc']:.4f}  "
            f"domain={row['domain_acc']:.4f}  complexity={row['complexity_acc']:.4f}"
        )

    out_dir = HERE / "out"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "learning_curve.json"
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")

    rising = results[-1]["artifact_type_acc"] > results[0]["artifact_type_acc"] + 0.03
    print(f"\nwrote {out}")
    if rising:
        print(
            "Curve is RISING: more data still helps. Do not conclude the "
            "architecture is the ceiling yet; gather another round."
        )
    else:
        print(
            "Curve is FLAT/plateaued: data volume alone is no longer moving "
            "the needle at this size. Architecture (or task ambiguity) is "
            "now the more likely lever; revisit before generating more data."
        )


if __name__ == "__main__":
    main()
