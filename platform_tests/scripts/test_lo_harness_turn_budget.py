from __future__ import annotations

import argparse
import tomllib
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from scripts import alibaba_cloud_studio_harness, ollama_harness, openrouter_harness


class HarnessModule(Protocol):
    DEFAULT_MAX_TURNS: int

    def build_arg_parser(self) -> argparse.ArgumentParser: ...


HARNESS_MODULES: tuple[HarnessModule, ...] = (
    openrouter_harness,
    ollama_harness,
    alibaba_cloud_studio_harness,
)


def _parse_default_args(module: HarnessModule) -> argparse.Namespace:
    return module.build_arg_parser().parse_args(["-p", "hello"])


def _parse_override_args(module: HarnessModule, args: Sequence[str]) -> argparse.Namespace:
    return module.build_arg_parser().parse_args(["-p", "hello", *args])


def test_lo_harness_routing_uses_owner_approved_generous_envelope() -> None:
    root = Path(__file__).resolve().parents[2]

    for provider in ("ollama", "openrouter", "alibaba-cloud-studio"):
        # The generic .api-harness tree is retired; each provider carries its own projected routing.
        routing = tomllib.loads((root / ".api-harness" / provider / "routing.toml").read_text(encoding="utf-8"))[
            "routing"
        ]
        assert routing[provider]["timeout_seconds"] == 900
        assert routing[provider]["session_timeout_seconds"] == 3600
        assert routing[provider]["max_turns"] == 600


def test_lo_harness_argparse_default_tracks_constant() -> None:
    for module in HARNESS_MODULES:
        args = _parse_default_args(module)
        assert args.max_turns == module.DEFAULT_MAX_TURNS


def test_lo_harness_argparse_accepts_per_invocation_override() -> None:
    for module in HARNESS_MODULES:
        args = _parse_override_args(module, ["--max-turns", "5"])
        assert args.max_turns == 5
