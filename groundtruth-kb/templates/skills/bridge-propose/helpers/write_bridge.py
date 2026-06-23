# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""Helper for the /gtkb-bridge-propose skill.

Writes a bridge proposal file ``bridge/<topic>-001.md`` through the no-index
bridge path under governance-safe credential-scan and work-intent controls.

Design contract:

- Credential-only pre-flight scan (``CREDENTIAL_PATTERNS +
  BASH_EXTRAS``; PII explicitly excluded, same policy as the
  ``scanner-safe-writer`` hook). Callers never get a silent write
  when credential-shaped text is present.
- Two options on hit: **abort** or **redact**. Redact normalizes
  overlapping intervals before replacement, applies in reverse
  order, and re-scans the result. A non-empty second scan raises
  :class:`RedactionResidualError` (this is a bug, not a recoverable
  user state). **No Force option.**
- File-first write: the bridge file is persisted only after credential,
  author-metadata, compliance, and work-intent checks pass. If the target file
  already exists, :class:`BridgeFileAlreadyExistsError` is raised before any
  mutation.
- Idempotency detection uses an **exact-line match** against the
  stripped ``Document: <topic>`` line — substring matching would
  false-positive on slug prefixes.
"""

from __future__ import annotations

import importlib
import json
import os
import re
import subprocess
import sys
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal


def _discover_project_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "scripts" / "bridge_author_metadata.py").is_file():
            return parent
    return Path(__file__).resolve().parents[4]


PROJECT_ROOT = _discover_project_root()
_GROUNDTRUTH_SRC = PROJECT_ROOT / "groundtruth-kb" / "src"
if _GROUNDTRUTH_SRC.is_dir() and str(_GROUNDTRUTH_SRC) not in sys.path:
    sys.path.insert(0, str(_GROUNDTRUTH_SRC))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

_credential_patterns = importlib.import_module("groundtruth_kb.governance.credential_patterns")
_prior_deliberations = importlib.import_module("groundtruth_kb.bridge.prior_deliberations")
BASH_EXTRAS = _credential_patterns.BASH_EXTRAS
CREDENTIAL_PATTERNS = _credential_patterns.CREDENTIAL_PATTERNS
ensure_author_metadata = importlib.import_module("scripts.bridge_author_metadata").ensure_author_metadata
DEFAULT_DB_PATH = _prior_deliberations.DEFAULT_DB_PATH
DEFAULT_GLOSSARY_PATH = _prior_deliberations.DEFAULT_GLOSSARY_PATH
DEFAULT_PREPOPULATION_LOG = _prior_deliberations.DEFAULT_PREPOPULATION_LOG
DEFAULT_PRE_POPULATION_LIMIT = _prior_deliberations.DEFAULT_PRE_POPULATION_LIMIT
NO_PRIOR_DELIBS_PLACEHOLDER = _prior_deliberations.NO_PRIOR_DELIBS_PLACEHOLDER
_find_prior_deliberations_section = _prior_deliberations._find_prior_deliberations_section
_format_helper_entry = _prior_deliberations._format_helper_entry
_glossary_seed_ids_for_topic = _prior_deliberations._glossary_seed_ids_for_topic
_insert_prior_deliberations_block = _prior_deliberations._insert_prior_deliberations_block
_try_open_default_db = _prior_deliberations._try_open_default_db
pre_populate_prior_deliberations = _prior_deliberations.pre_populate_prior_deliberations


if TYPE_CHECKING:

    def pre_populate_prior_deliberations(*args: Any, **kwargs: Any) -> str: ...


class BridgeFileAlreadyExistsError(RuntimeError):
    """Raised when ``bridge/<topic>-001.md`` exists on disk before phase 3.

    The skill never silently overwrites. Callers should pick a fresh
    slug (or a versioned suffix like ``-002`` for REVISED) and retry.
    """


class BridgeIndexConflictError(RuntimeError):
    """Retained historical exception name for no-index publication conflicts."""


class RedactionResidualError(RuntimeError):
    """Raised when the post-redaction re-scan still finds hits.

    This indicates a catalog/redactor bug (for example, a newly
    added pattern that the redactor doesn't cover). It is not a
    recoverable user state — the caller cannot fix it by editing
    the body. The fix is in the redactor/catalog code.
    """


class CredentialHitsFoundError(RuntimeError):
    """Raised by ``handle_hits_abort_or_redact`` when ``mode='abort'``.

    The body contained credential-shaped text and the caller chose
    to abort rather than redact.
    """


class BridgeComplianceError(RuntimeError):
    """Raised when the Codex helper path fails bridge-compliance validation.

    Codex does not currently have a Write/Edit tool hook route equivalent to
    Claude's bridge-compliance PreToolUse path. The Codex path therefore runs
    the bridge-compliance gate in audit mode before any proposal file write and
    raises this error on a deny decision.
    """


class BridgeWorkIntentError(RuntimeError):
    """Raised when bridge work-intent acquisition blocks a helper write."""


# Credential-only catalog. Iterates ``CREDENTIAL_PATTERNS + BASH_EXTRAS``
# directly — matching the scanner-safe-writer policy of excluding
# ``PII_PATTERNS`` (phone, email, ipv4) so operators can reference
# redacted samples without tripping a false-positive deny.
_SCAN_CATALOG: list[tuple[re.Pattern[str], str, str]] = [
    (spec.pattern, spec.name, spec.description) for spec in list(CREDENTIAL_PATTERNS) + list(BASH_EXTRAS)
]

WORK_INTENT_TTL_SECONDS = 300
# Session-id env-var membership is owned by scripts/gtkb_session_id.py
# (WI-4270 shared resolver unification; bridge/gtkb-session-id-shared-resolver-
# unification-003 GO at -004). Import the canonical bridge work-intent order;
# fail soft to a verbatim local copy so the helper never throws on a partial
# install. The drift-lock test platform_tests/scripts/test_gtkb_session_id.py +
# the bridge-propose work-intent test lock this fallback to the canonical
# BRIDGE_WORK_INTENT_ORDER.
try:
    from scripts.gtkb_session_id import BRIDGE_WORK_INTENT_ORDER as WORK_INTENT_SESSION_ENV_VARS
except Exception:  # pragma: no cover - helper fail-soft fallback for partial installs
    WORK_INTENT_SESSION_ENV_VARS = (
        "GTKB_BRIDGE_POLLER_RUN_ID",
        "CLAUDE_CODE_SESSION_ID",
        "CLAUDE_SESSION_ID",
        "GTKB_INHERITED_SESSION_ID",
        "CODEX_SESSION_ID",
        "CODEX_THREAD_ID",
        "ANTIGRAVITY_SESSION_ID",
        "GTKB_SESSION_ID",
    )


def resolve_work_intent_session_id(environ: Mapping[str, str] | None = None) -> str:
    """Resolve the current helper session id from supported env vars."""
    active_env = os.environ if environ is None else environ
    for name in WORK_INTENT_SESSION_ENV_VARS:
        value = active_env.get(name)
        if value and value.strip():
            return value.strip()
    expected = ", ".join(WORK_INTENT_SESSION_ENV_VARS)
    raise BridgeWorkIntentError(
        f"Bridge work-intent session id required before writing a bridge file. Set one of: {expected}."
    )


def _load_work_intent_registry(project_root: Path) -> Any:
    for scripts_dir in (project_root / "scripts", PROJECT_ROOT / "scripts"):
        if scripts_dir.is_dir() and str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
    try:
        return importlib.import_module("bridge_work_intent_registry")
    except Exception as exc:  # noqa: BLE001 - raise helper-specific guidance
        raise BridgeWorkIntentError(
            "Bridge work-intent registry unavailable; expected scripts/bridge_work_intent_registry.py to be importable."
        ) from exc


def _acquire_bridge_work_intent(thread_slug: str, session_id: str, *, project_root: Path) -> Any:
    registry = _load_work_intent_registry(project_root)
    holder = registry.current_holder(thread_slug, project_root=project_root)
    holder_session = holder.get("session_id") if holder else None
    if holder_session and holder_session != session_id:
        expires = holder.get("ttl_expires_at", "unknown expiration")
        raise BridgeWorkIntentError(
            f"Bridge work-intent for thread {thread_slug!r} is held by session "
            f"{holder_session!r} until {expires}; current session {session_id!r} "
            "cannot write. Claim another thread or wait for the holder to release/expire."
        )
    if registry.acquire(
        thread_slug,
        session_id,
        ttl_seconds=WORK_INTENT_TTL_SECONDS,
        project_root=project_root,
    ):
        return registry
    holder = registry.current_holder(thread_slug, project_root=project_root)
    holder_session = holder.get("session_id") if holder else "unknown"
    expires = holder.get("ttl_expires_at", "unknown expiration") if holder else "unknown expiration"
    raise BridgeWorkIntentError(
        f"Bridge work-intent acquire failed for thread {thread_slug!r}; "
        f"current holder is {holder_session!r} until {expires}."
    )


def _release_bridge_work_intent(registry: Any, thread_slug: str, session_id: str, *, project_root: Path) -> None:
    registry.release(thread_slug, session_id, project_root=project_root)


def scan_credential_hits(content: str) -> list[dict[str, Any]]:
    """Return every credential-class hit in ``content``.

    Iterates :data:`_SCAN_CATALOG` (``CREDENTIAL_PATTERNS +
    BASH_EXTRAS``) and collects every non-overlapping regex match
    via ``finditer``. The list may contain overlapping hits when
    multiple specs match the same span (e.g., ``aws_key`` and
    ``bash_aws_key`` both match the same ``AKIA...`` literal). The
    overlap is resolved downstream by
    :func:`_normalize_hit_intervals`.

    Args:
        content: Text to scan.

    Returns:
        List of hit dictionaries, each with keys:

        - ``pattern_name`` (str) — the canonical PatternSpec name
        - ``pattern_description`` (str) — human-readable description
        - ``span`` (tuple[int, int]) — ``(start, end)`` offsets
    """
    hits: list[dict[str, Any]] = []
    for pattern, name, description in _SCAN_CATALOG:
        for match in pattern.finditer(content):
            hits.append(
                {
                    "pattern_name": name,
                    "pattern_description": description,
                    "span": (match.start(), match.end()),
                }
            )
    return hits


def _normalize_hit_intervals(hits: list[dict[str, Any]]) -> list[tuple[int, int, str]]:
    """Merge overlapping hits into non-overlapping ``(start, end, label)`` tuples.

    Sort order is ``(start, -end)`` so longer spans come first at
    the same start offset. Overlapping intervals are merged; the
    merged interval's label is the outermost (earliest-start) spec's
    ``pattern_name``. Duplicate spans (same start, same end) collapse
    to a single interval using the first spec's name as the label.

    Args:
        hits: Output of :func:`scan_credential_hits`.

    Returns:
        Non-overlapping ``(start, end, label)`` tuples, sorted by
        start ascending. Empty if ``hits`` is empty.
    """
    if not hits:
        return []
    # Sort by start ascending, then by -end (longer span first at the same start).
    sorted_hits = sorted(hits, key=lambda h: (h["span"][0], -h["span"][1]))
    merged: list[tuple[int, int, str]] = []
    for hit in sorted_hits:
        start, end = hit["span"]
        name = hit["pattern_name"]
        if merged and start < merged[-1][1]:
            # Overlaps with previous merged interval — extend end, keep outer label.
            prev_start, prev_end, prev_name = merged[-1]
            merged[-1] = (prev_start, max(prev_end, end), prev_name)
        else:
            merged.append((start, end, name))
    return merged


def redact_credential_hits(content: str, hits: list[dict[str, Any]]) -> str:
    """Replace credential hits with ``[REDACTED:<label>]`` placeholders.

    Handles overlapping canonical matches by normalizing hits into
    non-overlapping intervals first (outer-span-wins label), then
    applying replacements in reverse-start order so earlier offsets
    remain stable against later replacements.

    Args:
        content: Original text.
        hits: Output of :func:`scan_credential_hits`. May contain
            overlaps — they are resolved internally.

    Returns:
        Redacted text. Every character in ``content`` is replaced at
        most once.
    """
    intervals = _normalize_hit_intervals(hits)
    if not intervals:
        return content
    result = content
    # Apply in reverse-start order so indices before the replacement remain valid.
    for start, end, label in sorted(intervals, key=lambda iv: iv[0], reverse=True):
        result = result[:start] + f"[REDACTED:{label}]" + result[end:]
    return result


def handle_hits_abort_or_redact(
    body: str,
    hits: list[dict[str, Any]],
    *,
    mode: Literal["abort", "redact"],
) -> str:
    """Resolve credential hits per ``mode`` or raise.

    Args:
        body: Original body text.
        hits: Output of :func:`scan_credential_hits`.
        mode: ``"abort"`` raises :class:`CredentialHitsFoundError`;
            ``"redact"`` applies :func:`redact_credential_hits` then
            re-scans and raises :class:`RedactionResidualError` if
            the second scan is non-empty.

    Returns:
        The body to write. Either the original (when ``hits`` is
        empty) or the redacted version (when ``mode='redact'`` and
        the second scan is clean).
    """
    if not hits:
        return body
    if mode == "abort":
        first = hits[0]
        raise CredentialHitsFoundError(
            f"Credential-shaped content detected: "
            f"{first['pattern_name']} ({first['pattern_description']}). "
            f"Re-invoke with mode='redact' or edit the body."
        )
    if mode == "redact":
        redacted = redact_credential_hits(body, hits)
        residual = scan_credential_hits(redacted)
        if residual:
            first = residual[0]
            raise RedactionResidualError(
                f"Post-redaction re-scan still finds credential hits: "
                f"{first['pattern_name']} ({first['pattern_description']}). "
                f"This is a catalog/redactor bug, not a recoverable user state."
            )
        return redacted
    raise ValueError(f"Unknown mode {mode!r}; expected 'abort' or 'redact'.")


def _disabled_legacy_state_update(*_args: Any, **_kwargs: Any) -> str:
    """Fail closed for removed compatibility-state publication helpers."""
    raise BridgeIndexConflictError(
        "retired bridge-index publication is disabled; use versioned bridge files plus dispatcher/TAFE state"
    )


def compose_proposal(
    slug: str,
    version: int,
    content: str,
    *,
    bridge_dir: Path | None = None,
) -> tuple[Path, str]:
    """Return the proposal target path and content without writing files."""
    bridge_root = bridge_dir if bridge_dir is not None else Path("bridge")
    return bridge_root / f"{slug}-{version:03d}.md", content


def compose_index_update(*args: Any, **kwargs: Any) -> str:
    """Historical API stub retained only to fail closed for stale callers."""
    return _disabled_legacy_state_update(*args, **kwargs)


def _relative_to_project(path: Path, project_root: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _run_bridge_compliance_audit(
    *,
    file_path: Path,
    content: str,
    project_root: Path,
) -> dict[str, Any]:
    """Run bridge-compliance-gate.py in audit mode for in-memory content."""
    gate_path = PROJECT_ROOT / ".claude" / "hooks" / "bridge-compliance-gate.py"
    payload = {
        "cwd": str(project_root.resolve()),
        "tool_input": {
            "file_path": _relative_to_project(file_path, project_root),
            "content": content,
        },
    }
    with tempfile.TemporaryDirectory(prefix="gtkb-bridge-compliance-") as tmp:
        audit_output = Path(tmp) / "audit.json"
        result = subprocess.run(
            [
                sys.executable,
                str(gate_path),
                "--audit-only",
                "--audit-output",
                str(audit_output),
            ],
            cwd=project_root,
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise BridgeComplianceError(
                "bridge-compliance audit failed to execute: "
                f"returncode={result.returncode} stdout={result.stdout!r} stderr={result.stderr!r}"
            )
        try:
            audit = json.loads(audit_output.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise BridgeComplianceError("bridge-compliance audit did not produce readable JSON") from exc
    if audit.get("decision") != "pass":
        reason = audit.get("reason") or "bridge-compliance audit denied the composed proposal"
        raise BridgeComplianceError(str(reason))
    return audit


def _update_bridge_index(*args: Any, **kwargs: Any) -> None:
    """Historical API stub retained only to fail closed for stale callers."""
    _disabled_legacy_state_update(*args, **kwargs)


def _update_bridge_index_with_composed_content(*args: Any, **kwargs: Any) -> None:
    """Historical API stub retained only to fail closed for stale callers."""
    _disabled_legacy_state_update(*args, **kwargs)


def propose_bridge(
    topic_slug: str,
    body: str,
    *,
    mode: Literal["abort", "redact"] = "abort",
    bridge_dir: Path | None = None,
    pre_populate_prior_deliberations: bool = True,
    db: Any | None = None,
    glossary_path: Path | None = None,
    pre_populate_log_path: Path | bool | None = None,
) -> Path:
    """Create ``bridge/<topic_slug>-001.md`` through the no-index bridge path.

    Phase 0 — Prior Deliberations pre-population (glossary seeding plus
    semantic-search opt-in; Phase 2 of GTKB-DA-READ-SURFACE-CORRECTION): when
    ``pre_populate_prior_deliberations=True`` (default), call
    :func:`pre_populate_prior_deliberations` on ``body`` before scanning.
    Glossary-source seeding from ``.claude/rules/canonical-terminology.md``
    plus optional semantic search (when ``db`` is provided) populates the
    proposal's ``## Prior Deliberations`` section. Authors review and
    prune. Set ``pre_populate_prior_deliberations=False`` to opt out;
    opt-out callers must include a justification in the section
    (``_No prior deliberations: <reason>._``).

    Phase 1 — Pre-flight scan: iterate ``CREDENTIAL_PATTERNS +
    BASH_EXTRAS`` over ``body``. If hits are found, resolve per
    ``mode`` via :func:`handle_hits_abort_or_redact`.

    Phase 2 — File-first write: write ``bridge/<topic_slug>-001.md`` after all
    checks pass. If the file already exists,
    :class:`BridgeFileAlreadyExistsError` is raised before any mutation.

    Args:
        topic_slug: Kebab-case slug for the bridge document. The
            file becomes ``bridge/<topic_slug>-001.md``.
        body: Proposal body text.
        mode: ``"abort"`` (default) or ``"redact"``. Controls the
            hit-resolution policy.
        bridge_dir: Parent bridge directory. Defaults to
            ``Path("bridge")``.
        pre_populate_prior_deliberations: Phase-0 pre-population flag
            (default ``True``). Set ``False`` to opt out; callers
            opting out must include a ``_No prior deliberations:_``
            justification line per the LO review-side check.
        db: Optional ``KnowledgeDB`` instance for the semantic-search
            stage of pre-population. ``None`` skips semantic search;
            glossary-source seeding still runs.
        glossary_path: Override the glossary path used for seeding.
            Defaults to ``.claude/rules/canonical-terminology.md``.
        pre_populate_log_path: Override the audit-log path. ``None``
            (default) writes to ``.gtkb-state/bridge-propose-helper/
            last-prepopulation.json``; ``False`` disables logging.

    Returns:
        Absolute path to the created bridge file.

    Raises:
        CredentialHitsFoundError: ``mode='abort'`` and hits found.
        RedactionResidualError: Redaction failed the re-scan gate.
        BridgeFileAlreadyExistsError: Target file already on disk.
        BridgeIndexConflictError: retained for historical stale-callers only;
            normal no-index writes do not raise it.
    """
    bridge_root = bridge_dir if bridge_dir is not None else Path("bridge")
    project_root = bridge_root.parent.resolve()
    bridge_file = bridge_root / f"{topic_slug}-001.md"

    # Phase 0: Prior Deliberations pre-population with semantic search opt-in.
    if pre_populate_prior_deliberations:
        body = globals()["pre_populate_prior_deliberations"](
            topic_slug,
            body,
            db=db,
            glossary_path=glossary_path,
            log_path=pre_populate_log_path,
        )

    # Phase 1: Pre-flight scan.
    hits = scan_credential_hits(body)
    body_to_write = handle_hits_abort_or_redact(body, hits, mode=mode)
    body_to_write = ensure_author_metadata(body_to_write, project_root=bridge_root.parent)

    # Phase 2: File-first write (fail-fast on existing file; no silent overwrite).
    if bridge_file.exists():
        raise BridgeFileAlreadyExistsError(
            f"{bridge_file} already exists — pick a fresh slug or bump to "
            f"-002 for a REVISED version. The skill never silently overwrites."
        )
    session_id = resolve_work_intent_session_id()
    work_intent_registry = _acquire_bridge_work_intent(topic_slug, session_id, project_root=project_root)
    bridge_file.parent.mkdir(parents=True, exist_ok=True)
    bridge_file.write_bytes(body_to_write.encode("utf-8"))
    _release_bridge_work_intent(work_intent_registry, topic_slug, session_id, project_root=project_root)
    return bridge_file


def propose_bridge_codex_non_bypass(
    topic_slug: str,
    body: str,
    *,
    version: int = 1,
    status: str = "NEW",
    mode: Literal["abort", "redact"] = "abort",
    bridge_dir: Path | None = None,
    pre_populate_prior_deliberations: bool = True,
    db: Any | None = None,
    glossary_path: Path | None = None,
    pre_populate_log_path: Path | bool | None = None,
    author_metadata: dict[str, Any] | None = None,
) -> Path:
    """Create a bridge proposal through the Codex inline-compliance path.

    This path is for Codex harnesses where ``apply_patch`` is not covered by
    the bridge-compliance PreToolUse hook. It composes the proposal body,
    ensures author metadata, runs ``bridge-compliance-gate.py --audit-only`` on
    the in-memory proposal content, and only then writes the proposal file.
    """
    bridge_root = bridge_dir if bridge_dir is not None else Path("bridge")
    project_root = bridge_root.parent.resolve()
    bridge_file, _ = compose_proposal(topic_slug, version, body, bridge_dir=bridge_root)

    if pre_populate_prior_deliberations:
        body = globals()["pre_populate_prior_deliberations"](
            topic_slug,
            body,
            db=db,
            glossary_path=glossary_path,
            log_path=pre_populate_log_path,
        )

    hits = scan_credential_hits(body)
    body_to_write = handle_hits_abort_or_redact(body, hits, mode=mode)
    body_to_write = ensure_author_metadata(
        body_to_write,
        project_root=project_root,
        explicit=author_metadata,
    )
    bridge_file, body_to_write = compose_proposal(
        topic_slug,
        version,
        body_to_write,
        bridge_dir=bridge_root,
    )

    _run_bridge_compliance_audit(
        file_path=bridge_file,
        content=body_to_write,
        project_root=project_root,
    )

    if bridge_file.exists():
        raise BridgeFileAlreadyExistsError(
            f"{bridge_file} already exists - pick a fresh slug or version. The skill never silently overwrites."
        )
    session_id = resolve_work_intent_session_id()
    work_intent_registry = _acquire_bridge_work_intent(topic_slug, session_id, project_root=project_root)
    bridge_file.parent.mkdir(parents=True, exist_ok=True)
    bridge_file.write_bytes(body_to_write.encode("utf-8"))
    _release_bridge_work_intent(work_intent_registry, topic_slug, session_id, project_root=project_root)
    return bridge_file


__all__ = [
    "BridgeFileAlreadyExistsError",
    "BridgeComplianceError",
    "BridgeIndexConflictError",
    "BridgeWorkIntentError",
    "CredentialHitsFoundError",
    "DEFAULT_GLOSSARY_PATH",
    "DEFAULT_PREPOPULATION_LOG",
    "DEFAULT_PRE_POPULATION_LIMIT",
    "NO_PRIOR_DELIBS_PLACEHOLDER",
    "RedactionResidualError",
    "WORK_INTENT_SESSION_ENV_VARS",
    "WORK_INTENT_TTL_SECONDS",
    "compose_index_update",
    "compose_proposal",
    "handle_hits_abort_or_redact",
    "pre_populate_prior_deliberations",
    "propose_bridge",
    "propose_bridge_codex_non_bypass",
    "redact_credential_hits",
    "resolve_work_intent_session_id",
    "scan_credential_hits",
]
