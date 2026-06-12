#!/usr/bin/env python3
"""
PreToolUse hook: bridge compliance gate.

Checks if a file being written matches a bridge proposal in NEW, REVISED, or
NO-GO status. Emits an ask checkpoint if the proposal hasn't been approved.

Uses latest-status-per-document parsing: only the first status line after
each Document: header is considered (newest-first per bridge protocol).

Hook type: PreToolUse (tools: Write, Edit)

Copyright 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC.
All rights reserved.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

for _parent in Path(__file__).resolve().parents:
    if (_parent / "scripts" / "bridge_author_metadata.py").is_file():
        if str(_parent) not in sys.path:
            sys.path.insert(0, str(_parent))
        _gt_src = _parent / "groundtruth-kb" / "src"
        if _gt_src.is_dir() and str(_gt_src) not in sys.path:
            sys.path.insert(0, str(_gt_src))
        break

try:
    from scripts.bridge_author_metadata import (
        BRIDGE_AUTHOR_METADATA_STATUSES,
        REQUIRED_AUTHOR_METADATA_FIELDS,
        author_metadata_gaps_for_content,
    )
except Exception:  # pragma: no cover - hook fail-soft fallback for partial installs
    BRIDGE_AUTHOR_METADATA_STATUSES = frozenset({"NEW", "REVISED", "GO", "NO-GO", "VERIFIED", "ADVISORY", "DEFERRED"})
    REQUIRED_AUTHOR_METADATA_FIELDS = (
        "author_identity",
        "author_harness_id",
        "author_session_context_id",
        "author_model",
        "author_model_version",
        "author_model_configuration",
    )

    def author_metadata_gaps_for_content(content: str) -> list[str]:
        values = dict(re.findall(r"^(author_[a-z0-9_]+):\s*(.*?)\s*$", content, re.IGNORECASE | re.MULTILINE))
        return [field for field in REQUIRED_AUTHOR_METADATA_FIELDS if not values.get(field)]


BRIDGE_INDEX_FILENAME = "bridge/INDEX.md"
WRITE_TOOLS = {"Write", "Edit"}
PENDING_PREFLIGHT_STATUSES = {"NEW", "REVISED"}
# Session-id env-var membership is owned by scripts/gtkb_session_id.py
# (WI-4270 shared resolver unification; bridge/gtkb-session-id-shared-resolver-
# unification-003 GO at -004). Import the canonical bridge work-intent order;
# fail soft to a verbatim local copy so the hook never throws on a partial
# install (same pattern as the bridge_author_metadata import above). The
# drift-lock test platform_tests/scripts/test_gtkb_session_id.py + the gate
# work-intent test lock this fallback to the canonical BRIDGE_WORK_INTENT_ORDER.
try:
    from scripts.gtkb_session_id import BRIDGE_WORK_INTENT_ORDER as WORK_INTENT_SESSION_ENV_VARS
except Exception:  # pragma: no cover - hook fail-soft fallback for partial installs
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
SPEC_LINK_HEADING_RE = re.compile(
    r"^#{1,6}\s*(?:relevant\s+|linked\s+|governing\s+)?specification(?:\s+links?|\s+references?|\s*)$",
    re.IGNORECASE,
)
# A heading line whose text begins with the Specification Links section name
# but which SPEC_LINK_HEADING_RE rejects (e.g. a trailing parenthetical). Used
# to tell a heading-format misdetection (ask) apart from a genuinely absent
# section (deny). See _specification_links_heading_misdetected.
SPEC_LINK_HEADING_NEAR_MISS_RE = re.compile(
    r"(?:relevant\s+|linked\s+|governing\s+)?specification\b",
    re.IGNORECASE,
)
SPEC_LINK_TOKEN_RE = re.compile(
    r"\b(?:SPEC|GOV|ADR|DCL|PB|REQ)-[A-Z0-9][A-Z0-9_.-]*\b"
    r"|(?:^|[`(\s])(?:\.claude/rules|groundtruth-kb/docs|docs|bridge)/[^\s`)]+",
    re.IGNORECASE | re.MULTILINE,
)
SPEC_PLACEHOLDER_LINE_RE = re.compile(
    r"^[\s>*`_\-:]*(?:tbd|todo|none|n/a|not applicable|no relevant)[\s.`_\-:]*$",
    re.IGNORECASE,
)
OWNER_DECISIONS_PLACEHOLDER_LINE_RE = re.compile(
    r"^[\s>*`_\-:]*"
    r"(?:tbd|todo|none|n/a|not applicable|no relevant(?: owner decisions?)?)"
    r"[\s.`_\-:]*$",
    re.IGNORECASE,
)
SPEC_TEST_HEADING_RE = re.compile(
    r"^#{1,6}\s*(?:spec(?:ification)?[-\s]+to[-\s]+test|specification[-\s]+derived\s+verification)",
    re.IGNORECASE | re.MULTILINE,
)
COMMAND_EVIDENCE_RE = re.compile(
    r"\b(?:python -m pytest|pytest|ruff|npm test|pnpm test|uv run|make test)\b",
    re.IGNORECASE,
)
APPLICABILITY_PREFLIGHT_HEADING_RE = re.compile(
    r"^#{1,6}\s*applicability\s+preflight\s*$",
    re.IGNORECASE,
)
PREFLIGHT_PACKET_HASH_RE = re.compile(
    r"\bpacket_hash\s*:\s*`?sha256:[0-9a-f]{64}`?",
    re.IGNORECASE,
)
PREFLIGHT_MISSING_REQUIRED_RE = re.compile(
    r"\bmissing_required_specs\s*:\s*(?:\[\s*\]|`?\[\s*\]`?|none|None|NONE)",
    re.IGNORECASE,
)

# Owner Decisions / Input section gate (Sub-slice C of GTKB-GOV-AUQ-ENFORCEMENT-STACK).
# Per bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-c-bridge-gate-003.md
# (Codex GO at -004): conditional check that fires only when proposal/report content
# indicates owner-approval scope. Verdict files (GO/NO-GO/VERIFIED first line) are
# excluded — they are evidence narratives, not approval claims.
OWNER_DECISIONS_HEADING_RE = re.compile(
    r"^#{1,6}\s*Owner Decisions(?:\s*/\s*Input)?\s*$",
    re.IGNORECASE | re.MULTILINE,
)
DEFERRED_REASON_RE = re.compile(r"\bdeferr(?:al|ed)\s+reason\b|\breason\s*:", re.IGNORECASE)
DEFERRED_CLEAR_CONDITION_RE = re.compile(
    r"\bclear\s+condition\b|\bresume\s+condition\b|\bunblock(?:ing)?\s+condition\b",
    re.IGNORECASE,
)
OWNER_EVIDENCE_RE = re.compile(
    r"\b(?:DELIB-[A-Z0-9_.-]+|AUQ|AskUserQuestion|owner\s+(?:decision|directive|input|approval))\b",
    re.IGNORECASE,
)
OWNER_APPROVAL_MARKER_RES = (
    # Marker 1: cites Sub-slice B's VERIFIED rule (the AUQ-only rule)
    re.compile(
        r"gtkb-gov-askuserquestion-enforcement-stack-slice-b-prime-rule-006\.md",
        re.IGNORECASE,
    ),
    # Marker 2: AUQ + decision-context phrase within ~200 chars
    re.compile(
        r"\b(?:AUQ|AskUserQuestion)\b[^.]{0,200}\b(?:answer|approval|decision|directive|authorize|authorization)\b",
        re.IGNORECASE,
    ),
)

# Project-linkage metadata gate (DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001).
# WI-3314: metadata-presence enabling slice. Implementation bridge proposals
# (NEW/REVISED status, not bridge_kind-exempt) must carry three machine-readable
# metadata lines so a proposal self-documents its project provenance.
# CLAUSE-PROJECT-METADATA-PRESENT is enforced here; CLAUSE-VERDICT-FILES-EXCLUDED
# is satisfied by the NEW/REVISED-only status gate; CLAUSE-NON-IMPLEMENTATION-EXEMPT
# is satisfied by the bridge_kind exempt set. CLAUSE-PROJECT-AUTH-LIVE-CHECK
# (live MemBase authorization lookup) is deferred to WI-3315.
PROJECT_AUTHORIZATION_LINE_RE = re.compile(r"^Project Authorization:\s*PAUTH-[A-Z0-9-]+\s*$", re.MULTILINE)
PROJECT_LINE_RE = re.compile(r"^Project:\s*[A-Z0-9-]+\s*$", re.MULTILINE)
WORK_ITEM_LINE_RE = re.compile(
    r"^Work Item:\s*(?:WI-\d+|WI-AUTO-[A-Z0-9-]+|GTKB-[A-Z0-9-]+|WORKLIST-[A-Z0-9-]+)\s*$", re.MULTILINE
)
BRIDGE_KIND_LINE_RE = re.compile(r"^bridge_kind:\s*(\S+)", re.IGNORECASE | re.MULTILINE)
BRIDGE_KIND_METADATA_EXEMPT = frozenset(
    {
        "spec_intake",
        "governance_review",
        "loyal_opposition_advisory",
        "governance_advisory",
        "index_reconciliation",
        "operational_state_change",
        "lo_verdict",
    }
)
PROJECT_METADATA_STATUSES = frozenset({"NEW", "REVISED"})

# WI-project membership gate (DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001/
# CLAUSE-BRIDGE-WI-PROJECT-MEMBERSHIP + DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-
# MANDATORY-001/CLAUSE-PROJECT-AUTH-LIVE-CHECK).
# WI-3315: when a NEW/REVISED implementation proposal carries all three
# project-linkage metadata lines, the cited Work Item must have an active
# membership in the cited Project, and the cited Project Authorization must be
# active, unexpired, project-matched, and must include (not exclude) the Work
# Item. The check fails open on any DB-access error so the gate never blocks on
# infrastructure failure. Verdict files (GO/NO-GO/VERIFIED) never reach this
# check because it lives inside the NEW/REVISED metadata branch.
PROJECT_AUTHORIZATION_VALUE_RE = re.compile(r"^Project Authorization:\s*(PAUTH-[A-Z0-9-]+)\s*$", re.MULTILINE)
PROJECT_VALUE_RE = re.compile(r"^Project:\s*([A-Z0-9-]+)\s*$", re.MULTILINE)
WORK_ITEM_VALUE_RE = re.compile(
    r"^Work Item:\s*(WI-\d+|WI-AUTO-[A-Z0-9-]+|GTKB-[A-Z0-9-]+|WORKLIST-[A-Z0-9-]+)\s*$", re.MULTILINE
)
TARGET_PATHS_LINE_RE = re.compile(r"^\s*target_paths?\s*[:=]\s*(.+)", re.IGNORECASE | re.MULTILINE)
KB_MUTATION_DECLARATION_RE = re.compile(
    r"\b(?:"
    r"MemBase\s+mutation|"
    r"mutat(?:e|es|ing)\s+MemBase|"
    r"(?:insert|inserts|inserting|inserted|write|writes|writing|create|creates|creating|add|adds|adding)\s+(?:(?:a|an|new)\s+){0,2}"
    r"(?:GOV|SPEC|ADR|DCL|PB|REQ|Deliberation Archive|project|work item|MemBase)\b[^.\n]{0,160}"
    r"\b(?:record|version|row|entry)\b|"
    r"(?:GOV|SPEC|ADR|DCL|PB|REQ)\b[^.\n]{0,120}\b(?:supersession|version\s+\d+|v\d+)\b|"
    r"\bretir(?:e|es|ing)\b[^.\n]{0,120}\b(?:project|work item|spec|specification)\b|"
    r"\bgroundtruth\.db\b"
    r")",
    re.IGNORECASE,
)
KB_MUTATION_NEGATION_RE = re.compile(
    r"\b(?:no|not|without|does\s+not|do\s+not|performs?\s+no|creates?\s+no|executes?\s+no)\b"
    r"[^.\n]{0,100}\b(?:MemBase|KB|groundtruth\.db)\b[^.\n]{0,80}\b(?:mutation|write|insert|change|edit)s?\b",
    re.IGNORECASE,
)

ADVISORY_REPORT_HEADER_FIELDS = ("bridge_kind", "Document", "Version", "Author", "Date")
ADVISORY_REPORT_SECTIONS = (
    "Source",
    "Claim",
    "Owner Decision Needed",
    "Recommended Prime Action",
    "Classification Slot",
)
AUDIT_OUTPUT_RELATIVE_PATH = Path(".codex") / "gtkb-hooks" / "last-bridge-audit.json"


def _record_gate_denial(pattern_id: str, subject: str, reason: str, *, root: Path | None = None) -> None:
    path = Path(os.environ.get("GTKB_GATE_DENIALS_PATH", ".gtkb-state/gate-denials.jsonl"))
    base = root or Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()
    if not path.is_absolute():
        path = base / path
    record = {
        "schema_version": 1,
        "timestamp_utc": _dt.datetime.now(tz=_dt.UTC).isoformat().replace("+00:00", "Z"),
        "gate": "bridge-compliance-gate",
        "pattern_id": pattern_id,
        "command_hash": hashlib.sha256(subject.encode("utf-8")).hexdigest(),
        "reason": reason,
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, sort_keys=True) + "\n")
    except OSError:
        pass


def _ancestor_or_self(root: Path, cwd_path: Path) -> bool:
    """Return True when ``root`` is ``cwd_path`` itself or one of its parents.

    The canonical GT-KB root always contains the session cwd: a canonical
    session runs at the root (or a subdirectory), and a linked worktree lives
    under ``<canonical>/.claude/worktrees/``. A resolver result that is neither
    cwd_path nor an ancestor of it does not describe this session and is
    discarded, so a synthetic cwd passed by a unit test is not silently
    redirected to the live project root.
    """
    try:
        resolved_root = root.resolve()
        resolved_cwd = cwd_path.resolve()
    except OSError:
        return False
    return resolved_root == resolved_cwd or resolved_root in resolved_cwd.parents


def _is_under_claude_worktrees(path: Path) -> bool:
    parts = path.resolve().parts
    return any(left == ".claude" and right == "worktrees" for left, right in zip(parts, parts[1:], strict=False))


def _has_scratch_boundary_between(root: Path, cwd_path: Path) -> bool:
    try:
        rel_parts = cwd_path.resolve().relative_to(root.resolve()).parts
    except ValueError:
        return False
    return any(part in {".tmp", ".gtkb-state"} for part in rel_parts)


def _nearest_marker_root(cwd_path: Path) -> Path | None:
    try:
        resolved_cwd = cwd_path.resolve()
    except OSError:
        resolved_cwd = cwd_path
    for candidate in (resolved_cwd, *resolved_cwd.parents):
        if not (candidate / "groundtruth.toml").is_file():
            continue
        if _has_scratch_boundary_between(candidate, resolved_cwd):
            return None
        return candidate
    return None


def _git_common_dir_root(cwd_path: Path) -> Path | None:
    """Resolve the canonical root via ``git rev-parse --git-common-dir``.

    The shared git directory's parent is the canonical main-worktree root,
    identical from the main worktree and from a linked worktree. Prefers
    ``--path-format=absolute`` (git >= 2.31) and falls back to the bare form
    resolved relative to ``cwd_path``. Returns None on any failure or when the
    resolved parent lacks ``groundtruth.toml``.
    """
    for args in (
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
        ["git", "rev-parse", "--git-common-dir"],
    ):
        try:
            out = subprocess.check_output(args, cwd=str(cwd_path), text=True, stderr=subprocess.DEVNULL).strip()
        except (OSError, subprocess.SubprocessError):
            continue
        if not out:
            continue
        common_dir = (cwd_path / out).resolve()
        candidate = common_dir.parent
        if (candidate / "groundtruth.toml").is_file():
            return candidate
    return None


def _canonical_project_root(cwd_path: Path) -> Path:
    """Resolve the canonical GT-KB project root for project-state access.

    Bridge governance state -- ``groundtruth.db``, the live ``bridge/INDEX.md``,
    and the audit-output tree -- exists only at the canonical main-worktree
    root. A session running inside a ``.claude/worktrees/*`` linked worktree has
    a cwd that is NOT that root; trusting it makes the gate read an empty
    scaffold database and falsely block a valid proposal.

    Resolution is fail-soft and uses ``cwd_path`` directly; package-level root
    helpers rely on process cwd and are therefore unsafe for hook unit tests that
    pass a synthetic cwd. Linked worktrees resolve through ``git-common-dir``;
    normal subdirectories use the nearest ``groundtruth.toml`` marker; scratch
    directories under ``.tmp`` or ``.gtkb-state`` stay hermetic and fall back
    to ``cwd_path``.
    """
    if _is_under_claude_worktrees(cwd_path):
        git_root = _git_common_dir_root(cwd_path)
        if git_root is not None and _ancestor_or_self(git_root, cwd_path):
            return git_root
    marker_root = _nearest_marker_root(cwd_path)
    if marker_root is not None:
        return marker_root
    git_root = _git_common_dir_root(cwd_path)
    if (
        git_root is not None
        and _ancestor_or_self(git_root, cwd_path)
        and not _has_scratch_boundary_between(git_root, cwd_path)
    ):
        return git_root
    return cwd_path


def _parse_bridge_index(index_path: Path) -> dict[str, str]:
    """
    Returns {document_name: latest_status}.
    Only the first status line per document entry is considered (latest version).
    """
    result: dict[str, str] = {}
    current_doc: str | None = None
    current_doc_status_seen: bool = False

    try:
        lines = index_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return result

    for line in lines:
        line = line.strip()
        if line.startswith("Document:"):
            current_doc = line.removeprefix("Document:").strip()
            current_doc_status_seen = False
        elif current_doc and not current_doc_status_seen:
            for status in ("VERIFIED", "GO", "NO-GO", "ADVISORY", "DEFERRED", "REVISED", "NEW"):
                if line.startswith(status + ":"):
                    result[current_doc] = status
                    current_doc_status_seen = True
                    break

    return result


def _first_nonblank_line(content: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped:
            return stripped
    return ""


def _is_bridge_markdown_file(file_path: str) -> bool:
    normalized = file_path.replace("\\", "/")
    if not normalized.endswith(".md"):
        return False
    return "/bridge/" in f"/{normalized}" and not normalized.endswith("/bridge/INDEX.md")


def _extract_bridge_id_from_path(file_path: str) -> str | None:
    filename = Path(file_path.replace("\\", "/")).name
    match = re.match(r"(?P<bridge_id>.+)-\d{3}\.md$", filename)
    return match.group("bridge_id") if match else None


def _resolve_work_intent_session_id(payload: dict) -> str:
    for env_var in WORK_INTENT_SESSION_ENV_VARS:
        env_value = os.environ.get(env_var, "").strip()
        if env_value:
            return env_value
    session_id = str(payload.get("session_id") or "").strip()
    if session_id:
        return session_id
    return ""


def _work_intent_project_root(cwd_path: Path, file_path: str) -> Path:
    candidate_path = Path(file_path)
    if not candidate_path.is_absolute():
        candidate_path = cwd_path / candidate_path
    try:
        bridge_dir = candidate_path.resolve().parent
    except OSError:
        bridge_dir = candidate_path.parent
    if bridge_dir.name.lower() == "bridge":
        candidate_root = bridge_dir.parent
        if (candidate_root / "groundtruth.toml").is_file():
            return candidate_root.resolve()
    return _canonical_project_root(cwd_path)


def _bridge_work_intent_deny_reason(*, cwd_path: Path, file_path: str, payload: dict) -> str | None:
    if not _is_bridge_markdown_file(file_path):
        return None
    bridge_id = _extract_bridge_id_from_path(file_path)
    if bridge_id is None:
        return None
    session_id = _resolve_work_intent_session_id(payload)
    if not session_id:
        return (
            f"[Governance] Bridge file Write blocked: no harness session id is available for thread "
            f"'{bridge_id}'. Acquire a work-intent claim first with: "
            f"python scripts/bridge_claim_cli.py claim {bridge_id} --session-id <session-id>"
        )
    try:
        from scripts.bridge_work_intent_registry import WorkIntentRegistryError, current_holder
    except Exception as exc:  # pragma: no cover - defensive runtime guard.
        return f"[Governance] Bridge file Write blocked: work-intent registry unavailable: {exc}"
    try:
        holder = current_holder(bridge_id, project_root=_work_intent_project_root(cwd_path, file_path))
    except WorkIntentRegistryError as exc:
        return f"[Governance] Bridge file Write blocked: work-intent registry error for '{bridge_id}': {exc}"
    if holder is None:
        return (
            f"[Governance] Bridge file Write blocked: no prior claim for thread '{bridge_id}'. "
            "Per .claude/rules/file-bridge-protocol.md 'Mandatory Pre-Drafting Claim Step', run: "
            f"python scripts/bridge_claim_cli.py claim {bridge_id}"
        )
    if holder.get("session_id") != session_id:
        return (
            f"[Governance] Bridge file Write blocked: thread '{bridge_id}' is claimed by "
            f"{holder.get('session_id')} until {holder.get('ttl_expires_at')}. Acquire claim first: "
            f"python scripts/bridge_claim_cli.py claim {bridge_id}"
        )
    return None


# Body status-token rule (GTKB-GOV-PROPOSAL-STANDARDS Slice 1; owner decision
# DELIB-S382-PROPOSAL-STANDARDS-COMPLETION-SCOPE; GO at
# bridge/gtkb-gov-proposal-standards-slice1-023.md). Versioned bridge files
# (bridge/<slug>-NNN.md) must begin with a canonical status token on the first
# non-blank line so the file is self-describing and the first line is a
# reliable routing signal. See .claude/rules/file-bridge-protocol.md
# "Body Status-Token Rule".
def _first_line_is_recognized_status(first_line: str) -> bool:
    """True when ``first_line`` is a canonical bridge status token.

    Mirrors the gate's existing first-line recognition union (the ADVISORY,
    GO/NO-GO/VERIFIED, and PENDING_PREFLIGHT_STATUSES {NEW, REVISED} checks in
    ``_deny_reason_for_content``) plus the non-actionable ``DEFERRED`` and
    terminal ``WITHDRAWN`` statuses used throughout bridge/INDEX.md. Errs toward acceptance (``.startswith`` for
    verdicts) so the body-status-token rule never false-blocks a line the rest
    of the gate would recognize.
    """
    return (
        first_line == "ADVISORY"
        or first_line == "DEFERRED"
        or first_line == "WITHDRAWN"
        or first_line in PENDING_PREFLIGHT_STATUSES
        or first_line.startswith(("GO", "NO-GO", "VERIFIED"))
    )


def _ondisk_first_nonblank_line(file_path: str) -> str | None:
    """Return the current on-disk first non-blank line, or None when the file
    does not exist or cannot be read. Used for body-status-token grandfathering
    so the rule does not retroactively break historical files on overwrite.
    """
    try:
        path = Path(file_path)
        if not path.is_file():
            return None
        with path.open("r", encoding="utf-8-sig") as handle:
            for raw_line in handle:
                stripped = raw_line.strip()
                if stripped:
                    return stripped
        return ""
    except OSError:
        return None


def _body_status_token_violation(file_path: str, content: str) -> bool:
    """True when a versioned bridge file's first non-blank line is not a
    recognized status token AND the file is not grandfathered.

    New files (and overwrites of files that currently have a canonical first
    line) must keep a canonical first line. Files that already exist on disk
    with a non-canonical first line are grandfathered. Non-versioned bridge
    markdown (no ``-NNN`` suffix, e.g. bridge/INDEX.md is already excluded by
    ``_is_bridge_markdown_file``) is not subject to the rule.
    """
    if _extract_bridge_id_from_path(file_path) is None:
        return False
    if _first_line_is_recognized_status(_first_nonblank_line(content)):
        return False
    ondisk_first = _ondisk_first_nonblank_line(file_path)
    # Block when the file is new (no on-disk line) or its current first line is
    # already canonical (an overwrite must not corrupt a valid status token).
    # Grandfather only when the on-disk first line is already non-canonical.
    return ondisk_first is None or _first_line_is_recognized_status(ondisk_first)


def _collect_section_lines(lines: list[str], start: int) -> list[str]:
    """Collect section body lines, ignoring headings inside backtick fences."""
    section: list[str] = []
    in_fence = False
    for line in lines[start:]:
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            section.append(line)
            continue
        if not in_fence and stripped.startswith("#"):
            break
        section.append(line)
    return section


def _has_concrete_spec_links(content: str) -> bool:
    lines = content.splitlines()
    start: int | None = None
    for idx, line in enumerate(lines):
        if SPEC_LINK_HEADING_RE.match(line.strip()):
            start = idx + 1
            break
    if start is None:
        return False

    section = _collect_section_lines(lines, start)
    section_text = "\n".join(section).strip()
    if not section_text or not SPEC_LINK_TOKEN_RE.search(section_text):
        return False
    # Per-line placeholder evaluation: a line carrying a genuine spec-link
    # citation token is concrete-citation rationale and is exempt from the
    # placeholder test -- its rationale prose may legitimately contain a word
    # like "none" or "n/a". The section is placeholder-content only when a
    # line WITHOUT any spec-link token is itself a placeholder line.
    for section_line in section:
        stripped_line = section_line.strip()
        if not stripped_line or SPEC_LINK_TOKEN_RE.search(stripped_line):
            continue
        if SPEC_PLACEHOLDER_LINE_RE.match(stripped_line):
            return False
    return True


def _specification_links_heading_misdetected(content: str) -> bool:
    """True when no strict Specification Links heading matched but a near-miss
    heading line is present.

    The near-miss class is a Markdown heading line whose text begins with the
    Specification Links section name -- optionally a relevant/linked/governing
    qualifier -- that SPEC_LINK_HEADING_RE rejects, e.g. a trailing
    parenthetical such as ``## Specification Links (carried forward)``. A
    genuinely absent section has no such heading line at all; it is not a
    misdetection. A misdetection should ask (the author wrote the section); an
    absent section should still deny.
    """
    near_miss = False
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("#"):
            continue
        if SPEC_LINK_HEADING_RE.match(stripped):
            return False
        if SPEC_LINK_HEADING_NEAR_MISS_RE.match(stripped.lstrip("#").strip()):
            near_miss = True
    return near_miss


def _ask_reason_for_content(file_path: str, content: str) -> str | None:
    """Return an ask-checkpoint reason when an implementation proposal's
    Specification Links section fails the gate solely because its heading is a
    near-miss form SPEC_LINK_HEADING_RE does not match.

    A heading-format misdetection is a section-scanner boundary ambiguity, not
    a genuine missing-section failure -- the author wrote the section. It is
    surfaced as an ask checkpoint rather than a hard deny so the author can
    confirm or correct the heading instead of being blocked outright. A
    genuinely absent or placeholder-only section continues to deny via
    _deny_reason_for_content.
    """
    if not (_is_bridge_markdown_file(file_path) and content):
        return None
    first_line = _first_nonblank_line(content)
    if first_line == "ADVISORY" or first_line.startswith(("GO", "NO-GO", "VERIFIED")):
        return None
    if first_line in PENDING_PREFLIGHT_STATUSES:
        kb_mutation_reason = _kb_mutation_target_paths_ask_reason(content)
        if kb_mutation_reason:
            return kb_mutation_reason
    if _has_concrete_spec_links(content):
        return None
    if not _specification_links_heading_misdetected(content):
        return None
    return (
        "[Governance] The Specification Links heading was not recognized in "
        "its strict form (expected a heading line such as `## Specification "
        "Links`). Confirm or correct the heading format before filing. "
        "(Heading-format ambiguity surfaced as a checkpoint rather than a hard "
        "block per W4 enforcement calibration.)"
    )


def _target_paths_from_content(content: str) -> list[str]:
    """Parse a proposal's inline target_paths declaration."""
    paths: list[str] = []
    for match in TARGET_PATHS_LINE_RE.finditer(content):
        raw = match.group(1).strip()
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            for item in re.split(r"[,\s]+", raw):
                cleaned = item.strip().strip("\"'`")
                if cleaned:
                    paths.append(cleaned)
        else:
            if isinstance(parsed, list):
                paths.extend(str(item) for item in parsed)
            else:
                paths.append(str(parsed))
    return paths


def _declares_kb_mutation(content: str) -> bool:
    """Return True when proposal text declares its own KB/MemBase mutation."""
    if KB_MUTATION_NEGATION_RE.search(content):
        return False
    return bool(KB_MUTATION_DECLARATION_RE.search(content))


def _kb_mutation_target_paths_ask_reason(content: str) -> str | None:
    """Checkpoint proposals that declare KB mutation but omit groundtruth.db."""
    first_line = _first_nonblank_line(content)
    if first_line not in PENDING_PREFLIGHT_STATUSES:
        return None
    if _bridge_kind_is_metadata_exempt(content):
        return None
    if not _declares_kb_mutation(content):
        return None
    target_paths = {path.replace("\\", "/").lstrip("./") for path in _target_paths_from_content(content)}
    if "groundtruth.db" in target_paths:
        return None
    return (
        "[Governance] This bridge proposal appears to declare KB/MemBase mutation work, "
        "but target_paths does not include `groundtruth.db`. Add `groundtruth.db` to "
        "target_paths, or confirm the proposal performs no KB mutation. "
        "(Ask checkpoint per bridge target_paths KB-mutation completeness check.)"
    )


def _has_spec_derived_verification(content: str) -> bool:
    return bool(
        _has_concrete_spec_links(content)
        and SPEC_TEST_HEADING_RE.search(content)
        and COMMAND_EVIDENCE_RE.search(content)
    )


def _proposal_claims_owner_approval(content: str) -> bool:
    """Return True when proposal content signals dependence on owner approval.

    Self-citing (Owner Decisions / Input heading present) also counts as a
    claim because the author invoked the contract. The hook then verifies
    the section is substantive, not placeholder-only.
    """
    if OWNER_DECISIONS_HEADING_RE.search(content):
        return True
    return any(p.search(content) for p in OWNER_APPROVAL_MARKER_RES)


def _has_concrete_owner_decisions_section(content: str) -> bool:
    """Section heading present AND section text non-empty AND not placeholder-only."""
    lines = content.splitlines()
    start: int | None = None
    for i, line in enumerate(lines):
        if OWNER_DECISIONS_HEADING_RE.match(line.strip()):
            start = i + 1
            break
    if start is None:
        return False
    section = _collect_section_lines(lines, start)
    text = "\n".join(section).strip()
    if not text:
        return False
    nonblank_lines = [line for line in (ln.strip() for ln in section) if line]
    return any(not OWNER_DECISIONS_PLACEHOLDER_LINE_RE.match(line) for line in nonblank_lines)


def _owner_decisions_section_text(content: str) -> str:
    lines = content.splitlines()
    start: int | None = None
    for idx, line in enumerate(lines):
        if OWNER_DECISIONS_HEADING_RE.match(line.strip()):
            start = idx + 1
            break
    if start is None:
        return ""
    return "\n".join(_collect_section_lines(lines, start)).strip()


def _has_deferred_owner_evidence(content: str) -> bool:
    section_text = _owner_decisions_section_text(content)
    if not section_text:
        return False
    concrete_lines = [line.strip() for line in section_text.splitlines() if line.strip()]
    if not concrete_lines or not any(not OWNER_DECISIONS_PLACEHOLDER_LINE_RE.match(line) for line in concrete_lines):
        return False
    return bool(OWNER_EVIDENCE_RE.search(section_text))


def _bridge_kind_is_metadata_exempt(content: str) -> bool:
    """Return True when the proposal's bridge_kind header exempts it from the
    project-metadata gate (CLAUSE-NON-IMPLEMENTATION-EXEMPT).

    Non-implementation proposal classes (spec_intake, governance_review,
    loyal_opposition_advisory) self-declare via the bridge_kind header and are
    not subject to project-linkage metadata.
    """
    match = BRIDGE_KIND_LINE_RE.search(content)
    if not match:
        return False
    return match.group(1).strip().lower() in BRIDGE_KIND_METADATA_EXEMPT


def _project_metadata_gaps(content: str) -> list[str]:
    """Return the list of missing project-linkage metadata lines.

    Empty list means all three lines are present
    (CLAUSE-PROJECT-METADATA-PRESENT satisfied).
    """
    gaps: list[str] = []
    if not PROJECT_AUTHORIZATION_LINE_RE.search(content):
        gaps.append("Project Authorization:")
    if not PROJECT_LINE_RE.search(content):
        gaps.append("Project:")
    if not WORK_ITEM_LINE_RE.search(content):
        gaps.append("Work Item:")
    return gaps


def _extract_project_metadata(content: str) -> tuple[str | None, str | None, str | None]:
    """Return (authorization_id, project_id, work_item_id) captured from the
    three project-linkage metadata lines, or None per field when absent."""
    auth = PROJECT_AUTHORIZATION_VALUE_RE.search(content)
    proj = PROJECT_VALUE_RE.search(content)
    wi = WORK_ITEM_VALUE_RE.search(content)
    return (
        auth.group(1) if auth else None,
        proj.group(1) if proj else None,
        wi.group(1) if wi else None,
    )


def _parse_json_id_list(raw: object) -> list[str]:
    """Parse a JSON-encoded list-of-strings column; tolerate None/empty/garbage."""
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return []
    if isinstance(parsed, list):
        return [str(x) for x in parsed]
    return []


def _wi_project_membership_gap(content: str, cwd_path: Path) -> str | None:
    """Return a specific failed-condition token when the cited Work Item /
    Project / Project Authorization fails the live MemBase membership +
    authorization check, or None when all conditions pass.

    Fails open: missing DB or any sqlite/OS error returns None (with a stderr
    warning) so the gate never blocks on infrastructure failure. The check only
    runs when all three metadata lines are present (the metadata-presence gate
    handles absence). Condition tokens, in evaluation order:
    wi-not-found-in-project, wi-membership-inactive, authorization-not-found,
    authorization-inactive, authorization-expired, wi-excluded-from-authorization,
    wi-not-included-by-authorization.
    """
    authorization_id, project_id, work_item_id = _extract_project_metadata(content)
    if not (authorization_id and project_id and work_item_id):
        return None
    db_path = _canonical_project_root(cwd_path) / "groundtruth.db"
    if not db_path.is_file():
        return None
    conn: sqlite3.Connection | None = None
    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True, timeout=5)
        conn.row_factory = sqlite3.Row
        membership = conn.execute(
            "SELECT status FROM current_project_work_item_memberships WHERE work_item_id = ? AND project_id = ?",
            (work_item_id, project_id),
        ).fetchone()
        if membership is None:
            return "wi-not-found-in-project"
        if membership["status"] != "active":
            return "wi-membership-inactive"
        auth = conn.execute(
            "SELECT project_id, status, "
            "(expires_at IS NOT NULL AND expires_at <= datetime('now')) AS is_expired, "
            "included_work_item_ids, excluded_work_item_ids "
            "FROM current_project_authorizations WHERE id = ?",
            (authorization_id,),
        ).fetchone()
        if auth is None or auth["project_id"] != project_id:
            return "authorization-not-found"
        if auth["status"] != "active":
            return "authorization-inactive"
        if auth["is_expired"]:
            return "authorization-expired"
        if work_item_id in _parse_json_id_list(auth["excluded_work_item_ids"]):
            return "wi-excluded-from-authorization"
        included = _parse_json_id_list(auth["included_work_item_ids"])
        if included and work_item_id not in included:
            return "wi-not-included-by-authorization"
    except (sqlite3.Error, OSError) as exc:
        print(f"[Governance] WI-project membership check warning: {exc}", file=sys.stderr)
        return None
    finally:
        if conn is not None:
            conn.close()
    return None


def _advisory_report_template_gaps(content: str) -> list[str]:
    gaps: list[str] = []
    first_line = _first_nonblank_line(content)
    if first_line != "ADVISORY":
        gaps.append("first line ADVISORY")
    for field in ADVISORY_REPORT_HEADER_FIELDS:
        if not re.search(rf"^{re.escape(field)}\s*:", content, re.IGNORECASE | re.MULTILINE):
            gaps.append(f"header field {field}")
    for section in ADVISORY_REPORT_SECTIONS:
        if not re.search(rf"^#{{1,6}}\s*{re.escape(section)}\s*$", content, re.IGNORECASE | re.MULTILINE):
            gaps.append(f"section ## {section}")
    return gaps


def _is_template_shaped_advisory_report(content: str) -> bool:
    return not _advisory_report_template_gaps(content)


def _has_clean_applicability_preflight(content: str) -> bool:
    lines = content.splitlines()
    start: int | None = None
    for idx, line in enumerate(lines):
        if APPLICABILITY_PREFLIGHT_HEADING_RE.match(line.strip()):
            start = idx + 1
            break
    if start is None:
        return False

    section = _collect_section_lines(lines, start)
    section_text = "\n".join(section)
    return bool(PREFLIGHT_PACKET_HASH_RE.search(section_text) and PREFLIGHT_MISSING_REQUIRED_RE.search(section_text))


def _root_contained_scratch_path(cwd: Path, bridge_id: str) -> Path:
    root = cwd.resolve()
    scratch_dir = root / ".tmp" / "bridge-preflight-hook"
    scratch_dir.mkdir(parents=True, exist_ok=True)
    scratch = scratch_dir / f"{bridge_id}-{uuid4().hex}.md"
    scratch.resolve().relative_to(root)
    return scratch


def _run_pending_applicability_preflight(
    *,
    cwd: Path,
    file_path: str,
    bridge_id: str,
    content: str,
) -> tuple[bool, str]:
    scratch_path: Path | None = None
    try:
        scratch_path = _root_contained_scratch_path(cwd, bridge_id)
        scratch_path.write_text(content, encoding="utf-8")
        result = subprocess.run(
            [
                sys.executable,
                "scripts/bridge_applicability_preflight.py",
                "--bridge-id",
                bridge_id,
                "--content-file",
                str(scratch_path),
                "--json",
            ],
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        print(f"[Governance] Bridge applicability preflight warning for {file_path}: {exc}", file=sys.stderr)
        return True, ""
    finally:
        if scratch_path is not None:
            try:
                scratch_path.unlink(missing_ok=True)
            except OSError as exc:
                print(f"[Governance] Could not remove bridge preflight scratch file: {exc}", file=sys.stderr)

    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part).strip()
    if result.returncode not in (0, 5):
        print(
            f"[Governance] Bridge applicability preflight warning for {file_path}: {combined_output}",
            file=sys.stderr,
        )
        return True, ""
    try:
        packet = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(
            f"[Governance] Bridge applicability preflight warning for {file_path}: invalid JSON output",
            file=sys.stderr,
        )
        return True, ""
    missing_required = packet.get("missing_required_specs") or []
    if missing_required:
        return False, json.dumps(missing_required)
    return True, ""


def _read_proposal_target_paths(index_path: Path, doc_name: str) -> list[str]:
    """Read target_paths from the latest proposal file's frontmatter."""
    # Find the latest proposal file path from the index
    try:
        lines = index_path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []

    in_doc = False
    latest_file: str | None = None
    for line in lines:
        line = line.strip()
        if line.startswith("Document:") and line.removeprefix("Document:").strip() == doc_name:
            in_doc = True
            continue
        if in_doc and line.startswith("Document:"):
            break
        if in_doc and latest_file is None:
            for status in ("VERIFIED", "GO", "NO-GO", "ADVISORY", "DEFERRED", "REVISED", "NEW"):
                if line.startswith(status + ":"):
                    latest_file = line.split(":", 1)[1].strip()
                    break

    if not latest_file:
        return []

    proposal_path = index_path.parent.parent / latest_file
    try:
        content = proposal_path.read_text(encoding="utf-8")
    except OSError:
        return []

    # Look for target_paths in frontmatter or proposal body
    # Simple heuristic: look for target_paths: [...] or target_paths lines
    paths: list[str] = []
    for fline in content.splitlines():
        m = re.match(r"^\s*target_paths?\s*[:=]\s*(.+)", fline, re.IGNORECASE)
        if m:
            raw = m.group(1).strip()
            # Support JSON array or comma-separated
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    paths.extend(str(p) for p in parsed)
                else:
                    paths.append(str(parsed))
            except json.JSONDecodeError:
                for p in re.split(r"[,\s]+", raw):
                    p = p.strip("\"' ")
                    if p:
                        paths.append(p)
    return paths


def _is_bridge_index_file(file_path: str) -> bool:
    """True when file_path points at the canonical bridge index.

    Edits to bridge/INDEX.md are intrinsic bridge protocol (every proposal
    filing, verdict, and status transition edits it) and are never the gated
    "implementation" of a pending proposal - even when a proposal legitimately
    lists bridge/INDEX.md in its target_paths.
    """
    normalized = file_path.replace("\\", "/")
    return f"/{normalized}".endswith("/bridge/INDEX.md")


def _pending_proposal_ask_reason(index_path: Path, file_path: str) -> str | None:
    """Return an ask-checkpoint reason when file_path matches a pending
    proposal's target_paths, or None. bridge/INDEX.md is always exempt."""
    if _is_bridge_index_file(file_path):
        return None
    doc_statuses = _parse_bridge_index(index_path)
    file_path_normalized = file_path.replace("\\", "/")
    for doc_name, status in doc_statuses.items():
        if status not in ("NEW", "REVISED", "NO-GO"):
            continue
        for tp in _read_proposal_target_paths(index_path, doc_name):
            tp_norm = tp.replace("\\", "/")
            if file_path_normalized.endswith(tp_norm) or tp_norm == file_path_normalized:
                if status == "NO-GO":
                    return (
                        "[Governance] Bridge proposal for this module has NO-GO status. "
                        f"Review Codex findings at bridge/{doc_name} before implementing."
                    )
                return (
                    f"[Governance] Bridge proposal for {doc_name} is pending Codex review ({status}). "
                    "Wait for GO verdict before implementing."
                )
    return None


def _bridge_kind_validation_error(content: str) -> str | None:
    match = BRIDGE_KIND_LINE_RE.search(content)
    if not match:
        return None
    val = match.group(1).strip().lower()
    try:
        from groundtruth_kb.bridge.taxonomy import BridgeKind

        allowed = {k.value for k in BridgeKind}
    except ImportError:
        allowed = {
            "prime_proposal",
            "lo_verdict",
            "implementation_report",
            "governance_advisory",
            "index_reconciliation",
            "operational_state_change",
        }
    if val not in allowed:
        return (
            f"[Governance] Invalid bridge_kind: {val!r}. "
            f"Must be one of {sorted(allowed)} per DCL-BRIDGE-KIND-TAXONOMY-ENUM-001."
        )
    return None


def _deny_reason_for_content(
    *,
    cwd_path: Path,
    file_path: str,
    content: str,
    run_pending_preflight: bool = True,
) -> str | None:
    if _is_bridge_markdown_file(file_path) and content:
        if _body_status_token_violation(file_path, content):
            return (
                "[Governance] Versioned bridge files (bridge/<slug>-NNN.md) must begin with a "
                "canonical status token on the first non-blank line: one of NEW, REVISED, GO, "
                "NO-GO, VERIFIED, ADVISORY, DEFERRED, WITHDRAWN. The first non-blank line was "
                f"{_first_nonblank_line(content)!r}. Put the status token on line 1 (headings "
                "and prose follow it). Existing files with a non-canonical first line are "
                "grandfathered. (Hard-block per GTKB-GOV-PROPOSAL-STANDARDS Slice 1 "
                "body-status-token rule; see .claude/rules/file-bridge-protocol.md "
                "section 'Body Status-Token Rule'.)"
            )
        kind_err = _bridge_kind_validation_error(content)
        if kind_err:
            return kind_err
        first_line = _first_nonblank_line(content)
        if first_line == "ADVISORY" and not _is_template_shaped_advisory_report(content):
            return (
                "[Governance] ADVISORY bridge reports must match the verified ADVISORY report template: "
                "first line ADVISORY; header fields bridge_kind, Document, Version, Author, Date; "
                "sections ## Source, ## Claim, ## Owner Decision Needed, "
                "## Recommended Prime Action, and ## Classification Slot."
            )
        if first_line == "DEFERRED" and (
            not _has_deferred_owner_evidence(content)
            or not DEFERRED_REASON_RE.search(content)
            or not DEFERRED_CLEAR_CONDITION_RE.search(content)
        ):
            return (
                "[Governance] DEFERRED bridge files are owner-only parked status records. "
                "They must include concrete Owner Decisions / Input evidence plus a deferral "
                "reason and clear/resume condition."
            )
        if first_line in {"GO", "VERIFIED"} and not _has_clean_applicability_preflight(content):
            return (
                "[Governance] GO and VERIFIED bridge verdicts must include a clean "
                "Applicability Preflight section with packet_hash and "
                "missing_required_specs: []. Generate it with "
                "python scripts/bridge_applicability_preflight.py --bridge-id <document-name>. "
                "(Hard-block per mechanical cross-cutting specification applicability gate.)"
            )
        if first_line == "VERIFIED" and not _has_spec_derived_verification(content):
            return (
                "[Governance] VERIFIED bridge reports must carry Specification Links, "
                "a spec-to-test mapping, and executed test command evidence. "
                "(Hard-block per DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 + "
                "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001.)"
            )
        if (
            first_line not in {"ADVISORY", "DEFERRED"}
            and not first_line.startswith(("GO", "NO-GO", "VERIFIED"))
            and not _has_concrete_spec_links(content)
            and not _specification_links_heading_misdetected(content)
        ):
            return (
                "[Governance] Implementation proposals must include concrete Specification Links "
                "before bridge submission. "
                "(Hard-block per DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001.)"
            )
        if (
            first_line not in {"ADVISORY", "DEFERRED"}
            and not first_line.startswith(("GO", "NO-GO", "VERIFIED"))
            and _proposal_claims_owner_approval(content)
            and not _has_concrete_owner_decisions_section(content)
        ):
            return (
                "[Governance] Bridge proposals/reports that claim owner-approval scope must "
                "include a non-empty Owner Decisions / Input section enumerating the "
                "AskUserQuestion answers that authorize the work. "
                "(Hard-block per Sub-slice C of GTKB-GOV-AUQ-ENFORCEMENT-STACK; "
                "see bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-c-bridge-gate-003.md.)"
            )
        if first_line in PROJECT_METADATA_STATUSES and not _bridge_kind_is_metadata_exempt(content):
            metadata_gaps = _project_metadata_gaps(content)
            if metadata_gaps:
                return (
                    "[Governance] Implementation bridge proposals must include "
                    "project-linkage metadata lines: missing "
                    f"{', '.join(metadata_gaps)}. Add the absent line(s), or set "
                    "bridge_kind: spec_intake|governance_review|loyal_opposition_advisory "
                    "for a non-implementation proposal. "
                    "(Hard-block per DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001/"
                    "CLAUSE-PROJECT-METADATA-PRESENT.)"
                )
            membership_gap = _wi_project_membership_gap(content, cwd_path)
            if membership_gap:
                authorization_id, project_id, work_item_id = _extract_project_metadata(content)
                return (
                    "[Governance] Bridge proposal fails the live work-item/project "
                    f"membership check: {membership_gap}. Cited WI={work_item_id}, "
                    f"Project={project_id}, Project Authorization={authorization_id}. "
                    "The cited metadata must resolve to an active project membership and "
                    "an active, unexpired, including authorization in MemBase. "
                    "(Hard-block per DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001/"
                    "CLAUSE-BRIDGE-WI-PROJECT-MEMBERSHIP + "
                    "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001/"
                    "CLAUSE-PROJECT-AUTH-LIVE-CHECK.)"
                )
        if run_pending_preflight and first_line in PENDING_PREFLIGHT_STATUSES:
            bridge_id = _extract_bridge_id_from_path(file_path)
            if bridge_id:
                preflight_ok, error_msg = _run_pending_applicability_preflight(
                    cwd=cwd_path,
                    file_path=file_path,
                    bridge_id=bridge_id,
                    content=content,
                )
                if not preflight_ok:
                    return (
                        "[Governance] Pre-filing applicability preflight failed: "
                        f"file_path={file_path}; "
                        f"missing_required_specs={error_msg}. Run "
                        f"python scripts/bridge_applicability_preflight.py --bridge-id {bridge_id} "
                        "for full output. (Hard-block per "
                        "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 "
                        "mechanical enforcement.)"
                    )
        if first_line in BRIDGE_AUTHOR_METADATA_STATUSES:
            author_metadata_gaps = author_metadata_gaps_for_content(content)
            if author_metadata_gaps:
                return (
                    "[Governance] Bridge artifacts must include authoritative author/model audit "
                    "metadata lines: missing or invalid "
                    f"{', '.join(author_metadata_gaps)}. Required lines: "
                    f"{', '.join(REQUIRED_AUTHOR_METADATA_FIELDS)}. The authoring session must "
                    "supply accurate model, version, and configuration values; the dispatcher "
                    "must not guess. (Hard-block per owner emergency audit directive 2026-05-19.)"
                )
    return None


def _write_audit_result(
    *, cwd_path: Path, file_path: str, content: str, reason: str | None, audit_output: str = ""
) -> None:
    if audit_output:
        output_path = Path(audit_output)
        if not output_path.is_absolute():
            output_path = cwd_path / output_path
    else:
        output_path = _canonical_project_root(cwd_path) / AUDIT_OUTPUT_RELATIVE_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "audit_mode": True,
        "file_path": file_path,
        "preflight_passed": reason is None,
        "decision": "pass" if reason is None else "deny",
        "reason": reason,
    }
    output_path.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def preflight_advisory_for_write(
    cwd_path: Path,
    file_path: str,
    *,
    bridge_id: str | None = None,
) -> dict[str, object] | None:
    """Advisory-only target_paths preflight call path for Write/Edit operations (WI-3380).

    Per ``bridge/gtkb-impl-start-target-paths-preflight-005.md`` (GO), this is a
    non-blocking integration point: it runs the preflight in
    ``scripts/impl_start_target_paths_preflight.py`` for a single candidate file
    path and returns a structured advisory result (or ``None`` when the
    preflight is unavailable / no implementation-authorization packet is active).

    The function does NOT change ``permissionDecision`` semantics, does NOT emit
    output, and does NOT mutate state. Callers may incorporate the returned dict
    into ``additionalContext`` of an existing ``emit_ask``/``emit_deny`` payload
    to surface scope-drift signal without widening blocking behavior. This
    slice (per the proposal) defines the call path; downstream slices may wire
    it into ``main()``.

    Resolution:

    - When ``bridge_id`` is None, the active impl-auth packet's bridge id is
      used (``load_packet`` -> ``packet["bridge_id"]``). When no packet is
      active, the function returns ``None``.
    - The candidate set is the single ``file_path`` argument.

    Returns:
        None  - preflight could not run (no packet, missing module, error).
        dict  - the preflight result dict from
                ``impl_start_target_paths_preflight.run_preflight`` containing
                ``bridge_id``, ``verdict``, ``exit_code``, ``in_scope``,
                ``out_of_scope``, ``target_paths``, etc.
    """
    try:
        _scripts_dir = Path(__file__).resolve().parents[2] / "scripts"
        if str(_scripts_dir) not in sys.path:
            sys.path.insert(0, str(_scripts_dir))
        from impl_start_target_paths_preflight import run_preflight
        from implementation_authorization import load_packet
    except Exception:
        return None

    project_root = cwd_path
    resolved_bridge_id = bridge_id
    if resolved_bridge_id is None:
        try:
            packet = load_packet(project_root)
            resolved_bridge_id = packet.get("bridge_id")
        except Exception:
            return None
        if not resolved_bridge_id:
            return None

    try:
        result, _exit_code = run_preflight(
            project_root,
            resolved_bridge_id,
            explicit_candidates=[file_path],
            use_git_diff=False,
        )
    except Exception:
        return None
    return result


def _audit_only(argv: list[str]) -> int:
    cwd_path = Path.cwd().resolve()
    file_path = ""
    audit_output = ""
    if "--audit-output" in argv:
        idx = argv.index("--audit-output")
        if idx + 1 < len(argv):
            audit_output = argv[idx + 1]
    if "--file-path" in argv:
        idx = argv.index("--file-path")
        if idx + 1 < len(argv):
            file_path = argv[idx + 1]
    if not file_path:
        try:
            payload = json.loads(sys.stdin.read() or "{}")
        except json.JSONDecodeError:
            payload = {}
        cwd_path = Path(str(payload.get("cwd") or ".")).resolve()
        tool_input = payload.get("tool_input") or {}
        file_path = str(tool_input.get("file_path") or "")
        content = str(tool_input.get("content") or "")
    else:
        target = (cwd_path / file_path).resolve()
        try:
            content = target.read_text(encoding="utf-8")
        except OSError:
            content = ""
    reason = _deny_reason_for_content(
        cwd_path=cwd_path,
        file_path=file_path,
        content=content,
        run_pending_preflight=True,
    )
    _write_audit_result(
        cwd_path=cwd_path,
        file_path=file_path,
        content=content,
        reason=reason,
        audit_output=audit_output,
    )
    print("{}")
    return 0


def main() -> None:
    try:
        from groundtruth_kb.governance.output import emit_ask, emit_deny, emit_pass
    except ImportError:

        def emit_ask(event: str, reason: str) -> None:  # type: ignore[misc]
            out = {
                "hookSpecificOutput": {
                    "hookEventName": event,
                    "permissionDecision": "ask",
                    "permissionDecisionReason": reason,
                    "additionalContext": reason,
                }
            }
            print(json.dumps(out))

        def emit_deny(event: str, reason: str) -> None:  # type: ignore[misc]
            _record_gate_denial("bridge-compliance", file_path, reason, root=cwd_path)
            out = {
                "hookSpecificOutput": {
                    "hookEventName": event,
                    "permissionDecision": "deny",
                    "permissionDecisionReason": reason,
                    "additionalContext": reason,
                }
            }
            print(json.dumps(out))

        def emit_pass() -> None:  # type: ignore[misc]
            print("{}")

    if "--audit-only" in sys.argv:
        sys.exit(_audit_only(sys.argv[1:]))

    if "--self-test" in sys.argv:
        emit_ask(
            "PreToolUse",
            "[Governance] Bridge compliance gate active. Ensure bridge proposal has GO status before implementing.",
        )
        sys.exit(0)

    try:
        payload = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, OSError):
        emit_pass()
        sys.exit(0)

    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})
    cwd = payload.get("cwd", ".")
    cwd_path = Path(cwd).resolve()

    if tool_name not in WRITE_TOOLS:
        emit_pass()
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path:
        emit_pass()
        sys.exit(0)

    work_intent_reason = _bridge_work_intent_deny_reason(cwd_path=cwd_path, file_path=file_path, payload=payload)
    if work_intent_reason:
        _record_gate_denial("bridge-compliance", file_path, work_intent_reason, root=cwd_path)
        emit_deny("PreToolUse", work_intent_reason)
        sys.exit(0)

    content = str(tool_input.get("content", ""))
    reason = _deny_reason_for_content(
        cwd_path=cwd_path,
        file_path=file_path,
        content=content,
        run_pending_preflight=tool_name == "Write",
    )
    if reason:
        _record_gate_denial("bridge-compliance", file_path, reason, root=cwd_path)
        emit_deny("PreToolUse", reason)
        sys.exit(0)

    heading_ask_reason = _ask_reason_for_content(file_path, content)
    if heading_ask_reason:
        emit_ask("PreToolUse", heading_ask_reason)
        sys.exit(0)

    index_path = _canonical_project_root(cwd_path) / BRIDGE_INDEX_FILENAME
    if not index_path.exists():
        emit_pass()
        sys.exit(0)

    ask_reason = _pending_proposal_ask_reason(index_path, file_path)
    if ask_reason:
        emit_ask("PreToolUse", ask_reason)
        sys.exit(0)

    emit_pass()
    sys.exit(0)


if __name__ == "__main__":
    main()
