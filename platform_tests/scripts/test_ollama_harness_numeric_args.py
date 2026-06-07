from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from scripts import ollama_harness as oh

FIXTURE_MODEL_ID = "fixture-model:fixture-version"
FIXTURE_MODEL_VERSION = oh.infer_model_version(FIXTURE_MODEL_ID)


def metadata() -> oh.ModelMetadata:
    return oh.ModelMetadata(
        model_id=FIXTURE_MODEL_ID,
        model_version=FIXTURE_MODEL_VERSION,
        endpoint="http://localhost:11434",
        route_key="fixture-full",
    )


def make_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "note.txt").write_text("abcdef", encoding="utf-8")
    (root / "a.txt").write_text("needle one\n", encoding="utf-8")
    (root / "b.txt").write_text("needle two\n", encoding="utf-8")
    return root


def numeric_args(tool_name: str, value: Any) -> dict[str, Any]:
    if tool_name == "Read":
        return {"path": "note.txt", "max_chars": value}
    if tool_name == "Grep":
        return {"pattern": "needle", "path": ".", "max_results": value}
    if tool_name == "Glob":
        return {"pattern": "*.txt", "path": ".", "max_results": value}
    raise AssertionError(f"unexpected tool: {tool_name}")


@pytest.mark.parametrize("value", [3, 3.0, "3", "3.0"])
def test_read_max_chars_accepts_positive_integral_forms(tmp_path: Path, value: Any):
    root = make_root(tmp_path)

    result = oh.dispatch_tool_call("Read", numeric_args("Read", value), metadata(), root)

    assert result == "abc"


@pytest.mark.parametrize(
    ("tool_name", "value"),
    [
        ("Grep", 1),
        ("Grep", 1.0),
        ("Grep", "1"),
        ("Grep", "1.0"),
        ("Glob", 1),
        ("Glob", 1.0),
        ("Glob", "1"),
        ("Glob", "1.0"),
    ],
)
def test_max_results_accepts_positive_integral_forms(tmp_path: Path, tool_name: str, value: Any):
    root = make_root(tmp_path)

    result = oh.dispatch_tool_call(tool_name, numeric_args(tool_name, value), metadata(), root)

    assert len(result.splitlines()) == 1


@pytest.mark.parametrize(
    ("tool_name", "args", "expected"),
    [
        ("Read", {"path": "note.txt"}, "abcdef"),
        ("Grep", {"pattern": "needle", "path": "."}, "a.txt:1:needle one\nb.txt:1:needle two"),
        ("Glob", {"pattern": "*.txt", "path": "."}, "a.txt\nb.txt\nnote.txt"),
    ],
)
def test_omitted_numeric_arguments_use_existing_defaults(
    tmp_path: Path, tool_name: str, args: dict[str, Any], expected: str
):
    root = make_root(tmp_path)

    result = oh.dispatch_tool_call(tool_name, args, metadata(), root)

    assert result == expected


@pytest.mark.parametrize("tool_name", ["Read", "Grep", "Glob"])
@pytest.mark.parametrize("value", [True, False, 0, "0", -1, "-1", 1.5, "1.5", "", "abc"])
def test_numeric_arguments_reject_invalid_values_with_harness_error(tmp_path: Path, tool_name: str, value: Any):
    root = make_root(tmp_path)
    field = "max_chars" if tool_name == "Read" else "max_results"

    with pytest.raises(oh.OllamaHarnessError, match=rf"{field} must be a positive integer"):
        oh.dispatch_tool_call(tool_name, numeric_args(tool_name, value), metadata(), root)
