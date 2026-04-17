# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Tests for the scanner-safe-writer PreToolUse hook.

Required by GO ``bridge/gtkb-hook-scanner-safe-writer-008.md`` and the
``-007`` proposal's exit criteria.

Test families:

1. Self-test end-to-end (runs the hook with ``--self-test`` and inspects
   the deny record on disk + stderr marker).
2. PII pass-through (phone, email, IPv4 — must NOT trigger a deny even
   when placed inside a direct bridge write target).
3. Credential-class denial (AWS, Anthropic, Agent Red — runtime-assembled
   sample payloads to avoid triggering repo-level credential scanners).
4. Path-scope coverage (case variants + absolute POSIX and Windows paths
   must match; nested bridge/, bridgelike/, and .txt paths must not).
5. Schema-v1 assertions (the literal ``schema_version`` key present as
   the first field and value ``1`` as an ``int``).
6. Canonical/fallback stderr markers (+ a subprocess fallback test).
7. Cross-hook parity: the inline fallback catalog mirrors canonical
   ``CREDENTIAL_PATTERNS + BASH_EXTRAS`` by ``(name, pattern, flags,
   description)`` exactly, and excludes ``PII_PATTERNS``.
8. First-match ordering (a sample that matches multiple specs surfaces
   every match in catalog order).
9. Non-Write pass-through (Bash and Edit tool events do not trigger).

Sample construction note
------------------------
Agent-Red-family sample values are assembled at runtime from split
strings so repo-level credential scanners running on this source do
not see a literal credential.

Parsing note
------------
The parity parser uses the Python standard library ``ast`` module to
safely parse string literals from the hook source (via
``ast.literal_eval``) — this is explicitly the safe, non-executing
parser described in the stdlib docs and parallels the approach used in
``tests/test_credential_patterns.py`` for the credential-scan hook.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK_PATH = REPO_ROOT / "templates" / "hooks" / "scanner-safe-writer.py"


# ---------------------------------------------------------------------------
# Runtime-assembled sample payloads (avoid literal credentials in source)
# ---------------------------------------------------------------------------

_AR_LIVE_PREFIX = "ar_" + "live_"
_SK_ANT_PREFIX = "sk-" + "ant-api"
_AWS_PREFIX = "AK" + "IA"
_PAYLOAD = "abcdefghijklmnopqrst"


def _aws_sample() -> str:
    return _AWS_PREFIX + "ABCDEFGHIJKLMNOP"


def _ant_api_sample() -> str:
    return _SK_ANT_PREFIX + "03-" + "a" * 30


def _ar_live_sample() -> str:
    return _AR_LIVE_PREFIX + _PAYLOAD


# ---------------------------------------------------------------------------
# Helper: load the hook module directly (needed for _is_in_scope, _scan_content)
# ---------------------------------------------------------------------------


def _load_hook_module():
    """Import the hook module as ``scanner_safe_writer_hook`` for direct calls."""
    import importlib.util

    spec = importlib.util.spec_from_file_location("scanner_safe_writer_hook", HOOK_PATH)
    assert spec is not None and spec.loader is not None, f"cannot load spec from {HOOK_PATH}"
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def hook_module():
    """Module-scoped hook import — reused across tests for direct-API access."""
    return _load_hook_module()


# ---------------------------------------------------------------------------
# 1. Self-test
# ---------------------------------------------------------------------------


