from __future__ import annotations

from scripts import ollama_harness as oh


def test_default_timeout_seconds_is_at_least_240() -> None:
    assert oh.DEFAULT_TIMEOUT_SECONDS >= 240.0


def test_default_max_turns_is_at_least_24() -> None:
    assert oh.DEFAULT_MAX_TURNS >= 24


def test_dispatch_uses_default_constants_when_not_overridden() -> None:
    parser = oh.build_arg_parser()
    args = parser.parse_args(["-p", "hello"])
    assert args.max_turns == oh.DEFAULT_MAX_TURNS
    assert args.timeout == oh.DEFAULT_TIMEOUT_SECONDS


def test_dispatch_accepts_per_invocation_overrides() -> None:
    parser = oh.build_arg_parser()
    args = parser.parse_args(["-p", "hello", "--max-turns", "5", "--timeout", "10.0"])
    assert args.max_turns == 5
    assert args.timeout == 10.0
