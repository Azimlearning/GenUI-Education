"""Lazy full-Keras inference for the distilled router."""

import asyncio
import json
import math
import threading
import time
from dataclasses import asdict, dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np

from config import get_settings
from schemas.intent import Intent, IntentPublic


class LocalRouterError(RuntimeError):
    """The optional local router cannot safely produce a classification."""


@dataclass(frozen=True)
class LocalClassification:
    intent: IntentPublic
    confidence: float  # top artifact_type softmax probability
    latency_ms: int = 0

    def trace_payload(self) -> dict[str, Any]:
        data = asdict(self)
        data["intent"] = self.intent.model_dump()
        return data


class LocalRouter:
    """Load one ``.keras`` model on demand and run CPU inference off-loop."""

    model_filename = "router_student.keras"
    labels_filename = "labels.json"

    def __init__(self, model_dir: Path) -> None:
        self.model_dir = model_dir
        self._model: Any | None = None
        self._labels: dict[str, list[Any]] | None = None
        self._load_lock = threading.Lock()
        self._predict_lock = threading.Lock()

    def _load(self) -> tuple[Any, dict[str, list[Any]]]:
        if self._model is not None and self._labels is not None:
            return self._model, self._labels
        with self._load_lock:
            if self._model is not None and self._labels is not None:
                return self._model, self._labels
            model_path = self.model_dir / self.model_filename
            labels_path = self.model_dir / self.labels_filename
            if not model_path.is_file() or not labels_path.is_file():
                raise LocalRouterError(
                    f"model artifacts missing in {self.model_dir} "
                    f"(expected {self.model_filename} and {self.labels_filename})"
                )
            try:
                labels = json.loads(labels_path.read_text(encoding="utf-8"))
                if not all(isinstance(labels.get(key), list) for key in IntentPublic.model_fields):
                    raise ValueError("labels.json is missing a router output head")
                # Deliberately deferred: default LLM mode must not import TensorFlow.
                import tensorflow as tf

                model = tf.keras.models.load_model(model_path)
            except Exception as exc:
                raise LocalRouterError(f"could not load local router: {exc}") from exc
            self._model = model
            self._labels = labels
            return model, labels

    def classify_sync(self, query: str) -> LocalClassification:
        model, labels = self._load()
        started = time.monotonic()
        try:
            # This shape matches the training/evaluation call in train_local.py.
            with self._predict_lock:
                predictions = model.predict(np.asarray([query], dtype=object), verbose=0)
            artifact_probs = predictions["artifact_type"][0]
            artifact_index = int(np.argmax(artifact_probs))
            intent = IntentPublic(
                artifact_type=labels["artifact_type"][artifact_index],
                domain=labels["domain"][int(np.argmax(predictions["domain"][0]))],
                complexity=labels["complexity"][int(np.argmax(predictions["complexity"][0]))],
            )
            confidence = float(artifact_probs[artifact_index])
            if not math.isfinite(confidence):
                raise ValueError("artifact confidence is not finite")
        except LocalRouterError:
            raise
        except Exception as exc:
            raise LocalRouterError(f"local router inference failed: {exc}") from exc
        return LocalClassification(
            intent=intent,
            confidence=confidence,
            latency_ms=int((time.monotonic() - started) * 1000),
        )

    async def classify(self, query: str) -> LocalClassification:
        return await asyncio.to_thread(self.classify_sync, query)


def shadow_details(llm_intent: Intent, local: LocalClassification) -> dict[str, Any]:
    """Structured, query-free telemetry for comparing router decisions."""
    llm = llm_intent.public.model_dump()
    student = local.intent.model_dump()
    agreement = {field: llm[field] == student[field] for field in llm}
    return {
        "llm": llm,
        "local": local.trace_payload(),
        "agreement": {**agreement, "all": all(agreement.values())},
    }


@lru_cache
def get_local_router() -> LocalRouter:
    return LocalRouter(get_settings().router_model_dir)