def test_self_test_emits_deny_and_writes_record(tmp_path: Path) -> None:
    """``python scanner-safe-writer.py --self-test`` must emit a deny JSON,
    print the CANONICAL_CATALOG_USED marker to stderr, and append one JSON
    line to ``.claude/hooks/scanner-safe-writer.log``.
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    result = subprocess.run(
        [sys.executable, str(HOOK_PATH), "--self-test"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env=env,
        timeout=30,
    )
    assert result.returncode == 0, f"self-test exit code {result.returncode}; stderr={result.stderr}"
    assert "CANONICAL_CATALOG_USED" in result.stderr
    stdout_data = json.loads(result.stdout.strip())
    hook_out = stdout_data["hookSpecificOutput"]
    assert hook_out["permissionDecision"] == "deny"
    assert hook_out["hookEventName"] == "PreToolUse"
    log_path = tmp_path / ".claude" / "hooks" / "scanner-safe-writer.log"
    assert log_path.exists(), "self-test did not write a deny record"
    lines = [ln for ln in log_path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    assert len(lines) == 1, f"expected exactly one deny record line, got {len(lines)}"
    record = json.loads(lines[0])
    assert record["schema_version"] == 1
    assert record["hook"] == "scanner-safe-writer"
    assert record["event"] == "deny"
    assert record["catalog_source"] == "canonical"
    assert record["hits"], "self-test deny record has no hits"


# ---------------------------------------------------------------------------
# 2. PII pass-through (scope=direct bridge file, content=PII only)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "content",
    [
        "Contact support at user@example.com for help",
        "Customer called from +18005551234 last Tuesday",
        "Caller IP was 192.168.1.100 before retry",
    ],
    ids=["email", "phone", "ipv4"],
)
def test_pii_is_allowed_in_bridge_writes(hook_module, content: str) -> None:
    """PII patterns (phone/email/ipv4) must not trigger a deny because the
    scanner-safe-writer catalog is credential-class only.
    """
    hits = hook_module._scan_content(content)
    assert hits == [], f"PII triggered credential deny unexpectedly: {hits}"


# ---------------------------------------------------------------------------
# 3. Credential denial (direct-API)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "sample_factory,expected_name",
    [
        (_aws_sample, "aws_key"),
        (_ant_api_sample, "anthropic_api_key"),
        (_ar_live_sample, "ar_live_key"),
    ],
    ids=["aws_key", "anthropic_api_key", "ar_live_key"],
)
def test_credential_content_triggers_deny(hook_module, sample_factory, expected_name: str) -> None:
    """Every credential-class sample produces at least one catalog hit whose
    first-match name is the expected spec.
    """
    sample = sample_factory()
    content = f"Sample value: {sample}\n"
    hits = hook_module._scan_content(content)
    assert hits, f"expected at least one hit for {expected_name} sample"
    names_hit = {name for name, _, _ in hits}
    assert expected_name in names_hit, f"expected {expected_name} in hits, got {sorted(names_hit)}"


# ---------------------------------------------------------------------------
# 4. Path-scope coverage
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "path",
    [
        "bridge/foo-001.md",
        "Bridge/Foo-001.md",
        "BRIDGE/FOO-001.MD",
        "BriDgE/Foo-001.Md",
        "/home/user/project/bridge/foo-001.md",
        r"C:\Users\user\project\bridge\foo-001.md",
    ],
    ids=["lower", "title", "upper", "mixed", "posix_abs", "windows_abs"],
)
def test_is_in_scope_matches_direct_bridge_paths(hook_module, path: str) -> None:
    """Direct bridge paths in various casings and separators must be in scope."""
    assert hook_module._is_in_scope(path), f"{path!r} should be in scope"


@pytest.mark.parametrize(
    "path",
    [
        "bridgelike/foo.md",
        "bridge/sub/foo.md",
        "bridge/foo.txt",
        "docs/foo.md",
    ],
    ids=["bridgelike", "nested", "wrong_ext", "unrelated_md"],
)
def test_is_in_scope_rejects_out_of_scope_paths(hook_module, path: str) -> None:
    """Non-direct bridge paths must not be in scope."""
    assert not hook_module._is_in_scope(path), f"{path!r} should NOT be in scope"


# ---------------------------------------------------------------------------
# 5. Schema v1 assertions
# ---------------------------------------------------------------------------


def test_deny_record_schema_version_is_literal_int_1(hook_module, tmp_path: Path) -> None:
    """The deny record's ``schema_version`` must be the integer ``1``."""
    old_cwd = Path.cwd()
    os.chdir(tmp_path)
    try:
        hook_module._write_deny_record(
            "bridge/foo-001.md",
            [("aws_key", "AWS access key ID (AKIA...)", (0, 10))],
            session_id="unit-test",
        )
    finally:
        os.chdir(old_cwd)
    log_path = tmp_path / ".claude" / "hooks" / "scanner-safe-writer.log"
    assert log_path.exists()
    record = json.loads(log_path.read_text(encoding="utf-8").splitlines()[0])
    assert record["schema_version"] == 1
    assert isinstance(record["schema_version"], int)


