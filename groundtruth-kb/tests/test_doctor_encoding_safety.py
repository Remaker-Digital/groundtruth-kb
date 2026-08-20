"""WI-6681 — doctor must survive non-UTF-8 input and report it as a named failure.

These tests pin the contract established by the approved proposal at
``bridge/gtkb-wi6681-doctor-encoding-safety-005.md`` and the binding prior
deliberation ``DELIB-202667656`` (WI-5688), which rejected lossy
``errors="replace"`` decoding in doctor checks because silent character
replacement can turn a broken health surface into a false ``PASS``.

The regression under test: ``UnicodeDecodeError`` subclasses ``ValueError``,
not ``OSError``, so call sites guarding only ``OSError`` let a decode error
escape and abort the entire ``gt project doctor`` run.
"""

from __future__ import annotations

import inspect
from pathlib import Path

from groundtruth_kb.project import doctor
from groundtruth_kb.project.doctor import (
    _check_harness_local_scratchpad_boundary,
    _check_harness_metadata_freshness,
    _read_text_for_check,
)

# A cp1252 em dash. Invalid as standalone UTF-8 -- this is the exact byte that
# aborted the live run, observed in AGENTS.md at offset 24100.
INVALID_UTF8 = b"valid text \x97 more text"


def test_valid_utf8_is_returned_unchanged() -> None:
    """The success path must be transparent: text through, no finding."""
    path = Path(__file__)
    text, error = _read_text_for_check(path, "self")
    assert error is None
    assert text is not None
    assert "WI-6681" in text


def test_undecodable_file_yields_finding_not_exception(tmp_path: Path) -> None:
    """The core regression: a decode error becomes a finding, never a raise."""
    target = tmp_path / "bad.md"
    target.write_bytes(INVALID_UTF8)

    text, error = _read_text_for_check(target, "bad.md")

    assert text is None
    assert error is not None


def test_finding_names_the_path_and_byte_offset(tmp_path: Path) -> None:
    """A finding is only actionable if it says which file and where."""
    target = tmp_path / "bad.md"
    target.write_bytes(INVALID_UTF8)

    _, error = _read_text_for_check(target, "some/rel/bad.md")

    assert error is not None
    assert "some/rel/bad.md" in error
    assert "not valid UTF-8" in error
    assert "0x97" in error
    assert str(INVALID_UTF8.index(b"\x97")) in error


def test_missing_file_still_reported_as_unreadable(tmp_path: Path) -> None:
    """Broadening to ValueError must not drop the pre-existing OSError path."""
    missing = tmp_path / "nope.md"

    text, error = _read_text_for_check(missing, "nope.md")

    assert text is None
    assert error is not None
    assert "nope.md unreadable" in error


def test_strict_decoding_is_retained() -> None:
    """DELIB-202667656: no lossy decoding may be reintroduced in the helper.

    Guards against a future 'fix' that silences the failure with errors=replace
    instead of reporting it, which is precisely what WI-5688 was NO-GO'd for.
    """
    # Scan the executable body only. The docstring deliberately names
    # errors="replace" to explain why it is forbidden, so scanning raw source
    # would match that prose rather than testing the code.
    source = inspect.getsource(_read_text_for_check)
    body = source.split('"""')[-1]

    assert 'errors="replace"' not in body
    assert 'errors="ignore"' not in body
    assert "errors=" not in body
    assert 'encoding="utf-8"' in body


def test_boundary_check_fails_rather_than_aborting(tmp_path: Path) -> None:
    """End-to-end: the check that crashed the live run now FAILS cleanly.

    Asserting ``status == "fail"`` matters more than asserting "no exception".
    A check that swallowed the error and returned ``pass`` would also not raise,
    and that is the false-PASS outcome DELIB-202667656 forbids.
    """
    (tmp_path / ".claude" / "rules").mkdir(parents=True)
    (tmp_path / "AGENTS.md").write_bytes(INVALID_UTF8)
    (tmp_path / ".claude" / "rules" / "project-root-boundary.md").write_text(
        "harness-local scratchpads are non-authoritative",
        encoding="utf-8",
    )

    result = _check_harness_local_scratchpad_boundary(tmp_path)

    assert result.status == "fail"
    assert "AGENTS.md" in result.message


def test_boundary_check_passes_on_valid_input(tmp_path: Path) -> None:
    """Finding-set preservation: valid input must not gain a spurious finding.

    DELIB-202667656 required proof that a decode-safety change 'preserves the
    real warning/finding set' rather than masking or inventing findings.
    """
    (tmp_path / ".claude" / "rules").mkdir(parents=True)
    body = "\n".join(doctor._HARNESS_SCRATCHPAD_REQUIRED_TERMS)
    (tmp_path / "AGENTS.md").write_text(body, encoding="utf-8")
    (tmp_path / ".claude" / "rules" / "project-root-boundary.md").write_text(body, encoding="utf-8")

    result = _check_harness_local_scratchpad_boundary(tmp_path)

    assert "not valid UTF-8" not in result.message
    assert "unreadable" not in result.message


def test_metadata_freshness_check_fails_rather_than_aborting(tmp_path: Path) -> None:
    """A non-boundary remaining site also converts decode failure into a named FAIL.

    ``_check_harness_metadata_freshness`` previously called unguarded
    ``read_text(encoding="utf-8")`` and caught only ``OSError`` /
    ``TOMLDecodeError``, so ``UnicodeDecodeError`` aborted the doctor run.
    """
    (tmp_path / ".api-harness").mkdir()
    (tmp_path / "config" / "dispatcher").mkdir(parents=True)
    (tmp_path / ".api-harness" / "routing.toml").write_bytes(INVALID_UTF8)
    (tmp_path / "config" / "dispatcher" / "rules.toml").write_text(
        "[harnesses]\n",
        encoding="utf-8",
    )

    result = _check_harness_metadata_freshness(tmp_path)

    assert result.status == "fail"
    assert "not valid UTF-8" in result.message
    assert "0x97" in result.message


def test_unguarded_strict_read_text_sites_remain_only_in_the_helper() -> None:
    """Option (a) of the WI-6681 NO-GO: remaining strict sites go through the helper."""
    import ast

    source = Path(doctor.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    func_by_line: dict[int, str] = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            end = node.end_lineno or node.lineno
            for lineno in range(node.lineno, end + 1):
                func_by_line.setdefault(lineno, node.name)

    unguarded: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute) or node.func.attr != "read_text":
            continue
        kwargs = {kw.arg: kw.value for kw in node.keywords if kw.arg}
        if "errors" in kwargs:
            continue
        enc = kwargs.get("encoding")
        if not isinstance(enc, ast.Constant) or enc.value != "utf-8":
            continue
        unguarded.append(func_by_line.get(node.lineno, "<module>"))

    assert unguarded == ["_read_text_for_check"]
