"""Slice 10: parity-drift regression tests at the consumer/drift-class level.

bridge/gtkb-interactive-session-role-override-slice-10-regression-tests-005.md
(Codex GO at -006).

Module scope (per the slice proposal):

- Covers DCL-SESSION-ROLE-RESOLUTION-001 assertion 8 (parity between Claude
  and Codex SessionStart dispatchers) at the functional drift-class level,
  complementing ``test_check_codex_hook_parity_resolution_table.py`` which
  exercises the parity helper's internal assertions one-by-one with
  fine-grained mutations.
- This module asserts the OUTER contract a downstream consumer cares about:
  if a real-world regression to one of the three Slice 1/3/8 load-bearing
  contracts were introduced, the parity tool returns non-empty errors that
  would block CI / surface in doctor checks.
- Five tests:
    1. Canonical-state baseline — clean tree yields zero errors.
    2. StartupDecision divergence — vocabulary mismatch between dispatchers.
    3. Cache-writer divergence — regression to the pre-Slice-1 defective
       shape that conditioned cache writes on the durable role set.
    4. Marker-invalidation divergence — Slice 3 invocation removed from
       one dispatcher's ``main()``.
    5. Init-keyword regex divergence — closed-vocabulary keyword drift
       between dispatchers (load-bearing for header-of-spec compatibility).

The staging helper copies only the four files the parity tool reads, then
calls ``_resolution_table_parity_errors(tmp_root)`` directly. No real
dispatcher is invoked; no real parity-tool main() is run; failures are
deterministic and trace back to the exact assertion that fired.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_codex_hook_parity as parity  # noqa: E402

# The four files the parity helper reads. Same set as the existing
# fine-grained test module so the staging behavior is identical and any
# expansion of the helper's scope is caught by both modules.
_PARITY_RELEVANT_FILES = (
    ".claude/hooks/session_start_dispatch.py",
    ".codex/gtkb-hooks/session_start_dispatch.py",
    "scripts/session_role_resolution.py",
    "scripts/workstream_focus.py",
)


def _stage_canonical_tree(tmp_path: Path) -> Path:
    """Copy the four parity-relevant files into ``tmp_path`` and return it.

    Returning ``tmp_path`` (rather than a derived ``tmp_path/staged``)
    matches the parity helper's project-root semantics: it walks
    ``project_root / relpath`` for each file.
    """
    for relpath in _PARITY_RELEVANT_FILES:
        src = REPO_ROOT / relpath
        dest = tmp_path / relpath
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    return tmp_path


def _mutate(path: Path, old: str, new: str) -> None:
    """Replace the first occurrence of ``old`` with ``new`` in ``path``."""
    text = path.read_text(encoding="utf-8")
    assert old in text, f"expected substring not present in {path.relative_to(REPO_ROOT.parent)}: {old!r}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


# ---------------------------------------------------------------------------
# Drift class 0: canonical-pass baseline (assertion 8 negative case).
# ---------------------------------------------------------------------------


def test_canonical_tree_yields_zero_parity_errors(tmp_path: Path) -> None:
    """The clean, unmutated tree must produce zero parity errors.

    This is the negative case for assertion 8: when both dispatchers are in
    sync, the parity tool returns ``[]``. Any non-empty result on a clean
    tree would indicate a parity-tool defect, not a dispatcher drift.
    """
    staged_root = _stage_canonical_tree(tmp_path)
    errors = parity._resolution_table_parity_errors(staged_root)
    assert errors == [], f"unexpected errors on canonical tree: {errors!r}"


# ---------------------------------------------------------------------------
# Drift class 1: StartupDecision vocabulary divergence between dispatchers.
# ---------------------------------------------------------------------------


def test_startup_decision_value_drift_caught_as_parity_error(tmp_path: Path) -> None:
    """A drifted StartupDecision string value in one dispatcher must produce
    a parity error.

    Real-world failure scenario: an unattended IDE refactor or a half-applied
    enum rename leaves Claude's ``DISPATCH_AUTHORIZED`` member with a
    renamed string value while Codex still has the canonical one. The
    receiver-side dispatch tables would silently disagree on which return
    value means "dispatch authorized".
    """
    staged_root = _stage_canonical_tree(tmp_path)
    _mutate(
        staged_root / ".claude/hooks/session_start_dispatch.py",
        'DISPATCH_AUTHORIZED = "dispatch_authorized"',
        'DISPATCH_AUTHORIZED = "renamed_at_drift"',
    )
    errors = parity._resolution_table_parity_errors(staged_root)
    assert errors, "drift-class regression: parity tool returned no errors despite vocabulary drift"
    assert any(
        "Claude SessionStart dispatcher" in e and "StartupDecision.DISPATCH_AUTHORIZED" in e and "value must equal" in e
        for e in errors
    ), f"expected DISPATCH_AUTHORIZED value-divergence error in {errors!r}"


# ---------------------------------------------------------------------------
# Drift class 2: cache-writer regression to pre-Slice-1 defective shape.
# ---------------------------------------------------------------------------


def test_cache_writer_regression_to_role_set_iteration_caught(tmp_path: Path) -> None:
    """If ``_write_role_scoped_startup_relay_caches`` regresses to iterating
    ``_resolve_own_role_set()`` instead of ``_MODE_TO_ROLE_PROFILE`` keys,
    the parity tool must catch it.

    Real-world failure scenario: a well-intentioned refactor "consolidates"
    the cache-writer to consult the durable role set, breaking the
    ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001 Decision 2 contract that
    BOTH -pb and -lo caches are generated unconditionally so the
    UserPromptSubmit init-keyword matcher's keyword-keyed lookup succeeds
    regardless of the harness's durable role.
    """
    staged_root = _stage_canonical_tree(tmp_path)
    _mutate(
        staged_root / ".codex/gtkb-hooks/session_start_dispatch.py",
        "for mode in sorted(_MODE_TO_ROLE_PROFILE):",
        "for role in sorted(_resolve_own_role_set()):",
    )
    errors = parity._resolution_table_parity_errors(staged_root)
    assert errors, "drift-class regression: parity tool returned no errors despite cache-writer regression"
    # The mutation triggers both the loop-shape error AND the forbidden-
    # reference error per assertion 9; assert the loop error specifically.
    assert any(
        "Codex SessionStart dispatcher" in e and "_write_role_scoped_startup_relay_caches" in e and "must iterate" in e
        for e in errors
    ), f"expected cache-writer loop-shape error in {errors!r}"


# ---------------------------------------------------------------------------
# Drift class 3: marker-invalidation divergence (Slice 3 contract regression).
# ---------------------------------------------------------------------------


def test_marker_invalidation_removal_caught_as_parity_error(tmp_path: Path) -> None:
    """If one dispatcher's ``main()`` stops calling
    ``_invalidate_session_role_marker()`` before the dispatch fork, the
    parity tool must catch it.

    Real-world failure scenario: a hot-fix to the dispatcher's ``main()``
    "tidies up" the pre-dispatch helper calls and accidentally drops the
    Slice 3 invalidation. The session-stated marker from a previous session
    would survive into the new SessionStart, causing the resolver to honor
    a marker that should have been ephemeral.
    """
    staged_root = _stage_canonical_tree(tmp_path)
    _mutate(
        staged_root / ".claude/hooks/session_start_dispatch.py",
        "    _invalidate_session_role_marker()",
        "    pass  # drift: removed Slice 3 pre-dispatch invalidation",
    )
    errors = parity._resolution_table_parity_errors(staged_root)
    assert errors, "drift-class regression: parity tool returned no errors despite marker-invalidation removal"
    assert any(
        "Claude SessionStart dispatcher" in e
        and "main()" in e
        and "must call" in e
        and "_invalidate_session_role_marker" in e
        for e in errors
    ), f"expected marker-invalidation absence error in {errors!r}"


# ---------------------------------------------------------------------------
# Drift class 4: canonical init-keyword regex divergence between dispatchers.
# ---------------------------------------------------------------------------


def test_init_keyword_regex_drift_caught_as_parity_error(tmp_path: Path) -> None:
    """If the closed-vocabulary init-keyword regex in one dispatcher drifts
    from SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001's canonical form, the
    parity tool must catch it.

    Real-world failure scenario: a "support for additional keyword modes"
    proposal lands in only one dispatcher's regex, breaking parity. The
    receiver-side keyword recognition would diverge silently: one
    dispatcher accepts the new mode, the other doesn't, and headless
    dispatch routing becomes non-deterministic at the harness boundary.
    """
    staged_root = _stage_canonical_tree(tmp_path)
    _mutate(
        staged_root / ".codex/gtkb-hooks/session_start_dispatch.py",
        '_CANONICAL_KEYWORD_RE = re.compile(r"^::init gtkb (pb|lo)$")',
        '_CANONICAL_KEYWORD_RE = re.compile(r"^::init gtkb (pb|lo|admin)$")',
    )
    errors = parity._resolution_table_parity_errors(staged_root)
    assert errors, "drift-class regression: parity tool returned no errors despite keyword-regex drift"
    assert any("Codex SessionStart dispatcher" in e and "canonical init-keyword regex" in e for e in errors), (
        f"expected init-keyword regex divergence error in {errors!r}"
    )
