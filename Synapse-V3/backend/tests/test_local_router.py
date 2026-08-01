import json

import numpy as np

from schemas.intent import Intent
from services.local_router import LocalRouter, shadow_details


class FakeModel:
    def predict(self, values, verbose=0):
        assert values.tolist() == ["show projectile motion"]
        assert verbose == 0
        return {
            "artifact_type": np.asarray([[0.1, 0.8, 0.05, 0.03, 0.02]]),
            "domain": np.asarray([[0.9, 0.02, 0.03, 0.02, 0.03]]),
            "complexity": np.asarray([[0.05, 0.1, 0.85]]),
        }


def test_classifies_keras_outputs_without_importing_tensorflow(tmp_path):
    labels = {
        "artifact_type": [
            "simulation",
            "explorable_diagram",
            "virtual_experiment",
            "data_visualization",
            "text_only",
        ],
        "domain": ["physics", "chemistry", "biology", "earth_space", "math_adjacent"],
        "complexity": [1, 2, 3],
    }
    (tmp_path / "labels.json").write_text(json.dumps(labels))
    router = LocalRouter(tmp_path)
    router._model = FakeModel()
    router._labels = labels

    result = router.classify_sync("show projectile motion")

    assert result.intent.model_dump() == {
        "artifact_type": "explorable_diagram",
        "domain": "physics",
        "complexity": 3,
    }
    assert result.confidence == 0.8


def test_shadow_details_compares_each_router_head():
    llm = Intent(
        artifact_type="simulation",
        domain="physics",
        complexity=2,
        canonical_concept="projectile_motion",
    )

    local = type("Local", (), {})()
    local.intent = llm.public
    local.confidence = 0.91
    local.latency_ms = 8
    local.trace_payload = lambda: {
        "intent": local.intent.model_dump(),
        "confidence": local.confidence,
        "latency_ms": local.latency_ms,
    }

    details = shadow_details(llm, local)

    assert details["agreement"] == {
        "artifact_type": True,
        "domain": True,
        "complexity": True,
        "all": True,
    }
