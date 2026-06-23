from __future__ import annotations

import argparse
from collections.abc import Sequence
from typing import Protocol

from scripts import ollama_harness, openrouter_harness


class HarnessModule(Protocol):
    DEFAULT_MAX_TURNS: int

    def build_arg_parser(self) -> argparse.ArgumentParser: ...


HARNESS_MODULES: tuple[HarnessModule, ...] = (openrouter_harness, ollama_harness)


def _parse_default_args(module: HarnessModule) -> argparse.Namespace:
    return module.build_arg_parser().parse_args(["-p", "hello"])


def _parse_override_args(module: HarnessModule, args: Sequence[str]) -> argparse.Namespace:
    return module.build_arg_parser().parse_args(["-p", "hello", *args])


def test_lo_harness_default_max_turns_has_verification_headroom() -> None:
    for module in HARNESS_MODULES:
        assert module.DEFAULT_MAX_TURNS >= 80


def test_lo_harness_argparse_default_tracks_constant() -> None:
    for module in HARNESS_MODULES:
        args = _parse_default_args(module)
        assert args.max_turns == module.DEFAULT_MAX_TURNS


def test_lo_harness_argparse_accepts_per_invocation_override() -> None:
    for module in HARNESS_MODULES:
        args = _parse_override_args(module, ["--max-turns", "5"])
        assert args.max_turns == 5
