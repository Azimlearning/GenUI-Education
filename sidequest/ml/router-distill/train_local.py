"""Train the router student locally (same model as train_colab.ipynb).

Reads the cleaned splits from dataset/clean/ (run prepare_dataset.py first).

Usage: python train_local.py [--epochs 40] [--out out]
Needs: pip install -r requirements.txt (TensorFlow)
"""

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent

ARTIFACT_TYPES = [
    "simulation",
    "explorable_diagram",
    "virtual_experiment",
    "data_visualization",
    "text_only",
]
DOMAINS = ["physics", "chemistry", "biology", "earth_space", "math_adjacent"]
COMPLEXITIES = [1, 2, 3]


def load_rows(path: Path) -> list[dict]:
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    print(f"{len(rows)} rows from {path}")
    return rows


def build_model(train_texts):
    import tensorflow as tf

    vectorize = tf.keras.layers.TextVectorization(
        max_tokens=8000, output_sequence_length=32, name="vectorize"
    )
    vectorize.adapt(train_texts)

    # NOTE (2026-07-18): a more heavily regularized variant (32-dim embed,
    # L2, dropout 0.5) was tried against this same ~850-row training set and
    # scored WORSE on held-out data (artifact_type 64.5% vs 65.9%, domain
    # 74.4% vs 77.8%) while converging slower, not faster. That rules out
    # "this model is too big and memorizing" as the fixable cause: capacity
    # is not the bottleneck, DATA VOLUME is. Train-vs-val gap in the logs is
    # real, but shrinking capacity doesn't close it here; more labeled rows
    # per class will. Do not re-tune these hyperparameters without first
    # trying more data (see README "Known limitation").
    inp = tf.keras.Input(shape=(1,), dtype=tf.string, name="query")
    x = vectorize(inp)
    x = tf.keras.layers.Embedding(8000, 64, name="embed")(x)
    x = tf.keras.layers.GlobalAveragePooling1D()(x)
    x = tf.keras.layers.Dense(128, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    outputs = {
        "artifact_type": tf.keras.layers.Dense(
            len(ARTIFACT_TYPES), activation="softmax", name="artifact_type"
        )(x),
        "domain": tf.keras.layers.Dense(len(DOMAINS), activation="softmax", name="domain")(x),
        "complexity": tf.keras.layers.Dense(
            len(COMPLEXITIES), activation="softmax", name="complexity"
        )(x),
    }
    model = tf.keras.Model(inp, outputs)
    model.compile(
        optimizer="adam",
        loss={k: "sparse_categorical_crossentropy" for k in outputs},
        metrics={k: ["accuracy"] for k in outputs},
    )
    return model


def main() -> None:
    import numpy as np
    import tensorflow as tf

    parser = argparse.ArgumentParser()
    parser.add_argument("--train", type=Path, default=HERE / "dataset" / "clean" / "train.jsonl")
    parser.add_argument("--test", type=Path, default=HERE / "dataset" / "clean" / "test.jsonl")
    parser.add_argument("--epochs", type=int, default=40)
    parser.add_argument("--out", type=Path, default=HERE / "out")
    args = parser.parse_args()

    train = load_rows(args.train)
    test = load_rows(args.test)

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

    x_train, y_train = xy(train)
    x_test, y_test = xy(test)

    model = build_model(x_train)
    model.fit(
        x_train,
        y_train,
        validation_split=0.1,
        epochs=args.epochs,
        batch_size=32,
        verbose=2,
        callbacks=[
            tf.keras.callbacks.EarlyStopping(
                monitor="val_loss", patience=10, restore_best_weights=True
            )
        ],
    )

    results = model.evaluate(x_test, y_test, verbose=0, return_dict=True)
    preds = model.predict(x_test, verbose=0)
    type_pred = preds["artifact_type"].argmax(axis=1)
    text_only_idx = ARTIFACT_TYPES.index("text_only")
    mask = y_test["artifact_type"] == text_only_idx
    text_only_recall = float((type_pred[mask] == text_only_idx).mean()) if mask.any() else None

    metrics = {
        "held_out_n": len(test),
        "artifact_type_acc": round(results["artifact_type_accuracy"], 4),
        "domain_acc": round(results["domain_accuracy"], 4),
        "complexity_acc": round(results["complexity_accuracy"], 4),
        "text_only_recall": round(text_only_recall, 4) if text_only_recall is not None else None,
    }
    print("\nheld-out metrics vs teacher:", json.dumps(metrics, indent=2))

    args.out.mkdir(parents=True, exist_ok=True)
    model.save(args.out / "router_student.keras")
    model.export(args.out / "saved_model")  # TF serving format
    (args.out / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (args.out / "labels.json").write_text(
        json.dumps(
            {"artifact_type": ARTIFACT_TYPES, "domain": DOMAINS, "complexity": COMPLEXITIES}
        ),
        encoding="utf-8",
    )
    try:
        converter = tf.lite.TFLiteConverter.from_saved_model(str(args.out / "saved_model"))
        converter.target_spec.supported_ops = [
            tf.lite.OpsSet.TFLITE_BUILTINS,
            tf.lite.OpsSet.SELECT_TF_OPS,  # TextVectorization needs flex ops
        ]
        (args.out / "router_student.tflite").write_bytes(converter.convert())
        print("exported tflite")
    except Exception as exc:
        print(f"tflite export skipped: {exc}")
    print(f"artifacts in {args.out}")


if __name__ == "__main__":
    main()
