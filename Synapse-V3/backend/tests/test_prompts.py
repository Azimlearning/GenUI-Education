import re

from services.prompts import load_prompt, prompt_version


def test_prompts_load():
    for name, marker in [
        ("router", "Router"),
        ("explainer", "Explainer"),
        ("planner", "Planner"),
        ("generator", "creative-coding educator"),
        ("verifier", "adversarial reviewer"),
    ]:
        assert marker in load_prompt(name), name


def test_prompt_versions_parse_from_header():
    # Versions move as prompts are tuned; assert the header parses, not a pin.
    for name in ("router", "explainer", "planner", "generator", "verifier"):
        assert re.fullmatch(rf"{name}-v\d+", prompt_version(name)), name
