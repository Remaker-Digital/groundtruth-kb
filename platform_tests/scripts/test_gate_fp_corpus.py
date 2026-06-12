"""FAB-14 (WI-4426) HYG-040/HYG-042: cross-gate false-positive regression corpus.

Loads config/governance/gate-fp-corpus.toml and asserts the root-boundary Bash
parser ALLOWS every `bash_parser_pass` command and STILL BLOCKS every
`bash_parser_block` command. This corpus is the required regression surface for
any future change to a gate parser (SPEC-AUQ-NO-LLM-CLASSIFIER-001 /
SPEC-AUQ-POLICY-ENGINE-001 / DCL-CROSS-HARNESS-ENFORCEMENT-001).
"""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_SRC = _ROOT / "groundtruth-kb" / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from groundtruth_kb.enforcement import check_bash_command, check_path_boundary  # noqa: E402

_CORPUS_PATH = _ROOT / "config" / "governance" / "gate-fp-corpus.toml"
_CORPUS = tomllib.loads(_CORPUS_PATH.read_text(encoding="utf-8"))


@pytest.mark.parametrize("case", _CORPUS.get("bash_parser_pass", []), ids=lambda c: c["command"][:48])
def test_bash_parser_allows_false_positive_cases(case):
    allowed, reason = check_bash_command(case["command"], _ROOT)
    assert allowed, f"FP regression: {case['command']!r} falsely blocked: {reason} ({case.get('note')})"


@pytest.mark.parametrize("case", _CORPUS.get("bash_parser_block", []), ids=lambda c: c["command"][:48])
def test_bash_parser_blocks_genuine_violations(case):
    allowed, _reason = check_bash_command(case["command"], _ROOT)
    assert not allowed, f"True-negative: {case['command']!r} should still be blocked ({case.get('note')})"


@pytest.mark.parametrize("case", _CORPUS.get("powershell_parser_pass", []), ids=lambda c: c["command"][:48])
def test_powershell_parser_allows_false_positive_cases(case):
    allowed, reason = check_bash_command(case["command"], _ROOT)
    assert allowed, f"PowerShell FP regression: {case['command']!r} falsely blocked: {reason} ({case.get('note')})"


@pytest.mark.parametrize("case", _CORPUS.get("codex_apply_patch_pass", []), ids=lambda c: c["path"][:48])
def test_codex_apply_patch_paths_allow_in_root_cases(case):
    allowed, reason = check_path_boundary(case["path"], _ROOT)
    assert allowed, f"Codex apply_patch FP regression: {case['path']!r} falsely blocked: {reason}"


@pytest.mark.parametrize("case", _CORPUS.get("codex_apply_patch_block", []), ids=lambda c: c["path"][:48])
def test_codex_apply_patch_paths_block_genuine_violations(case):
    allowed, _reason = check_path_boundary(case["path"], _ROOT)
    assert not allowed, f"True-negative: {case['path']!r} should still be blocked ({case.get('note')})"
