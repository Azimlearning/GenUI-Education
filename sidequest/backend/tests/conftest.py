import pytest

import config


@pytest.fixture(autouse=True)
def echo_env(monkeypatch):
    """Force echo mode so unit tests never touch the Anthropic API,
    regardless of what the developer's environment or .env contains."""
    monkeypatch.setenv("ECHO_MODE", "true")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "")
    config.get_settings.cache_clear()
    yield
    config.get_settings.cache_clear()