def test_deny_record_schema_version_is_first_field_in_json_text(hook_module, tmp_path: Path) -> None:
    """Raw JSON text must start with ``{"schema_version": 1`` — the literal
    key is the first field, satisfying the proposal's "schema_version: 1
    FIRST field" contract.
    """
    old_cwd = Path.cwd()
    os.chdir(tmp_path)
    try:
        hook_module._write_deny_record(
            "bridge/foo-001.md",
            [("aws_key", "AWS access key ID (AKIA...)", (0, 10))],
            session_id="unit-test",
        )
    finally:
        os.chdir(old_cwd)
    log_path = tmp_path / ".claude" / "hooks" / "scanner-safe-writer.log"
    line = log_path.read_text(encoding="utf-8").splitlines()[0]
    assert line.startswith('{"schema_version": 1,'), (
        f"raw JSON does not start with schema_version: 1 — got {line[:40]!r}"
    )


# ---------------------------------------------------------------------------
# 6. Canonical/fallback markers
# ---------------------------------------------------------------------------


def test_canonical_catalog_used_when_groundtruth_kb_on_path(tmp_path: Path) -> None:
    """With ``PYTHONPATH`` pointing at ``src``, the canonical marker is
    emitted and ``CANONICAL_CATALOG_USED`` appears on stderr.
    """
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    result = subprocess.run(
        [sys.executable, str(HOOK_PATH), "--self-test"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env=env,
        timeout=30,
    )
    assert "CANONICAL_CATALOG_USED" in result.stderr
    assert "FALLBACK_CATALOG_USED" not in result.stderr


def test_fallback_catalog_used_when_groundtruth_kb_unavailable(tmp_path: Path) -> None:
    """With isolation flags (``-S -I``), the hook cannot import
    ``groundtruth_kb`` and falls back to the inline catalog. The
    ``FALLBACK_CATALOG_USED`` marker must appear on stderr.
    """
    env: dict[str, str] = {}
    for key in ("SystemRoot", "SYSTEMROOT", "PATH", "PATHEXT", "Path", "TEMP", "TMP"):
        if key in os.environ:
            env[key] = os.environ[key]
    result = subprocess.run(
        [sys.executable, "-S", "-I", str(HOOK_PATH), "--self-test"],
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env=env,
        timeout=30,
    )
    assert "FALLBACK_CATALOG_USED" in result.stderr, (
        f"expected FALLBACK_CATALOG_USED marker; stderr was:\n{result.stderr}"
    )
    assert "CANONICAL_CATALOG_USED" not in result.stderr


# ---------------------------------------------------------------------------
# 7. Cross-hook parity (fallback ↔ canonical)
# ---------------------------------------------------------------------------
#
# The fallback parity test imports the hook once with the canonical catalog
# active (for sanity) and then re-imports with groundtruth_kb hidden from
# sys.modules to force the ImportError branch. The re-import produces a
# ``_CATALOG`` list whose entries are ``(compiled_pattern, name, description)``
# tuples — flag is implicit in the pattern object via ``.flags``.


def _load_fallback_module():
    """Import the hook with ``groundtruth_kb.governance.credential_patterns``
    hidden so the ImportError fallback branch is taken. Returns the module.
    """
    import importlib.util

    # Stash any existing import state so we can restore it after.
    saved = sys.modules.pop("groundtruth_kb.governance.credential_patterns", None)
    # Inject a sentinel that raises ImportError when the hook tries to import.
    sys.modules["groundtruth_kb.governance.credential_patterns"] = None  # type: ignore[assignment]
    try:
        spec = importlib.util.spec_from_file_location("scanner_safe_writer_fallback", HOOK_PATH)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        del sys.modules["groundtruth_kb.governance.credential_patterns"]
        if saved is not None:
            sys.modules["groundtruth_kb.governance.credential_patterns"] = saved


def test_scanner_safe_writer_fallback_exact_canonical_mirror() -> None:
    """The inline fallback must mirror ``CREDENTIAL_PATTERNS + BASH_EXTRAS``
    exactly by ``(name, pattern, flags, description)``. PII entries must
    not appear. Drift fails the build.

    Instead of textually parsing the fallback source, this test forces the
    hook's ImportError branch at runtime and inspects the resulting
    ``_CATALOG`` list. Each entry contributes ``(compiled_pattern, name,
    description)`` and the pattern's ``.flags`` carries the flag bitmask.
    """
    from groundtruth_kb.governance.credential_patterns import (
        BASH_EXTRAS,
        CREDENTIAL_PATTERNS,
        PII_PATTERNS,
    )

    fallback_module = _load_fallback_module()
    assert fallback_module._catalog_source == "fallback", "_load_fallback_module failed to force the fallback branch"

    # Translate a re.Pattern's numeric flag bitmask back to the literal the
    # canonical module carries, for a byte-level comparison.
    def _flag_literal(pattern_obj: re.Pattern[str]) -> str:
        flags = pattern_obj.flags
        parts = []
        if flags & re.IGNORECASE:
            parts.append("IGNORECASE")
        if flags & re.DOTALL:
            parts.append("DOTALL")
        return "|".join(parts)

    inline_entries: list[tuple[str, str, str, str]] = []
    for pattern_obj, name, description in fallback_module._CATALOG:
        inline_entries.append((name, pattern_obj.pattern, _flag_literal(pattern_obj), description))

    canonical = [
        (s.name, s.pattern.pattern, s.flags_literal, s.description)
        for s in list(CREDENTIAL_PATTERNS) + list(BASH_EXTRAS)
    ]

    canonical_by_name = {n: (p, f, d) for n, p, f, d in canonical}
    inline_by_name = {n: (p, f, d) for n, p, f, d in inline_entries}

    missing = set(canonical_by_name) - set(inline_by_name)
    assert not missing, f"Inline fallback missing canonical names: {sorted(missing)}"

    pii_names = {s.name for s in PII_PATTERNS}
    leaked_pii = set(inline_by_name) & pii_names
    assert not leaked_pii, f"Inline fallback includes PII patterns: {sorted(leaked_pii)}"

    extra = set(inline_by_name) - set(canonical_by_name) - pii_names
    assert not extra, f"Inline fallback has unknown names: {sorted(extra)}"

    # Names exempt from description parity: canonical descriptions for these
    # entries contain product-specific strings (e.g., "Agent Red") that must
    # not appear in adopter-facing template files per test_scaffold_smoke's
    # no-leakage contract. Pattern + flag parity still enforced — divergence
    # is in human-readable description only.
    _DESCRIPTION_PARITY_EXEMPT = {
        "ar_live_key",
        "ar_user_key",
        "ar_spa_plat_key",
        "pk_live_key",
        "arsk_key",
    }

    for name, (c_pat, c_flg, c_desc) in canonical_by_name.items():
        i_pat, i_flg, i_desc = inline_by_name[name]
        assert i_pat == c_pat, f"Pattern regex mismatch for {name}"
        assert i_flg == c_flg, f"Flags mismatch for {name}: inline={i_flg!r} canonical={c_flg!r}"
        if name in _DESCRIPTION_PARITY_EXEMPT:
            continue
        assert i_desc == c_desc, f"Description mismatch for {name}: inline={i_desc!r} canonical={c_desc!r}"


# ---------------------------------------------------------------------------
# 8. First-match ordering
# ---------------------------------------------------------------------------


def test_first_match_follows_canonical_catalog_order(hook_module) -> None:
    """A content buffer containing both ``api_key=...`` and an AWS key must
    surface ``api_key`` first because it appears first in the canonical
    ``CREDENTIAL_PATTERNS + BASH_EXTRAS`` ordering.
    """
    content = "deploy-config:\n  api_key=abcdefghijklmnopqrst\n  iam: " + _aws_sample() + "\n"
    hits = hook_module._scan_content(content)
    assert hits, "expected hits on content with multiple credential classes"
    first_name = hits[0][0]
    assert first_name == "api_key", (
        f"first hit should be api_key per canonical ordering; got {first_name}. Full hits: {[h[0] for h in hits]}"
    )


# ---------------------------------------------------------------------------
# 9. Non-Write pass-through (end-to-end via subprocess)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "tool_name",
    ["Bash", "Edit"],
)
def test_non_write_tool_events_pass_through(tmp_path: Path, tool_name: str) -> None:
    """Bash and Edit events must emit an empty ``{}`` pass JSON rather than
    a deny, even when the payload looks credential-laden.
    """
    payload = {
        "tool_name": tool_name,
        "tool_input": {
            "file_path": "bridge/foo-001.md",
            "content": "credential " + _aws_sample(),
            "command": "echo " + _aws_sample(),
        },
        "session_id": "unit-test",
    }
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT / "src")
    result = subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=tmp_path,
        env=env,
        timeout=30,
    )
    assert result.returncode == 0
    stdout = result.stdout.strip()
    assert stdout == "{}", f"expected pass '{{}}', got {stdout!r}"
    log_path = tmp_path / ".claude" / "hooks" / "scanner-safe-writer.log"
    assert not log_path.exists() or not log_path.read_text(encoding="utf-8").strip(), (
        "non-Write tool event unexpectedly wrote a deny record"
    )
