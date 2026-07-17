from config import Settings


def make(**kwargs) -> Settings:
    return Settings(_env_file=None, **kwargs)


def test_echo_when_no_key():
    assert make(anthropic_api_key="").llm_enabled is False


def test_live_when_key_present():
    assert make(anthropic_api_key="sk-test", echo_mode=False).llm_enabled is True


def test_echo_mode_overrides_key():
    assert make(anthropic_api_key="sk-test", echo_mode=True).llm_enabled is False


def test_unknown_model_price_is_zero():
    assert make().price_for("some-future-model") == (0.0, 0.0)


def test_budget_defaults():
    s = make()
    assert s.max_run_cost_usd == 0.75
    # 420, not the brief's 30: generation size + provider TTFT variance +
    # revision cycles (PLANNING.md findings 7 and 12)
    assert s.artifact_timeout_s == 420
    assert s.gen_rate_limit_per_hour == 10
