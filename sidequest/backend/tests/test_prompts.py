from services.prompts import load_prompt, prompt_version


def test_prompts_load():
    assert "Router" in load_prompt("router")
    assert "Explainer" in load_prompt("explainer")


def test_prompt_versions_parse_from_header():
    assert prompt_version("router") == "router-v1"
    assert prompt_version("explainer") == "explainer-v1"
