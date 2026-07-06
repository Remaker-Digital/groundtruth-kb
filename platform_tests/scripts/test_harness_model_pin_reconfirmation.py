"""Spec-derived tests for harness model-pin reconfirmation doctor warnings.

These tests cover WI-4999's owner-facing model-pin drift surface:
active dispatch-capable harness pins come from the canonical harness projection,
confirmation metadata controls current/stale warning state, and non-dispatchable
or credential-adjacent surfaces remain outside the report.
"""

from __future__ import annotations

import json
from pathlib import Path

from groundtruth_kb.project.doctor import _check_harness_model_pin_reconfirmation


def _write_projection(root: Path, harnesses: list[dict[str, object]]) -> None:
    path = root / "harness-state" / "harness-registry.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "source_of_truth": "test",
                "harnesses": harnesses,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def _harness(
    harness_id: str,
    name: str,
    argv: list[str],
    *,
    active: bool = True,
    dispatchable: bool = True,
    extra_headless: dict[str, object] | None = None,
) -> dict[str, object]:
    headless: dict[str, object] = {"argv": argv}
    if extra_headless:
        headless.update(extra_headless)
    return {
        "id": harness_id,
        "harness_name": name,
        "harness_type": name,
        "status": "active" if active else "registered",
        "can_receive_dispatch": dispatchable,
        "invocation_surfaces": {"headless": headless},
    }


def _write_confirmations(root: Path, body: str) -> None:
    path = root / "config" / "agent-control" / "harness-model-pin-confirmations.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def test_passes_when_active_dispatchable_model_pins_are_currently_confirmed(tmp_path: Path) -> None:
    _write_projection(
        tmp_path,
        [
            _harness("A", "codex", ["codex", "exec", "--model", "gpt-5.5"]),
            _harness("B", "claude", ["claude", "--model=claude-opus-4-8"]),
            _harness("C", "antigravity", ["agy", "-m", "Gemini 3.5 Flash (High)"]),
        ],
    )
    _write_confirmations(
        tmp_path,
        """
schema_version = 1
stale_after_days = 99999

[confirmations.A]
model_pin = "gpt-5.5"
confirmed_at = "2026-07-06T00:00:00Z"

[confirmations.B]
model_pin = "claude-opus-4-8"
confirmed_at = "2026-07-06T00:00:00Z"

[confirmations.C]
model_pin = "Gemini 3.5 Flash (High)"
confirmed_at = "2026-07-06T00:00:00Z"
""".lstrip(),
    )

    result = _check_harness_model_pin_reconfirmation(tmp_path)

    assert result.status == "pass", result.message
    assert "A/codex=gpt-5.5" in result.message
    assert "B/claude=claude-opus-4-8" in result.message
    assert "C/antigravity=Gemini 3.5 Flash (High)" in result.message


def test_warns_when_confirmation_file_or_harness_confirmation_is_missing(tmp_path: Path) -> None:
    _write_projection(
        tmp_path,
        [
            _harness("A", "codex", ["codex", "exec", "--model", "gpt-5.5"]),
            _harness("B", "claude", ["claude", "--model", "claude-opus-4-8"]),
        ],
    )

    result = _check_harness_model_pin_reconfirmation(tmp_path)

    assert result.status == "warning"
    assert "harness-model-pin-confirmations.toml missing" in result.message
    assert "missing owner confirmation for A/codex=gpt-5.5" in result.message


def test_warns_when_confirmed_model_pin_changes_or_confirmation_is_stale(tmp_path: Path) -> None:
    _write_projection(
        tmp_path,
        [
            _harness("A", "codex", ["codex", "exec", "--model", "gpt-5.5"]),
            _harness("B", "claude", ["claude", "--model", "claude-opus-4-8"]),
        ],
    )
    _write_confirmations(
        tmp_path,
        """
schema_version = 1
stale_after_days = 1

[confirmations.A]
model_pin = "gpt-5"
confirmed_at = "2099-01-01T00:00:00Z"

[confirmations.B]
model_pin = "claude-opus-4-8"
confirmed_at = "2000-01-01T00:00:00Z"
""".lstrip(),
    )

    result = _check_harness_model_pin_reconfirmation(tmp_path)

    assert result.status == "warning"
    assert "owner confirmation changed for A/codex=gpt-5.5" in result.message
    assert "owner confirmation stale for B/claude=claude-opus-4-8" in result.message


def test_excludes_non_dispatchable_harnesses_and_credential_surfaces(tmp_path: Path) -> None:
    _write_projection(
        tmp_path,
        [
            _harness(
                "A",
                "codex",
                ["codex", "exec", "--model", "gpt-5.5"],
                extra_headless={"env": {"OPENAI_API_KEY": "sk-test-secret-value"}},
            ),
            _harness(
                "E",
                "cursor",
                ["cursor-agent", "--model", "secret-model-that-must-not-surface"],
                dispatchable=False,
                extra_headless={"env": {"CURSOR_TOKEN": "cursor-secret-value"}},
            ),
            _harness("Z", "retired", ["retired", "--model", "retired-model"], active=False),
        ],
    )
    _write_confirmations(
        tmp_path,
        """
schema_version = 1
stale_after_days = 99999

[confirmations.A]
model_pin = "gpt-5.5"
confirmed_at = "2026-07-06T00:00:00Z"
""".lstrip(),
    )

    result = _check_harness_model_pin_reconfirmation(tmp_path)

    assert result.status == "pass", result.message
    assert "A/codex=gpt-5.5" in result.message
    assert "secret-model-that-must-not-surface" not in result.message
    assert "sk-test-secret-value" not in result.message
    assert "cursor-secret-value" not in result.message
    assert "retired-model" not in result.message
