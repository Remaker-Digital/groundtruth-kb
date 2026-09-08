#!/usr/bin/env python3
# THIS FILE IS A PROJECTION, NOT CANONICAL.
# Projected from the neutral harness baseline by the GT-KB projection engine.
# Do not edit here: change the baseline (.harness-baseline-configuration) and re-project with
# `gt harness project antigravity`. If a needed change cannot be made through
# the baseline and re-projection, file a work item against the projector
# (GOV-HARNESS-NEUTRAL-BASELINE-001 obligation 6).
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
import fnmatch
import hashlib
import json
import os
import re
import sqlite3
import subprocess
import sys
import time
from pathlib import Path
from uuid import uuid4


def _no_window_subprocess_kwargs() -> dict[str, object]:
    kwargs: dict[str, object] = {}
    if os.name == "nt":
        kwargs["creationflags"] = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    return kwargs


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
        extract_author_metadata,
        is_synthetic_session_context_id,
    )
except Exception:  # pragma: no cover - hook fail-soft fallback for partial installs
    BRIDGE_AUTHOR_METADATA_STATUSES = frozenset(
        {
            "NEW",
            "REVISED",
            "GO",
            "NO-GO",
            "VERIFIED",
            "ADVISORY",
            "WITHDRAWN",
            "READY",
            "NOT-READY",
            "VERDICT-REJECTED",
            "SUPERSEDED",
            "BLOCKED",
        }
    )
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

    def extract_author_metadata(content: str) -> dict[str, str]:
        return {
            key.lower(): value.strip()
            for key, value in re.findall(r"^(author_[a-z0-9_]+):\s*(.*?)\s*$", content, re.IGNORECASE | re.MULTILINE)
        }

    def is_synthetic_session_context_id(value: object) -> bool:
        text = str(value or "").strip().strip("`")
        lowered = text.lower()
        leading_segment = lowered.split("-", 1)[0]
        return (
            lowered
            in {
                "",
                "-",
                "--",
                "<tbd>",
                "<unknown>",
                "[tbd]",
                "[unknown]",
                "n/a",
                "na",
                "none",
                "null",
                "tbd",
                "todo",
                "unknown",
                "unspecified",
            }
            or bool(re.fullmatch(r"(?:openrouter|ollama)-harness-[a-z]", text, re.IGNORECASE))
            or any(character.isspace() for character in text)
            or leading_segment
            in {
                "absent",
                "missing",
                "none",
                "nosession",
                "notset",
                "null",
                "unavailable",
                "unknown",
                "unset",
            }
        )


try:
    from scripts.gtkb_bridge_writer import BridgeEnvelopeError, validate_bridge_envelope_head
except Exception:  # pragma: no cover - hook fail-soft fallback for partial installs

    class BridgeEnvelopeError(RuntimeError):
        pass

    def validate_bridge_envelope_head(
        _content: str,
        *,
        require_dispatchable: bool = False,
        activity: str | None = None,
    ) -> None:
        return None


WRITE_TOOLS = {"Write", "Edit"}
PENDING_PREFLIGHT_STATUSES = {"NEW", "REVISED"}
try:
    from groundtruth_kb.bridge.vocabulary import CANONICAL_STATUSES as _CANONICAL_STATUSES
except Exception:  # pragma: no cover - hook fail-soft fallback for partial installs
    _CANONICAL_STATUSES = frozenset(BRIDGE_AUTHOR_METADATA_STATUSES)
try:
    from groundtruth_kb.bridge.vocabulary import (
        LOYAL_OPPOSITION_ACTIONABLE_STATUSES as _LO_ACTIONABLE_STATUSES,
    )
except Exception:  # pragma: no cover - hook fail-soft fallback for partial installs
    _LO_ACTIONABLE_STATUSES = frozenset({"NEW", "REVISED", "READY", "VERDICT-REJECTED"})
# Prime-authored files that request Loyal Opposition review; the Owner Decisions /
# Input section gate applies to these and to nothing else (verdicts, advisories,
# withdrawals and typed refusals are evidence narratives, not approval claims).
OWNER_DECISIONS_GATED_STATUSES = frozenset(_LO_ACTIONABLE_STATUSES)
# Canon section 6: the twelve canonical statuses come from the single code of
# record, groundtruth_kb.bridge.vocabulary; the gate does not restate them. The
# tuple is ordered longest-first so no token in the alternation below can be
# shadowed by a shorter token that it starts with.
BRIDGE_STATUS_TOKENS = tuple(sorted(_CANONICAL_STATUSES, key=lambda status: (-len(status), status)))
BRIDGE_VERSIONED_FILE_RE = re.compile(r"^(.+)-(\d{3,})\.md$")
LO_VERDICT_BRIDGE_FILE_RE = re.compile(r"^.+\.lo-verdict\.md$", re.IGNORECASE)
BRIDGE_FILE_STATUS_RE = re.compile(
    r"^[#>*\-\s`]*(?:" + "|".join(re.escape(status) for status in BRIDGE_STATUS_TOKENS) + r")\b",
    re.IGNORECASE,
)
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
    r"|(?:^|[`(\s])(?:.agent/rules|groundtruth-kb/docs|docs|bridge)/[^\s`)]+",
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
PRIOR_DELIBERATIONS_HEADING_RE = re.compile(
    r"^#{1,6}\s*prior\s+deliberations\s*$",
    re.IGNORECASE,
)
# WI-6741: mandatory Simplification Accounting section on implementation proposals.
# An explicit "nothing gets smaller" is a complete and valid answer; omission is not.
# Placeholder set is deliberately NARROWER than the owner-decisions one: "none" and
# "n/a" are excluded, because "none" is a substantive answer to "what gets smaller"
# where it is a non-answer to "which owner decisions authorize this".
SIMPLIFICATION_ACCOUNTING_HEADING_RE = re.compile(
    r"^#{1,6}\s*Simplification Accounting\s*$",
    re.IGNORECASE | re.MULTILINE,
)
SIMPLIFICATION_ACCOUNTING_PLACEHOLDER_LINE_RE = re.compile(
    r"^[\s>*`_\-:]*(?:tbd|todo|fill in|fill this in|\?+)[\s.`_\-:]*$",
    re.IGNORECASE,
)
NO_PRIOR_DELIBS_PLACEHOLDER = "_No prior deliberations: <fill in reason before filing>._"
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
COMMIT_FINALIZATION_HEADING_RE = re.compile(
    r"^#{1,6}\s*commit\s+finalization\s+evidence\s*$",
    re.IGNORECASE,
)
SAME_TRANSACTION_PATH_SET_RE = re.compile(r"\bsame-transaction\s+path\s+set\b", re.IGNORECASE)
# WI-6365: post-commit finalization evidence. Under owner canon the commit of the
# work product IS the terminal state and PRECEDES the VERIFIED verdict, so a
# canonical verdict can never carry same-transaction evidence -- the commit it
# attests already happened. It cites that commit instead.
WORK_PRODUCT_COMMIT_RE = re.compile(
    r"\bwork-product\s+commit\s*:\s*`?[0-9a-f]{7,40}`?",
    re.IGNORECASE,
)
FINALIZATION_PATH_BULLET_RE = re.compile(r"(?m)^\s*[-*]\s+`[^`]+`\s*$")
PREFLIGHT_PACKET_HASH_RE = re.compile(
    r"\bpacket_hash\s*:\s*`?sha256:[0-9a-f]{64}`?",
    re.IGNORECASE,
)
PREFLIGHT_MISSING_REQUIRED_RE = re.compile(
    r"\bmissing_required_specs\s*:\s*(?:\[\s*\]|`?\[\s*\]`?|none|None|NONE)",
    re.IGNORECASE,
)
VERDICT_PREFLIGHT_FRESHNESS_STATUSES = frozenset({"GO", "NO-GO", "VERIFIED"})
RESPONDS_TO_BRIDGE_PATH_RE = re.compile(r"(?im)^\s*Responds\s+to\s*:\s*`?(?P<path>[^`\r\n]+?\.md)`?\s*$")
PREFLIGHT_FIELD_LINE_RE = re.compile(r"(?im)^\s*[-*]?\s*(?P<name>[a-z_]+)\s*:\s*`?(?P<value>[^`\r\n]+?)`?\s*$")
CANDIDATE_EVIDENCE_HASH_SENTINEL = "<CANDIDATE_EVIDENCE_HASH>"
CANDIDATE_EVIDENCE_HASH_LINE_RE = re.compile(
    r"(?im)^(?P<prefix>\s*[-*]?\s*candidate_evidence_hash\s*:\s*`?)"
    r"(?P<value>sha256:[0-9a-f]{64}|<CANDIDATE_EVIDENCE_HASH>)"
    r"(?P<suffix>`?\s*)$"
)

# Owner Decisions / Input section gate (Sub-slice C of GTKB-GOV-AUQ-ENFORCEMENT-STACK).
# Per bridge/gtkb-gov-askuserquestion-enforcement-stack-slice-c-bridge-gate-003.md
# (Loyal Opposition GO at -004): conditional check that fires only when proposal/report content
# indicates owner-approval scope. Verdict files (GO/NO-GO/VERIFIED first line) are
# excluded — they are evidence narratives, not approval claims.
OWNER_DECISIONS_HEADING_RE = re.compile(
    r"^#{1,6}\s*Owner Decisions(?:\s*/\s*Input)?\s*$",
    re.IGNORECASE | re.MULTILINE,
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

# Cross-Harness Disposition gate (Slice 4 of PROJECT-GTKB-CROSS-HARNESS-PARITY;
# DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001 assertion PARITY-DISPOSITION-GATE;
# ADR-CROSS-HARNESS-PARITY-001 Q8). An implementation proposal whose target_paths
# touch a harness-surface file must declare, per applicable harness, behavioral
# parity or an owner-approved typed waiver in a ## Cross-Harness Disposition
# section. The harness-surface marker set is scoped to the demonstrated
# behavioral-surface set; .cursor/ surfaces and registry-driven expansion are a
# Slice-6 follow-on.
CROSS_HARNESS_DISPOSITION_HEADING_RE = re.compile(
    r"^#{1,6}\s*cross[-\s]?harness\s+disposition\s*$",
    re.IGNORECASE | re.MULTILINE,
)
HARNESS_SURFACE_PATH_MARKERS = (
    ".claude/settings.json",
    ".codex/hooks.json",
    ".claude/hooks/",
    ".codex/gtkb-hooks/",
    ".claude/skills/",
    ".codex/skills/",
)
# Leading bullet / punctuation markers stripped before testing a disposition
# line for real (alphanumeric) content, so a bare "-", blank bullet, or
# placeholder line is not mistaken for substantive content.
DISPOSITION_NONCONTENT_PREFIX_RE = re.compile(r"^[\s>*`_:\-]+")

# Modernization intuitiveness/non-impairment proposal gate. The exact heading
# is part of GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001's executable contract.
NONIMPAIRMENT_DISPOSITION_HEADING_RE = re.compile(
    r"^#{1,6}\s*intuitiveness\s*/\s*non[-\s]?impairment\s+disposition\s*$",
    re.IGNORECASE | re.MULTILINE,
)
NONIMPAIRMENT_REQUIRED_FIELDS = frozenset(
    {
        "applicability",
        "provenance",
        "canonical_authority",
        "primary_route",
        "before_behavior",
        "after_behavior",
        "self_descriptive_naming",
        "obsolete_guidance_disposition",
        "history_preservation",
        "baseline",
        "expected_result",
        "rollback",
        "hard_invariants",
        "fail_closed_conditions",
        "essential_context_preservation",
    }
)
NONIMPAIRMENT_PLACEHOLDERS = frozenset({"", "n/a", "none", "tbd", "todo", "unknown"})
NONIMPAIRMENT_GOV_ID = "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001"

# Project-linkage metadata gate (DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001).
# WI-3314: metadata-presence enabling slice. Implementation bridge proposals
# (NEW/REVISED status, not bridge_kind-exempt) must carry two machine-readable
# metadata lines, Project and Work Item, so a proposal self-documents its
# project provenance. CLAUSE-PROJECT-METADATA-PRESENT is enforced here;
# CLAUSE-VERDICT-FILES-EXCLUDED is satisfied by the NEW/REVISED-only status
# gate; CLAUSE-NON-IMPLEMENTATION-EXEMPT is satisfied by the bridge_kind exempt
# set. Canon section 3: authorization is a field on the project row and gates
# dispatch, not filing, so no authorization record is named or looked up here.
PROJECT_LINE_RE = re.compile(r"^Project:\s*[A-Z0-9-]+\s*$", re.MULTILINE)
WORK_ITEM_LINE_RE = re.compile(
    r"^Work Item:\s*(?:WI-\d+|WI-AUTO-[A-Z0-9-]+|GTKB-[A-Z0-9-]+|WORKLIST-[A-Z0-9-]+)\s*$", re.MULTILINE
)
PROJECT_METADATA_FORMAT_HINT = (
    "Expected plain metadata lines such as "
    "`Project: PROJECT-GTKB-RELIABILITY-FIXES` and `Work Item: WI-3496`. "
    "Markdown-bold forms such as `**Project:** ...` and `**Work Item:** ...` "
    "are not recognized as project-linkage metadata lines by this gate. "
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

# Requirement Sufficiency presence gate (WI-3439).
# .agent/rules/file-bridge-protocol.md section "Mandatory Implementation-Start
# Authorization Metadata" requires every implementation proposal that requests
# source/test/script/hook/config/deploy/repo-state/KB-mutation work to carry a
# "## Requirement Sufficiency" subsection with exactly one operative state. This
# Write-time gate enforces presence + a bounded operative state BEFORE GO, so the
# omission is caught here rather than post-GO at implementation-start. Scoped to
# implementation-proposal bridge_kind tokens (canonical prime_proposal plus the
# colloquial implementation_proposal used via the helper path), NOT
# implementation_report (post-implementation reports correctly lack the
# subsection). See the GO at
# bridge/gtkb-wi3439-requirement-sufficiency-presence-check-002.md constraint 1.
REQUIREMENT_SUFFICIENCY_HEADING_RE = re.compile(
    r"^#{1,6}\s*requirement\s+sufficiency\s*$",
    re.IGNORECASE,
)
# The implementation-start authorization parser owns the bounded Requirement
# Sufficiency vocabulary. The Write-time hook imports that classifier when the
# full project checkout is available, and falls back to the same bounded regexes
# when installed in a partial hook/template context.
try:
    from scripts.implementation_authorization import (
        REQUIREMENT_GAP_RE as REQUIREMENT_SUFFICIENCY_STATE_NEW_REQUIRED_RE,
    )
    from scripts.implementation_authorization import (
        REQUIREMENT_SUFFICIENCY_RE as REQUIREMENT_SUFFICIENCY_STATE_SUFFICIENT_RE,
    )
    from scripts.implementation_authorization import (
        requirement_sufficiency_state as _implementation_requirement_sufficiency_state,
    )
except Exception:  # pragma: no cover - hook fail-soft fallback for partial installs
    REQUIREMENT_SUFFICIENCY_STATE_NEW_REQUIRED_RE = re.compile(
        r"(?i)(?<!\bno\s)\bnew\s+or\s+revised\s+requirements?\b[^.]{0,60}?\b(?:required|needed)\b"
    )
    REQUIREMENT_SUFFICIENCY_STATE_SUFFICIENT_RE = re.compile(
        r"(?i)\b(?:existing\s+)?(?:requirements?|owner\s+direction)\b(?:(?!\bnot\b)[^.]){0,80}?\bsufficient\b"
    )
    _FALLBACK_FUTURE_SCOPED_GAP_CONTEXT_RE = re.compile(
        r"(?i)\b(?:would|could|might|may)\b[^.]{0,80}?\b(?:only|later|future|follow-?on|separate|child)\b"
    )

    def _implementation_requirement_sufficiency_state(markdown: str) -> str:
        lines = markdown.splitlines()
        start: int | None = None
        for idx, line in enumerate(lines):
            if REQUIREMENT_SUFFICIENCY_HEADING_RE.match(line.strip()):
                start = idx + 1
                break
        if start is None:
            return "missing"
        body_lines = _collect_section_lines(lines, start)
        body = "\n".join(body_lines).strip()
        if not body:
            return "missing"
        gap_match = REQUIREMENT_SUFFICIENCY_STATE_NEW_REQUIRED_RE.search(body)
        sufficiency_match = REQUIREMENT_SUFFICIENCY_STATE_SUFFICIENT_RE.search(body)
        if gap_match and sufficiency_match:
            if gap_match.start() < sufficiency_match.start():
                return "gap"
            gap_sentence_end = body.find(".", gap_match.start())
            if gap_sentence_end == -1:
                gap_sentence_end = len(body)
            gap_sentence = body[gap_match.start() : gap_sentence_end + 1]
            if _FALLBACK_FUTURE_SCOPED_GAP_CONTEXT_RE.search(gap_sentence):
                return "sufficient"
            return "gap"
        if gap_match:
            return "gap"
        if sufficiency_match:
            return "sufficient"
        return "unrecognized"


# The two mutually exclusive operative states. The file-bridge-protocol requires
# EXACTLY ONE; the gap helper counts distinct canonical states present and
# rejects zero or more than one (per WI-3439 verification NO-GO -008).
REQUIREMENT_SUFFICIENCY_OPERATIVE_STATES = (
    REQUIREMENT_SUFFICIENCY_STATE_SUFFICIENT_RE,
    REQUIREMENT_SUFFICIENCY_STATE_NEW_REQUIRED_RE,
)
BRIDGE_KIND_IMPLEMENTATION_PROPOSAL = frozenset(
    {"prime_proposal", "implementation_proposal", "prime_implementation_proposal"}
)

# WI-project membership gate (DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001/
# CLAUSE-BRIDGE-WI-PROJECT-MEMBERSHIP).
# When a NEW/REVISED implementation proposal carries both project-linkage
# metadata lines, the cited Work Item must have an active membership in the
# cited Project. The check fails open on any DB-access error so the gate never
# blocks on infrastructure failure. Verdict files (GO/NO-GO/VERIFIED) never
# reach this check because it lives inside the NEW/REVISED metadata branch.
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
APPROVAL_EVIDENCE_DECLARATION_RE = re.compile(
    r"\b(?:"
    r"formal[-\s]+artifact[-\s]+approval(?:[-\s]+evidence|[-\s]+packet)?|"
    r"formal[-\s]+approval[-\s]+packet|"
    r"narrative[-\s]+artifact[-\s]+approval(?:[-\s]+evidence|[-\s]+packet)?|"
    r"narrative[-\s]+approval[-\s]+packet|"
    r"artifact[-\s]+approval[-\s]+packet|"
    r"approval[-\s]+packet"
    r")\b"
    r"|\.groundtruth[\\/]+formal-artifact-approvals(?:[\\/][^\s`),]+)?",
    re.IGNORECASE,
)
APPROVAL_EVIDENCE_NEGATION_RE = re.compile(
    r"\b(?:"
    r"no|not|without|does\s+not|do\s+not|performs?\s+no|creates?\s+no|writes?\s+no|updates?\s+no|"
    r"requires?\s+no|omits?|excludes?"
    r")\b",
    re.IGNORECASE,
)
APPROVAL_EVIDENCE_TARGET_DIR = ".groundtruth/formal-artifact-approvals"

ADVISORY_REPORT_HEADER_FIELDS = ("bridge_kind", "Document", "Version", "Author", "Date")
ADVISORY_REPORT_SECTIONS = (
    "Source",
    "Claim",
    "Owner Decision Needed",
    "Recommended Prime Action",
    "Classification Slot",
)
AUDIT_OUTPUT_RELATIVE_PATH = Path(".agent/hooks") / "last-bridge-audit.json"
PENDING_TARGET_CACHE_RELATIVE_PATH = Path(".gtkb-state") / "bridge-compliance" / "pending-proposal-targets.json"
PENDING_TARGET_CACHE_SCHEMA_VERSION = 1


def _record_gate_denial(pattern_id: str, subject: str, reason: str, *, root: Path | None = None) -> None:
    path = Path(os.environ.get("GTKB_GATE_DENIALS_PATH", ".gtkb-state/gate-denials.jsonl"))
    base = root or Path(os.environ.get("ANTIGRAVITY_PROJECT_DIR") or os.getcwd()).resolve()
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
    under ``<canonical>/.agent/worktrees/``. A resolver result that is neither
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


def _is_under_harness_worktrees(path: Path) -> bool:
    parts = path.resolve().parts
    return any(left == ".agent" and right == "worktrees" for left, right in zip(parts, parts[1:], strict=False))


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
            out = subprocess.check_output(
                args,
                cwd=str(cwd_path),
                text=True,
                stderr=subprocess.DEVNULL,
                **_no_window_subprocess_kwargs(),
            ).strip()
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

    Bridge governance state -- ``groundtruth.db``, versioned bridge files, and
    the audit-output tree -- exists only at the canonical main-worktree
    root. A session running inside a ``.agent/worktrees/*`` linked worktree has
    a cwd that is NOT that root; trusting it makes the gate read an empty
    scaffold database and falsely block a valid proposal.

    Resolution is fail-soft and uses ``cwd_path`` directly; package-level root
    helpers rely on process cwd and are therefore unsafe for hook unit tests that
    pass a synthetic cwd. Linked worktrees resolve through ``git-common-dir``;
    normal subdirectories use the nearest ``groundtruth.toml`` marker; scratch
    directories under ``.tmp`` or ``.gtkb-state`` stay hermetic and fall back
    to ``cwd_path``.
    """
    if _is_under_harness_worktrees(cwd_path):
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


def _status_from_versioned_bridge_file(path: Path) -> str | None:
    try:
        handle = path.open("r", encoding="utf-8-sig", errors="replace")
    except OSError:
        return None
    with handle:
        for line in handle:
            stripped = line.strip()
            if not stripped:
                continue
            match = BRIDGE_FILE_STATUS_RE.match(stripped)
            return match.group(0).strip().split()[0].upper() if match else None
    return None


def _project_relative_path(path: Path, project_root: Path) -> str:
    try:
        return path.resolve().relative_to(project_root.resolve()).as_posix()
    except (OSError, ValueError):
        return path.as_posix()


def _versioned_bridge_file_groups(project_root: Path) -> dict[str, list[tuple[int, Path]]]:
    bridge_dir = project_root / "bridge"
    groups: dict[str, list[tuple[int, Path]]] = {}
    try:
        candidates = list(bridge_dir.iterdir())
    except OSError:
        return groups
    for path in candidates:
        if not path.is_file():
            continue
        match = BRIDGE_VERSIONED_FILE_RE.match(path.name)
        if not match:
            continue
        groups.setdefault(match.group(1), []).append((int(match.group(2)), path))
    for values in groups.values():
        values.sort(key=lambda row: row[0], reverse=True)
    return groups


def _versioned_bridge_entries(project_root: Path) -> dict[str, list[tuple[int, str, str, Path]]]:
    entries: dict[str, list[tuple[int, str, str, Path]]] = {}
    for slug, values in _versioned_bridge_file_groups(project_root).items():
        if not values:
            continue
        version, path = values[0]
        status = _status_from_versioned_bridge_file(path)
        if status is None:
            continue
        entries[slug] = [(version, status, _project_relative_path(path, project_root), path)]
    return entries


def _latest_bridge_statuses(project_root: Path) -> dict[str, str]:
    return {slug: values[0][1] for slug, values in _versioned_bridge_entries(project_root).items() if values}


_ENVELOPE_HEAD_PREFIXES = ("::init", "::open")


def _first_nonblank_line(content: str) -> str:
    """Return the first non-blank line that is not an artifact-head envelope marker.

    The canonical bridge header is::

        ::init gtkb <pb|lo>
        ::open <activity>
        <status token>

    (owner directive 2026-08-16; the ``::init`` / ``::open`` lines may be null
    only when the status is ``ADVISORY``). The status token is therefore not
    necessarily the first non-blank line of the file. Leading envelope markers
    are skipped here so that every status-dependent check in this module reads
    the true status token through this single accessor rather than each
    re-deriving it. Markers that appear after the status token are the envelope
    validator's concern, not this function's: iteration stops at the first
    non-marker line.
    """
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith(_ENVELOPE_HEAD_PREFIXES):
            continue
        return stripped
    return ""


_RETIRED_BRIDGE_AGGREGATE_NAME = "INDEX.md"


def _is_retired_bridge_aggregate_file(file_path: str) -> bool:
    path = Path(file_path.replace("\\", "/"))
    parts = tuple(path.parts)
    return len(parts) >= 2 and parts[-2].lower() == "bridge" and parts[-1] == _RETIRED_BRIDGE_AGGREGATE_NAME


def _is_bridge_markdown_file(file_path: str) -> bool:
    normalized = file_path.replace("\\", "/")
    if not normalized.endswith(".md"):
        return False
    return "/bridge/" in f"/{normalized}" and bool(BRIDGE_VERSIONED_FILE_RE.match(Path(normalized).name))


def _is_lo_verdict_bridge_file(file_path: str) -> bool:
    normalized = file_path.replace("\\", "/")
    if not normalized.endswith(".md"):
        return False
    return "/bridge/" in f"/{normalized}" and bool(LO_VERDICT_BRIDGE_FILE_RE.match(Path(normalized).name))


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
            "Per .agent/rules/file-bridge-protocol.md 'Mandatory Pre-Drafting Claim Step', run: "
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
# reliable routing signal. See .agent/rules/file-bridge-protocol.md
# "Body Status-Token Rule".
def _first_line_is_recognized_status(first_line: str) -> bool:
    """True when ``first_line`` is a canonical bridge status token.

    Mirrors the gate's existing first-line recognition union (the ADVISORY,
    GO/NO-GO/VERIFIED, and PENDING_PREFLIGHT_STATUSES {NEW, REVISED} checks in
    ``_deny_reason_for_content``) plus the non-actionable ``BLOCKED``, ``SUPERSEDED`` and
    terminal ``WITHDRAWN`` statuses used throughout bridge state. Errs toward acceptance (``.startswith`` for
    verdicts) so the body-status-token rule never false-blocks a line the rest
    of the gate would recognize.
    """
    return first_line in BRIDGE_STATUS_TOKENS or first_line.startswith(("GO", "NO-GO", "VERIFIED"))


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
                if not stripped:
                    continue
                if stripped.startswith(_ENVELOPE_HEAD_PREFIXES):
                    continue
                return stripped
        return ""
    except OSError:
        return None


def _versioned_bridge_file_exists_on_disk(file_path: str) -> bool:
    """Return True when a versioned bridge file already exists on disk.

    Fail-open: returns False on any OS error so a filesystem issue cannot
    create a spurious hard-block.
    """
    if _extract_bridge_id_from_path(file_path) is None:
        return False
    try:
        return Path(file_path).is_file()
    except OSError:
        return False


def _body_status_token_violation(file_path: str, content: str) -> bool:
    """True when a versioned bridge file's first non-blank line is not a
    recognized status token AND the file is not grandfathered.

    New files (and overwrites of files that currently have a canonical first
    line) must keep a canonical first line. Files that already exist on disk
    with a non-canonical first line are grandfathered. Non-versioned bridge
    markdown (no ``-NNN`` suffix) is not subject to the rule.
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
        approval_evidence_reason = _approval_evidence_target_paths_ask_reason(content)
        if approval_evidence_reason:
            return approval_evidence_reason
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


def _normalise_target_path(path: str) -> str:
    norm = path.replace("\\", "/").strip().strip("\"'`")
    while norm.startswith("./"):
        norm = norm[2:]
    return norm.rstrip("/")


def _target_path_set_from_content(content: str) -> set[str]:
    return {_normalise_target_path(path) for path in _target_paths_from_content(content)}


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
    target_paths = _target_path_set_from_content(content)
    if "groundtruth.db" in target_paths:
        return None
    return (
        "[Governance] This bridge proposal appears to declare KB/MemBase mutation work, "
        "but target_paths does not include `groundtruth.db`. Add `groundtruth.db` to "
        "target_paths, or confirm the proposal performs no KB mutation. "
        "(Ask checkpoint per bridge target_paths KB-mutation completeness check.)"
    )


def _declares_approval_evidence_scope(content: str) -> bool:
    """Return True when proposal text declares approval-packet evidence work."""
    for segment in re.split(r"(?<=[.!?])\s+|\n+", content):
        if not segment.strip():
            continue
        if not APPROVAL_EVIDENCE_DECLARATION_RE.search(segment):
            continue
        if APPROVAL_EVIDENCE_NEGATION_RE.search(segment):
            continue
        return True
    return False


def _target_paths_include_approval_evidence_packet(target_paths: set[str]) -> bool:
    for path in target_paths:
        if path == APPROVAL_EVIDENCE_TARGET_DIR:
            return True
        if path.startswith(f"{APPROVAL_EVIDENCE_TARGET_DIR}/"):
            return True
    return False


def _approval_evidence_target_paths_ask_reason(content: str) -> str | None:
    """Checkpoint approval-evidence work that omits its packet path envelope."""
    first_line = _first_nonblank_line(content)
    if first_line not in PENDING_PREFLIGHT_STATUSES:
        return None
    if _bridge_kind_is_metadata_exempt(content):
        return None
    if BRIDGE_KIND_LINE_RE.search(content) and not _bridge_kind_is_implementation_proposal(content):
        return None
    if not _declares_approval_evidence_scope(content):
        return None
    target_paths = _target_path_set_from_content(content)
    if _target_paths_include_approval_evidence_packet(target_paths):
        return None
    return (
        "[Governance] This bridge proposal appears to declare formal/narrative artifact "
        "approval evidence or approval-packet work, but target_paths does not include "
        "a concrete `.groundtruth/formal-artifact-approvals/<packet>.json` path or the "
        "`.groundtruth/formal-artifact-approvals/**` envelope. Add the approval-packet "
        "path to target_paths, or confirm the proposal performs no approval-evidence work. "
        "(Ask checkpoint per bridge target_paths approval-evidence completeness check.)"
    )


def _has_spec_derived_verification(content: str) -> bool:
    return bool(
        _has_concrete_spec_links(content)
        and SPEC_TEST_HEADING_RE.search(content)
        and COMMAND_EVIDENCE_RE.search(content)
    )


def _has_commit_finalization_evidence(content: str) -> bool:
    lines = content.splitlines()
    start: int | None = None
    for index, line in enumerate(lines):
        if COMMIT_FINALIZATION_HEADING_RE.match(line.strip()):
            start = index + 1
            break
    if start is None:
        return False
    section = "\n".join(_collect_section_lines(lines, start))
    # WI-6365: both accepted forms require the committed path set. What differs is
    # how the commit is identified -- same-transaction (legacy atomic helper) or a
    # work-product commit reference (canonical commit-then-verdict ordering).
    # Evidence must still be present and substantive; an empty section fails.
    if not FINALIZATION_PATH_BULLET_RE.search(section):
        return False
    return bool(SAME_TRANSACTION_PATH_SET_RE.search(section) or WORK_PRODUCT_COMMIT_RE.search(section))


def _synthetic_session_context_id_for_content(content: str) -> str | None:
    session_context_id = extract_author_metadata(content).get("author_session_context_id")
    if is_synthetic_session_context_id(session_context_id):
        return str(session_context_id).strip().strip("`")
    return None


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


def _has_concrete_simplification_accounting(content: str) -> bool:
    """Heading present AND section text non-empty AND not placeholder-only (WI-6741).

    Mirrors ``_has_concrete_owner_decisions_section``. The one deliberate
    divergence is the placeholder set: an author who writes "nothing gets
    smaller" has answered the question, so that must pass. Only genuinely
    unfilled markers -- ``tbd``, ``todo``, ``fill in``, a bare ``?`` -- fail.

    The gate cannot detect an insincere answer, and does not try. Its job is to
    put the question on the path the author already walks; whether the answer is
    honest is what the Loyal Opposition simplicity challenge (WI-6742) exists to
    test.
    """
    lines = content.splitlines()
    start: int | None = None
    for i, line in enumerate(lines):
        if SIMPLIFICATION_ACCOUNTING_HEADING_RE.match(line.strip()):
            start = i + 1
            break
    if start is None:
        return False
    section = _collect_section_lines(lines, start)
    if not "\n".join(section).strip():
        return False
    nonblank = [line for line in (ln.strip() for ln in section) if line]
    return any(not SIMPLIFICATION_ACCOUNTING_PLACEHOLDER_LINE_RE.match(line) for line in nonblank)


def _target_paths_touch_harness_surface(content: str) -> bool:
    """Return True when any declared target path is a harness-behavioral surface.

    Realizes the PARITY-DISPOSITION-GATE trigger: a proposal whose target_paths
    touch ``.claude/settings.json``, ``.codex/hooks.json``, ``.claude/hooks/**``,
    ``.codex/gtkb-hooks/**``, ``.claude/skills/**``, or ``.codex/skills/**`` is a
    harness-surface change. Paths are normalized by ``_target_path_set_from_content``.
    """
    for path in _target_path_set_from_content(content):
        for marker in HARNESS_SURFACE_PATH_MARKERS:
            normalized_marker = marker.rstrip("/")
            if path == normalized_marker or path.startswith(marker):
                return True
    return False


def _has_concrete_cross_harness_disposition_section(content: str) -> bool:
    """Heading present AND at least one substantive (non-placeholder, non-bullet) line.

    Mirrors ``_has_concrete_owner_decisions_section`` but additionally rejects
    lines that are only bullet/punctuation markers (a bare ``-`` or blank bullet)
    so a disposition section must carry real per-harness content, not a token.
    """
    lines = content.splitlines()
    start: int | None = None
    for idx, line in enumerate(lines):
        if CROSS_HARNESS_DISPOSITION_HEADING_RE.match(line.strip()):
            start = idx + 1
            break
    if start is None:
        return False
    for raw in _collect_section_lines(lines, start):
        stripped = raw.strip()
        if not stripped or OWNER_DECISIONS_PLACEHOLDER_LINE_RE.match(stripped):
            continue
        residue = DISPOSITION_NONCONTENT_PREFIX_RE.sub("", stripped)
        if re.search(r"[A-Za-z0-9]", residue):
            return True
    return False


def _nonimpairment_value_is_concrete(value: object) -> bool:
    if isinstance(value, str):
        return value.strip().lower() not in NONIMPAIRMENT_PLACEHOLDERS
    if isinstance(value, list):
        return bool(value) and all(_nonimpairment_value_is_concrete(item) for item in value)
    if isinstance(value, dict):
        return bool(value) and all(_nonimpairment_value_is_concrete(item) for item in value.values())
    return value is not None


def _nonimpairment_disposition_gap(content: str) -> str | None:
    """Validate the structured Intuitiveness/Non-Impairment Disposition."""
    lines = content.splitlines()
    start: int | None = None
    for index, line in enumerate(lines):
        if NONIMPAIRMENT_DISPOSITION_HEADING_RE.match(line.strip()):
            start = index + 1
            break
    if start is None:
        return "section absent"
    section = "\n".join(_collect_section_lines(lines, start)).strip()
    fenced_blocks = re.findall(r"```(?:json)?\s*([\s\S]*?)```", section, flags=re.IGNORECASE)
    if len(fenced_blocks) != 1:
        return "section must contain exactly one fenced JSON object"
    try:
        disposition = json.loads(fenced_blocks[0])
    except json.JSONDecodeError as exc:
        return f"disposition JSON is malformed: {exc.msg}"
    if not isinstance(disposition, dict):
        return "disposition JSON root must be an object"
    if disposition.get("schema_version") != 1:
        return "schema_version must be 1"
    if disposition.get("applicability") not in {"applicable", "not_applicable"}:
        return "applicability must be applicable or not_applicable"
    missing = sorted(NONIMPAIRMENT_REQUIRED_FIELDS - disposition.keys())
    if missing:
        return "missing fields: " + ", ".join(missing)
    nonconcrete = sorted(
        field for field in NONIMPAIRMENT_REQUIRED_FIELDS if not _nonimpairment_value_is_concrete(disposition.get(field))
    )
    if nonconcrete:
        return "placeholder or empty fields: " + ", ".join(nonconcrete)
    return None


def _prior_deliberations_has_unedited_placeholder(content: str) -> bool:
    """True when ## Prior Deliberations still has the helper placeholder."""
    lines = content.splitlines()
    start: int | None = None
    for idx, line in enumerate(lines):
        if PRIOR_DELIBERATIONS_HEADING_RE.match(line.strip()):
            start = idx + 1
            break
    if start is None:
        return False
    section = _collect_section_lines(lines, start)
    return any(line.strip() == NO_PRIOR_DELIBS_PLACEHOLDER for line in section)


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


def _bridge_kind_is_implementation_proposal(content: str) -> bool:
    """Return True when the proposal's bridge_kind denotes an implementation
    proposal (canonical ``prime_proposal`` or the colloquial
    ``implementation_proposal`` token used via the helper path).

    Used by the WI-3439 Requirement Sufficiency gate so the check fires ONLY for
    implementation proposals -- never for implementation reports, verdicts, or
    advisories, which legitimately lack the subsection. This is a POSITIVE
    predicate, deliberately NOT the negative ``_bridge_kind_is_metadata_exempt``
    set: that set does not contain ``implementation_report`` and so would wrongly
    gate post-implementation reports (GO constraint 1). A proposal that omits the
    bridge_kind line returns False (conservative; the project-linkage gate still
    catches missing metadata).
    """
    match = BRIDGE_KIND_LINE_RE.search(content)
    if not match:
        return False
    return match.group(1).strip().lower() in BRIDGE_KIND_IMPLEMENTATION_PROPOSAL


def _requirement_sufficiency_section_gap(content: str) -> str | None:
    """Return a short gap descriptor when an implementation proposal's
    ``## Requirement Sufficiency`` subsection is absent, placeholder-only, or
    does not carry EXACTLY ONE bounded operative state; return None when it is
    substantive with a single operative state.

    Operative states per .agent/rules/file-bridge-protocol.md section "Mandatory
    Implementation-Start Authorization Metadata": exactly one of "Existing
    requirements sufficient" or "New or revised requirement required before
    implementation". The two states are mutually exclusive, so a section that
    asserts BOTH is a gap (WI-3439 verification NO-GO -008). Mirrors the existing
    ``_has_concrete_spec_links`` / ``_has_concrete_owner_decisions_section``
    section-presence machinery (heading scan + ``_collect_section_lines`` +
    placeholder-line rejection).
    """
    lines = content.splitlines()
    start: int | None = None
    for idx, line in enumerate(lines):
        if REQUIREMENT_SUFFICIENCY_HEADING_RE.match(line.strip()):
            start = idx + 1
            break
    if start is None:
        return "section absent"
    section = _collect_section_lines(lines, start)
    nonblank = [stripped for stripped in (ln.strip() for ln in section) if stripped]
    if not nonblank:
        return "section empty"
    if not any(not SPEC_PLACEHOLDER_LINE_RE.match(ln) for ln in nonblank):
        return "section placeholder-only"
    joined = "\n".join(section)
    states_present = sum(1 for state_re in REQUIREMENT_SUFFICIENCY_OPERATIVE_STATES if state_re.search(joined))
    state = _implementation_requirement_sufficiency_state(content)
    if state == "unrecognized" or states_present == 0:
        return (
            "no operative state ('Existing requirements sufficient' or "
            "'New or revised requirement required before implementation')"
        )
    if states_present > 1 and state != "sufficient":
        return (
            "multiple operative states (exactly one required: 'Existing "
            "requirements sufficient' XOR 'New or revised requirement required "
            "before implementation')"
        )
    if state not in {"sufficient", "gap"}:
        return (
            "no operative state ('Existing requirements sufficient' or "
            "'New or revised requirement required before implementation')"
        )
    return None


def _project_metadata_gaps(content: str) -> list[str]:
    """Return the list of missing project-linkage metadata lines.

    Empty list means all three lines are present
    (CLAUSE-PROJECT-METADATA-PRESENT satisfied).
    """
    gaps: list[str] = []
    if not PROJECT_LINE_RE.search(content):
        gaps.append("Project:")
    if not WORK_ITEM_LINE_RE.search(content):
        gaps.append("Work Item:")
    return gaps


def _extract_project_metadata(content: str) -> tuple[str | None, str | None]:
    """Return (project_id, work_item_id) captured from the two project-linkage
    metadata lines, or None per field when absent."""
    proj = PROJECT_VALUE_RE.search(content)
    wi = WORK_ITEM_VALUE_RE.search(content)
    return (
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
    """Return a specific failed-condition token when the cited Work Item fails
    the live MemBase membership check for the cited Project, or None when it
    passes.

    Fails open: missing DB or any sqlite/OS error returns None (with a stderr
    warning) so the gate never blocks on infrastructure failure. The check only
    runs when both metadata lines are present (the metadata-presence gate
    handles absence). Condition tokens, in evaluation order:
    wi-not-found-in-project, wi-membership-inactive.
    """
    project_id, work_item_id = _extract_project_metadata(content)
    if not (project_id and work_item_id):
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
    except (sqlite3.Error, OSError) as exc:
        print(f"[Governance] WI-project membership check warning: {exc}", file=sys.stderr)
        return None
    finally:
        if conn is not None:
            conn.close()
    return None


def _project_membership_refusal_message(content: str, cwd_path: Path, membership_gap: str) -> str:
    """Render the stable refusal classification for a failed membership check."""
    project_id, work_item_id = _extract_project_metadata(content)
    return (
        "[Governance] Bridge proposal fails the live work-item/project "
        f"membership check: {membership_gap}. Cited WI={work_item_id}, "
        f"Project={project_id}. "
        "The cited metadata must resolve to an active project membership in "
        "MemBase; add it with `gt projects add-item`. "
        "(Hard-block per DCL-WORK-ITEM-MUST-BELONG-TO-APPROVED-PROJECT-001/"
        "CLAUSE-BRIDGE-WI-PROJECT-MEMBERSHIP.)"
    )


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


def _applicability_preflight_section(content: str) -> str | None:
    lines = content.splitlines()
    for idx, line in enumerate(lines):
        if APPLICABILITY_PREFLIGHT_HEADING_RE.match(line.strip()):
            return "\n".join(_collect_section_lines(lines, idx + 1))
    return None


def _preflight_field(section: str, field_name: str) -> str | None:
    wanted = field_name.lower()
    for match in PREFLIGHT_FIELD_LINE_RE.finditer(section):
        if match.group("name").lower() == wanted:
            return match.group("value").strip()
    return None


def _root_relative_path(raw_path: str, project_root: Path) -> tuple[str, Path] | None:
    cleaned = raw_path.strip().strip("`").replace("\\", "/")
    if not cleaned:
        return None
    candidate = Path(cleaned)
    if not candidate.is_absolute():
        candidate = project_root / candidate
    try:
        resolved = candidate.resolve(strict=False)
        relative = resolved.relative_to(project_root.resolve())
    except (OSError, ValueError):
        return None
    return relative.as_posix(), resolved


def _candidate_evidence_hash(file_path: str, content: str, project_root: Path) -> str | None:
    try:
        from scripts.bridge_applicability_preflight import candidate_evidence_hash as shared_candidate_evidence_hash
    except (ImportError, OSError):
        shared_candidate_evidence_hash = None
    if shared_candidate_evidence_hash is not None:
        try:
            return shared_candidate_evidence_hash(file_path, content, project_root)
        except (OSError, ValueError):
            return None

    # Partial-installation fallback. Keep byte-equivalent semantics with the
    # public implementation and fail closed if the candidate is ambiguous.
    candidate_path = _root_relative_path(file_path, project_root)
    if candidate_path is None:
        return None
    normalized_content = content.replace("\r\n", "\n").replace("\r", "\n")
    normalized_content, replacements = CANDIDATE_EVIDENCE_HASH_LINE_RE.subn(
        lambda match: match.group("prefix") + CANDIDATE_EVIDENCE_HASH_SENTINEL + match.group("suffix"),
        normalized_content,
    )
    if replacements != 1:
        return None
    payload = candidate_path[0] + "\n" + normalized_content
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _verdict_preflight_freshness_deny_reason(
    *,
    cwd_path: Path,
    file_path: str,
    content: str,
) -> str | None:
    status = _first_nonblank_line(content)
    if status not in VERDICT_PREFLIGHT_FRESHNESS_STATUSES:
        return None
    section = _applicability_preflight_section(content)
    if section is None:
        return None

    project_root = _canonical_project_root(cwd_path)
    bridge_id = _extract_bridge_id_from_path(file_path)
    if bridge_id is None:
        return "[Governance] Verdict applicability freshness check could not resolve the candidate bridge thread."

    responds_match = RESPONDS_TO_BRIDGE_PATH_RE.search(content)
    if responds_match is None:
        return (
            "[Governance] Verdict applicability freshness check requires an exact root-contained "
            "`Responds to:` bridge artifact."
        )
    responds_to = _root_relative_path(responds_match.group("path"), project_root)
    if responds_to is None:
        return (
            "[Governance] Verdict applicability freshness check rejected an out-of-root or invalid `Responds to:` path."
        )
    responds_relative, responds_path = responds_to
    responds_version = BRIDGE_VERSIONED_FILE_RE.match(responds_path.name)
    if (
        not responds_path.is_file()
        or responds_path.parent != (project_root / "bridge").resolve()
        or responds_version is None
        or responds_version.group(1) != bridge_id
    ):
        return (
            "[Governance] Verdict applicability freshness check requires `Responds to:` to name an "
            "existing canonical version of the same bridge thread."
        )

    packet_hash = _preflight_field(section, "packet_hash")
    packet_bridge_id = _preflight_field(section, "bridge_document_name")
    source_anchor = _preflight_field(section, "content_file")
    if source_anchor in {None, "", "(none)"}:
        source_anchor = _preflight_field(section, "operative_file")
    anchored_source = _root_relative_path(source_anchor or "", project_root)
    if anchored_source is None or anchored_source[0] != responds_relative:
        return (
            "[Governance] Verdict applicability freshness check rejected a source mismatch: "
            "`content_file`/`operative_file` must equal the exact `Responds to:` artifact."
        )
    if packet_bridge_id != bridge_id:
        return (
            "[Governance] Verdict applicability freshness check rejected a bridge-document mismatch: "
            "`bridge_document_name` must match the candidate thread."
        )
    if packet_hash is None or re.fullmatch(r"sha256:[0-9a-f]{64}", packet_hash, re.IGNORECASE) is None:
        return "[Governance] Verdict applicability freshness check requires a valid `packet_hash` anchor."

    try:
        from scripts.bridge_applicability_preflight import build_packet

        expected_packet = build_packet(
            bridge_id=bridge_id,
            bridge_dir=project_root / "bridge",
            config_path=project_root / "config" / "governance" / "spec-applicability.toml",
            db_path=project_root / "groundtruth.db",
            content_file=responds_path,
        )
    except (Exception, SystemExit) as exc:
        return f"[Governance] Verdict applicability freshness check could not rebuild the source packet: {exc}"
    expected_packet_hash = str(expected_packet.get("packet_hash") or "")
    if packet_hash.lower() != expected_packet_hash.lower():
        return (
            "[Governance] Verdict applicability freshness check rejected a stale packet_hash; "
            f"expected `{expected_packet_hash}` for `{responds_relative}`."
        )

    # Preflight assertion integrity (WI-5850 emergency-bootstrap, 2026-07-31):
    # the freshness match above proves packet_hash was built over the current
    # responded-to content, but NOT that the verdict's asserted PASS/FAIL matches
    # the re-derived truth. The 2026-07-31 autonomous LO loop exploited exactly
    # this gap: it embedded the real packet_hash (freshness passes) while
    # hard-coding `preflight_passed: true` / `missing_required_specs: []` over a
    # real result of False with required specs missing. Re-derive from the packet
    # already computed above and refuse any verdict that attests a passing
    # preflight the source does not actually pass. Authority: WI-5850,
    # DELIB-HARNESS-NO-ACTION-LO-RESPONSE-SET-20260702, .agent/rules/counterpart-review-gate.md
    # ("GO and VERIFIED are valid only when the preflight reports missing_required_specs: []").
    real_passed = bool(expected_packet.get("preflight_passed"))
    real_missing = [str(spec) for spec in (expected_packet.get("missing_required_specs") or [])]
    asserted_passed_raw = _preflight_field(section, "preflight_passed")
    if asserted_passed_raw is not None:
        asserted_passed = asserted_passed_raw.strip().strip("`").lower() == "true"
        if asserted_passed and not real_passed:
            return (
                "[Governance] Verdict preflight assertion is fabricated: the verdict asserts "
                "`preflight_passed: true` but the re-derived applicability preflight for the "
                f"responded-to artifact `{responds_relative}` returns False "
                f"(real missing_required_specs: {real_missing}). A GO/NO-GO/VERIFIED verdict may "
                "not attest a passing preflight the source does not actually pass. "
                "(Fabricated-attestation guard; WI-5850 emergency-bootstrap.)"
            )

    embedded_candidate_hash = _preflight_field(section, "candidate_evidence_hash")
    expected_candidate_hash = _candidate_evidence_hash(file_path, content, project_root)
    if (
        embedded_candidate_hash is None
        or re.fullmatch(r"sha256:[0-9a-f]{64}", embedded_candidate_hash, re.IGNORECASE) is None
        or expected_candidate_hash is None
        or embedded_candidate_hash.lower() != expected_candidate_hash.lower()
    ):
        expected = expected_candidate_hash or "<unavailable>"
        return (
            "[Governance] Verdict applicability freshness check rejected a stale or missing "
            f"`candidate_evidence_hash`; expected `{expected}` for the final normalized candidate bytes."
        )
    return None


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
            **_no_window_subprocess_kwargs(),
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
    blocking_errors = packet.get("blocking_errors") or []
    if packet.get("preflight_passed") is False or missing_required or blocking_errors:
        return False, json.dumps(
            {
                "missing_required_specs": missing_required,
                "blocking_errors": blocking_errors,
            },
            sort_keys=True,
        )
    return True, ""


def _trim_preflight_output(output: str, *, limit: int = 2400) -> str:
    text = re.sub(r"\s+\n", "\n", output).strip()
    if len(text) <= limit:
        return text
    return text[:limit].rstrip() + " ... <truncated>"


def _run_pending_clause_preflight(
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
                "scripts/adr_dcl_clause_preflight.py",
                "--bridge-id",
                bridge_id,
                "--content-file",
                str(scratch_path),
            ],
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
            **_no_window_subprocess_kwargs(),
        )
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        print(f"[Governance] ADR/DCL clause preflight warning for {file_path}: {exc}", file=sys.stderr)
        return True, ""
    finally:
        if scratch_path is not None:
            try:
                scratch_path.unlink(missing_ok=True)
            except OSError as exc:
                print(f"[Governance] Could not remove bridge clause preflight scratch file: {exc}", file=sys.stderr)

    combined_output = "\n".join(part for part in (result.stdout, result.stderr) if part).strip()
    if result.returncode == 0:
        return True, ""
    if result.returncode == 5:
        return False, _trim_preflight_output(combined_output)
    print(f"[Governance] ADR/DCL clause preflight warning for {file_path}: {combined_output}", file=sys.stderr)
    return True, ""


def _read_proposal_target_paths(
    project_root: Path,
    doc_name: str,
    file_groups: dict[str, list[tuple[int, Path]]] | None = None,
) -> list[str]:
    """Read target_paths from the latest Prime-authored proposal file."""
    proposal_path: Path | None = None
    groups = file_groups if file_groups is not None else _versioned_bridge_file_groups(project_root)
    for _version, path in groups.get(doc_name, []):
        status = _status_from_versioned_bridge_file(path)
        if status in {"NEW", "REVISED"}:
            proposal_path = path
            break
    if proposal_path is None:
        return []
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


def _pending_target_cache_path(project_root: Path) -> Path:
    return project_root / PENDING_TARGET_CACHE_RELATIVE_PATH


def _bridge_dir_signature(project_root: Path) -> dict[str, int]:
    bridge_dir = project_root / "bridge"
    signature = {"file_count": 0, "max_mtime_ns": 0}
    try:
        with os.scandir(bridge_dir) as entries:
            for entry in entries:
                if not entry.is_file():
                    continue
                if not BRIDGE_VERSIONED_FILE_RE.match(entry.name):
                    continue
                signature["file_count"] += 1
                try:
                    stat_result = entry.stat()
                except OSError:
                    continue
                mtime_ns = getattr(stat_result, "st_mtime_ns", int(stat_result.st_mtime * 1_000_000_000))
                signature["max_mtime_ns"] = max(signature["max_mtime_ns"], int(mtime_ns))
    except OSError:
        pass
    return signature


def _read_pending_target_cache(project_root: Path, signature: dict[str, int]) -> list[dict[str, object]] | None:
    try:
        payload = json.loads(_pending_target_cache_path(project_root).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if payload.get("schema_version") != PENDING_TARGET_CACHE_SCHEMA_VERSION:
        return None
    if payload.get("bridge_signature") != signature:
        return None
    records = payload.get("records")
    if not isinstance(records, list):
        return None
    return [record for record in records if isinstance(record, dict)]


def _write_pending_target_cache(
    project_root: Path,
    signature: dict[str, int],
    records: list[dict[str, object]],
) -> None:
    cache_path = _pending_target_cache_path(project_root)
    payload = {
        "schema_version": PENDING_TARGET_CACHE_SCHEMA_VERSION,
        "bridge_signature": signature,
        "records": records,
    }
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = cache_path.with_name(f"{cache_path.name}.{uuid4().hex}.tmp")
        tmp_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        tmp_path.replace(cache_path)
    except OSError:
        pass


def _build_pending_proposal_targets(project_root: Path) -> list[dict[str, object]]:
    file_groups = _versioned_bridge_file_groups(project_root)
    records: list[dict[str, object]] = []
    for doc_name, files in file_groups.items():
        if not files:
            continue
        _version, latest_path = files[0]
        status = _status_from_versioned_bridge_file(latest_path)
        if status not in ("NEW", "REVISED", "NO-GO"):
            continue
        records.append(
            {
                "document": doc_name,
                "status": status,
                "target_paths": _read_proposal_target_paths(project_root, doc_name, file_groups),
            }
        )
    return records


def _pending_proposal_target_records(project_root: Path) -> list[dict[str, object]]:
    signature = _bridge_dir_signature(project_root)
    cached = _read_pending_target_cache(project_root, signature)
    if cached is not None:
        return cached
    records = _build_pending_proposal_targets(project_root)
    _write_pending_target_cache(project_root, signature, records)
    return records


PARKED_THREAD_AGE_DAYS = 30


def _path_claimed_by_target(file_path_normalized: str, target: str) -> bool:
    """Root-anchored match of a repo-relative path against a target_paths entry.

    WI-6216 D1(c). The prior implementation used ``endswith``, which let an
    unrelated thread claim a file whose path merely ended with the target
    string. Matching is now anchored at the repository root: a glob is matched
    with fnmatch, and a non-glob target must be equal or a directory prefix.
    """

    target_norm = target.replace("\\", "/").strip()
    if not target_norm:
        return False
    if any(ch in target_norm for ch in "*?["):
        return fnmatch.fnmatchcase(file_path_normalized, target_norm)
    if file_path_normalized == target_norm:
        return True
    return file_path_normalized.startswith(target_norm.rstrip("/") + "/")


def _thread_last_activity(project_root: Path, doc_name: str) -> float:
    """Newest bridge-file mtime for a thread slug, or 0.0 when unreadable."""

    slug = doc_name[:-3] if doc_name.endswith(".md") else doc_name
    slug = re.sub(r"-\d{3}$", "", slug)
    newest = 0.0
    try:
        for path in (project_root / "bridge").glob(f"{slug}-*.md"):
            try:
                newest = max(newest, path.stat().st_mtime)
            except OSError:
                continue
    except OSError:
        return 0.0
    return newest


def _live_packet_authorizes(project_root: Path, file_path_normalized: str) -> bool:
    """True when an unexpired implementation-start packet authorizes this path.

    WI-6216 D1(a). A live packet means the session already cleared the bridge
    GO gate for this exact path, so a pending-proposal banner is noise that
    misdirects the implementer to an unrelated thread.
    """

    packet_dir = project_root / ".gtkb-state" / "implementation-authorizations" / "by-bridge"
    try:
        packets = list(packet_dir.glob("*.json"))
    except OSError:
        return False
    now = _dt.datetime.now(_dt.UTC)
    for packet_path in packets:
        try:
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        expires_raw = str(packet.get("expires_at") or "")
        try:
            expires = _dt.datetime.fromisoformat(expires_raw.replace("Z", "+00:00"))
        except ValueError:
            continue
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=_dt.UTC)
        if expires <= now:
            continue
        globs = packet.get("target_path_globs")
        if not isinstance(globs, list):
            continue
        for entry in globs:
            if isinstance(entry, str) and _path_claimed_by_target(file_path_normalized, entry):
                return True
    return False


def _pending_proposal_ask_reason(project_root: Path, file_path: str) -> str | None:
    """Return an ask-checkpoint reason when file_path matches a pending
    proposal's target_paths, or None.

    WI-6216 D1. Four corrections to the prior behaviour, which matched by path
    suffix against every pending thread and returned the FIRST match:

    (a) a live implementation-start packet authorizing this path suppresses the
        banner entirely;
    (b) among several matching threads the most recently active one is named,
        rather than whichever happened to be enumerated first;
    (c) matching is root-anchored (glob or exact/prefix), not suffix-based;
    (d) a NO-GO thread with no new version in 30 days no longer claims paths.
    """

    file_path_normalized = file_path.replace("\\", "/")

    if _live_packet_authorizes(project_root, file_path_normalized):
        return None

    now = time.time()
    parked_cutoff = now - (PARKED_THREAD_AGE_DAYS * 86400)
    matches: list[tuple[float, str, str]] = []

    for record in _pending_proposal_target_records(project_root):
        doc_name = str(record.get("document") or "")
        status = str(record.get("status") or "")
        if status not in ("NEW", "REVISED", "NO-GO"):
            continue
        target_paths = record.get("target_paths")
        if not isinstance(target_paths, list):
            continue
        if not any(isinstance(tp, str) and _path_claimed_by_target(file_path_normalized, tp) for tp in target_paths):
            continue

        last_activity = _thread_last_activity(project_root, doc_name)
        # (d) A long-parked NO-GO no longer claims paths. NEW/REVISED threads
        # are live review work and are not aged out.
        if status == "NO-GO" and last_activity and last_activity < parked_cutoff:
            continue
        matches.append((last_activity, doc_name, status))

    if not matches:
        return None

    # (b) Prefer the most recently active thread.
    _activity, doc_name, status = max(matches, key=lambda item: item[0])
    if status == "NO-GO":
        return (
            "[Governance] Bridge proposal for this module has NO-GO status. "
            f"Review Codex findings at bridge/{doc_name} before implementing."
        )
    return (
        f"[Governance] Bridge proposal for {doc_name} is pending Codex review ({status}). "
        "Wait for GO verdict before implementing."
    )


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


def _verdict_evidence_anchor_deny_reason(content: str, project_root: Path) -> str | None:
    """Deny reason when a NO-GO/VERIFIED verdict cites fabricated evidence anchors.

    WI-4520: a reviewing-harness NO-GO cited a non-existent "Draft Template
    Placeholder" at line 86 of a proposal whose line 86 was '## Implementation
    Plan'. This gate validates that a gated verdict's cited line numbers and
    quoted strings actually exist in the operative file(s) it references.

    Fails OPEN: any import or runtime error returns None so this gate can never
    block a verdict for an infrastructure reason (the bridge is top priority).
    """
    try:
        from scripts.verdict_evidence_anchor_preflight import (
            validate_verdict_evidence_anchors,
            violation_summary,
        )
    except Exception:  # pragma: no cover - fail open on partial install
        return None
    try:
        violations = validate_verdict_evidence_anchors(content, project_root=project_root)
    except Exception:  # pragma: no cover - fail open on parser error
        return None
    if not violations:
        return None
    return (
        "[Governance] This NO-GO/VERIFIED verdict cites evidence anchors that do not "
        "exist in the operative file(s): "
        + violation_summary(violations)
        + ". Point the citation at real line numbers / quoted text, or mark the finding "
        "[inference] / [no exact anchor] / [absent] if it is intentionally not an "
        "exact-text claim. (Hard-block per WI-4520 verdict-evidence-anchor preflight; "
        "see scripts/verdict_evidence_anchor_preflight.py.)"
    )


def _verdict_self_review_deny(file_path: str, content: str, cwd_path: Path) -> str | None:
    """Block a self-review GO/NO-GO/VERIFIED verdict at write time (WI-4829).

    A verdict is a self-review when its ``author_session_context_id`` equals the
    ``author_session_context_id`` of the artifact it reviews (resolved via the
    verdict's ``Responds to:`` reference). Such a verdict is invalid under the
    session-context review-independence rule and must not reach disk. Fails closed
    on any refusal reason (equal author, missing/unreadable author metadata).

    The comparator import and evaluation are defensive: an unavailable module or an
    unexpected comparator error must never break legitimate bridge writes, so this
    returns ``None`` (allow) in those cases — the impl-start backstop remains.
    """
    bridge_id = _extract_bridge_id_from_path(file_path)
    if not bridge_id:
        return None
    try:
        from scripts.bridge_review_independence import verdict_self_review_reason

        project_root = _canonical_project_root(cwd_path)
        reason = verdict_self_review_reason(content, bridge_id, project_root)
    except Exception:
        return None
    if reason is None:
        return None
    return (
        f"[Governance] Self-review bridge verdict blocked ({reason}): a GO/NO-GO/VERIFIED "
        "verdict's author_session_context_id must be present and distinct from the reviewed "
        "artifact's author session. Review independence is session-context based; a verdict "
        "authored by the same session that authored the reviewed proposal/report is invalid "
        "and fails closed. File the verdict from a different session context. "
        "(Hard-block per WI-4829; GOV-DOCUMENT-AUTHOR-PROVENANCE-001; review-independence rule.)"
    )


def _no_action_prior_verdict_deny(file_path: str, content: str) -> str | None:
    """Block a NO-ACTION bridge write when the thread has no prior LO GO/NO-GO verdict.

    Enforces DCL-NO-ACTION-STATUS-SEMANTICS-001: a NO-ACTION entry is a Prime
    Builder rejection of a prior Loyal Opposition GO or NO-GO verdict, so it is
    well-formed only when a prior GO/NO-GO exists in the same numbered bridge
    thread. Advisory threads have no prior verdict, so writing NO-ACTION to close
    an advisory is always ill-formed. Fires only on a Write whose first non-blank
    line is exactly NO-ACTION; reads the thread's lower-numbered sibling versions
    from the bridge directory and allows the write only when one carries GO or
    NO-GO. Existing on-disk NO-ACTION files are not re-written, so the guard has
    no retroactive effect (append-only bridge chain).
    """
    if not _is_bridge_markdown_file(file_path):
        return None
    if _first_nonblank_line(content) != "NO-ACTION":
        return None
    name_match = BRIDGE_VERSIONED_FILE_RE.match(Path(file_path).name)
    if name_match is None:
        return None
    bridge_id = name_match.group(1)
    this_version = int(name_match.group(2))
    bridge_dir = Path(file_path).resolve().parent
    try:
        siblings = list(bridge_dir.glob(f"{bridge_id}-*.md"))
    except OSError:
        siblings = []
    for sibling in siblings:
        sib_match = BRIDGE_VERSIONED_FILE_RE.match(sibling.name)
        if sib_match is None or sib_match.group(1) != bridge_id:
            continue
        if int(sib_match.group(2)) >= this_version:
            continue
        if _status_from_versioned_bridge_file(sibling) in {"GO", "NO-GO"}:
            return None
    return (
        "[Governance] NO-ACTION bridge write blocked: a NO-ACTION entry is a Prime Builder "
        "rejection of a prior Loyal Opposition GO or NO-GO verdict, so it is well-formed only when "
        f"thread '{bridge_id}' already contains a GO or NO-GO verdict for Prime to reject; none was "
        "found. Do NOT use NO-ACTION to close an ADVISORY thread or record a Prime 'no further "
        "action' close -- keep the thread ADVISORY with a recorded disposition note, or move it to "
        "a terminal WITHDRAWN status with cited rationale. (Hard-block per "
        "DCL-NO-ACTION-STATUS-SEMANTICS-001; see .agent/rules/file-bridge-protocol.md section "
        "'NO-ACTION Status'.)"
    )


# WI-5850 emergency-bootstrap (2026-07-31): close-intent detector for NO-ACTION.
# DCL-NO-ACTION-STATUS-SEMANTICS-001 forbids using NO-ACTION to record a Prime
# "no further action" close; a lawful NO-ACTION rejects a governance-noncompliant
# verdict and states what the reviewer must correct. The 2026-07-31 autonomous
# reviewing-harness loop wrote 322 "auto-disposition" NO-ACTION files that close threads
# instead of correcting a verdict. Detecting the *presence of remedy* is unusable
# (the lawful corpus is too inconsistent -- 2.6% false-positive). Detecting
# *close/disposal intent* (N1) plus *self-granted clearance* (N2) is measured at
# 0/269 false-positive against the lawful corpus and catches the unlawful set.
# Regex fragility (do NOT loosen; each loosening was measured to add FPs):
#   - `disposition-?close` must stay hyphen-optional, NOT `[-\s]?`: lawful files
#     quote "Advisory-disposition close" (space) while criticizing the practice.
#   - `acknowledges? receipt` must stay two-word, NOT bare `acknowledg`.
# Body is whitespace-collapsed and lowercased before matching (matches the audit
# measurement). Only fires when the first non-blank line is exactly NO-ACTION.
_NO_ACTION_CLOSE_INTENT_N1 = re.compile(
    r"this is a terminal disposition"
    r"|thread'?s? latest status is now no-action"
    r"|(?:disposed|disposition) as unactionable"
    r"|auto-?disposition"
    r"|disposition-?close"
    r"|removed from the actionable"
    r"|acknowledges? receipt"
    r"|carrier acknowledgment"
    r"|no (?:further|derived) (?:prime builder )?(?:action|work) is (?:due|required)"
    r"|informational audit trail acknowledged"
    r"|no action or code mutation is requested"
)
_NO_ACTION_CLOSE_INTENT_N2 = re.compile(
    r"(?:blocking (?:finding|condition)s?|finding f\d|the (?:sole|single) (?:dispositive )?"
    r"(?:blocking )?(?:finding|question|owner-gated question))[^.]{0,160}?"
    r"(?:is|are|now|already) (?:already )?(?:resolved|cleared|satisfied|unblocked|moot)"
    r"|##\s*owner decision applied"
    r"|resolved by operational intervention"
    r"|(?:blocking finding|authority gap|ambiguity) (?:is )?(?:already )?resolved"
    r"|no-action on (?:version )?v?\d+ as (?:a )?(?:blocking|review) verdict"
)


def _no_action_close_intent_deny(file_path: str, content: str) -> str | None:
    """Block a NO-ACTION whose body is a close/disposal rather than a verdict correction.

    Complements _no_action_prior_verdict_deny (which requires a prior verdict to
    exist). This guard fires even when a prior GO/NO-GO exists -- the 2026-07-31 burst
    files DID sit on prior verdicts, so the prior-verdict check passed; the defect
    was that the body closed the thread instead of stating a correction.
    """
    if not _is_bridge_markdown_file(file_path):
        return None
    if _first_nonblank_line(content) != "NO-ACTION":
        return None
    body = content
    # strip the copyright footer so its "(c) ... rights reserved" never matches
    marker = body.lower().rfind("rights reserved")
    if marker != -1:
        line_start = body.rfind("\n", 0, marker)
        body = body[:line_start] if line_start != -1 else body
    collapsed = re.sub(r"\s+", " ", body).lower()
    hit = None
    if _NO_ACTION_CLOSE_INTENT_N1.search(collapsed):
        hit = "close/disposal language (N1)"
    elif _NO_ACTION_CLOSE_INTENT_N2.search(collapsed):
        hit = "self-granted clearance of a blocking finding (N2)"
    if hit is None:
        return None
    return (
        "[Governance] NO-ACTION bridge write blocked: the body reads as a "
        f"{hit}, not a rejection of a governance-noncompliant verdict. Per "
        "DCL-NO-ACTION-STATUS-SEMANTICS-001 a NO-ACTION must state what the reviewing "
        "role must fix and route the thread back for a corrected verdict; it MUST NOT be "
        "used to record a Prime 'no further action' / disposition-close. Use WITHDRAWN "
        "(with cited owner rationale) to terminate a thread, or file a substantive "
        "correction directive. (Hard-block per WI-5850 emergency-bootstrap.)"
    )


def _bridge_envelope_head_deny_reason(content: str) -> str | None:
    try:
        validate_bridge_envelope_head(content, require_dispatchable=True)
    except BridgeEnvelopeError as exc:
        return (
            "[Governance] Bridge artifact-head envelope invalid: "
            f"{exc}. Status-bearing dispatchable bridge files must keep the status token on line 1, "
            "then `::init gtkb <pb|lo>` on line 2 and `::open <activity>` on line 3. "
            "(Hard-block per ADR-BRIDGE-ARTIFACT-HEAD-ENVELOPE-001 and "
            "DCL-BRIDGE-ENVELOPE-LINE-AUTHORING-PLACEMENT-001.)"
        )
    return None


def _deny_reason_for_content(
    *,
    cwd_path: Path,
    file_path: str,
    content: str,
    run_pending_preflight: bool = True,
) -> str | None:
    if _is_retired_bridge_aggregate_file(file_path):
        return (
            "[Governance] Retired bridge aggregate files are not live or writable bridge surfaces. "
            "Use dispatcher/TAFE state plus status-bearing versioned bridge files."
        )
    if _is_lo_verdict_bridge_file(file_path):
        return (
            "[Governance] Noncanonical bridge verdict files are not writable authority. "
            "Write the next numbered bridge/<slug>-NNN.md file through the governed bridge path "
            "instead of bridge/*.lo-verdict.md."
        )

    if _is_bridge_markdown_file(file_path) and _versioned_bridge_file_exists_on_disk(file_path):
        bridge_id = _extract_bridge_id_from_path(file_path) or Path(file_path).name
        return (
            "[Governance] Bridge append-only boundary violation: "
            f"{Path(file_path).name} already exists on disk. "
            "Bridge thread state advances by writing the next numbered version, "
            "never by rewriting an existing numbered file in place. "
            f"Write bridge/{bridge_id}-NNN.md where NNN is the next version number. "
            "(Hard-block per GOV-FILE-BRIDGE-AUTHORITY-001 append-only boundary guard; "
            "WI-4740.)"
        )

    if _is_bridge_markdown_file(file_path) and content:
        if _body_status_token_violation(file_path, content):
            return (
                "[Governance] Versioned bridge files (bridge/<slug>-NNN.md) must carry a "
                "canonical status token in the artifact head: one of "
                # WI-7675: derived from the constant rather than restated. The
                # hardcoded list had already drifted, omitting VERDICT-REJECTED
                # for the whole life of the WI-7045 repair, so an author reading
                # the refusal was told a token was invalid when it was accepted.
                f"{', '.join(BRIDGE_STATUS_TOKENS)}. The first "
                "non-envelope line was "
                f"{_first_nonblank_line(content)!r}. The canonical header is '::init gtkb "
                "<pb|lo>' then '::open <activity>' then the status token (the ::init/::open "
                "lines may be null only for ADVISORY); a bare status token on line 1 also "
                "remains accepted. Existing files with a non-canonical head are "
                "grandfathered. (Hard-block per GTKB-GOV-PROPOSAL-STANDARDS Slice 1 "
                "body-status-token rule; see .agent/rules/file-bridge-protocol.md "
                "section 'Body Status-Token Rule'.)"
            )
        envelope_deny = _bridge_envelope_head_deny_reason(content)
        if envelope_deny:
            return envelope_deny
        kind_err = _bridge_kind_validation_error(content)
        if kind_err:
            return kind_err
        first_line = _first_nonblank_line(content)
        if first_line == "NO-ACTION":
            no_action_deny = _no_action_prior_verdict_deny(file_path, content)
            if no_action_deny:
                return no_action_deny
            close_intent_deny = _no_action_close_intent_deny(file_path, content)
            if close_intent_deny:
                return close_intent_deny
        if first_line in {"GO", "NO-GO", "VERIFIED"}:
            self_review_deny = _verdict_self_review_deny(file_path, content, cwd_path)
            if self_review_deny:
                return self_review_deny
        if first_line == "ADVISORY" and not _is_template_shaped_advisory_report(content):
            return (
                "[Governance] ADVISORY bridge reports must match the verified ADVISORY report template: "
                "first line ADVISORY; header fields bridge_kind, Document, Version, Author, Date; "
                "sections ## Source, ## Claim, ## Owner Decision Needed, "
                "## Recommended Prime Action, and ## Classification Slot."
            )
        if first_line in {"GO", "VERIFIED"} and not _has_clean_applicability_preflight(content):
            return (
                "[Governance] GO and VERIFIED bridge verdicts must include a clean "
                "Applicability Preflight section with packet_hash and "
                "missing_required_specs: []. Generate it with "
                "python scripts/bridge_applicability_preflight.py --bridge-id <document-name>. "
                "(Hard-block per mechanical cross-cutting specification applicability gate.)"
            )
        if first_line in VERDICT_PREFLIGHT_FRESHNESS_STATUSES:
            freshness_deny = _verdict_preflight_freshness_deny_reason(
                cwd_path=cwd_path,
                file_path=file_path,
                content=content,
            )
            if freshness_deny:
                return freshness_deny
        if first_line == "VERIFIED" and not _has_spec_derived_verification(content):
            return (
                "[Governance] VERIFIED bridge reports must carry Specification Links, "
                "a spec-to-test mapping, and executed test command evidence. "
                "(Hard-block per DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 + "
                "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001.)"
            )
        if first_line == "VERIFIED" and not _has_commit_finalization_evidence(content):
            return (
                "[Governance] VERIFIED bridge verdicts must include a Commit Finalization Evidence "
                "section carrying the committed path set as `-` bullets, plus ONE of: "
                "(a) 'Work-product commit: <sha>' -- the canonical form, where the commit precedes "
                "the verdict; or (b) 'Same-transaction path set' -- the legacy atomic-helper form. "
                "(Hard-block per the Mandatory VERIFIED Commit-Finalization Gate.)"
            )
        if first_line in {"NO-GO", "VERIFIED"}:
            anchor_reason = _verdict_evidence_anchor_deny_reason(content, cwd_path)
            if anchor_reason:
                return anchor_reason
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
            first_line in OWNER_DECISIONS_GATED_STATUSES
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
        if (
            first_line in PENDING_PREFLIGHT_STATUSES
            and _bridge_kind_is_implementation_proposal(content)
            and not _has_concrete_simplification_accounting(content)
        ):
            return (
                "[Governance] Implementation proposals must include a non-empty "
                "`## Simplification Accounting` section stating what gets smaller: "
                "net artifacts, lines, state locations, concepts. An explicit "
                '"nothing gets smaller" is a complete answer; omitting the section '
                "is not. (Hard-block per WI-6741; see "
                "bridge/gtkb-wi6741-simplification-accounting-section-002.md.)"
            )
        if (
            first_line in PENDING_PREFLIGHT_STATUSES
            and _bridge_kind_is_implementation_proposal(content)
            and _prior_deliberations_has_unedited_placeholder(content)
        ):
            return (
                "[Governance] Implementation proposals must replace the helper-inserted "
                "Prior Deliberations placeholder before bridge submission. The exact "
                f"unedited line `{NO_PRIOR_DELIBS_PLACEHOLDER}` is still present in "
                "## Prior Deliberations. Add relevant DELIB citations or replace it "
                "with a substantive no-prior-deliberations reason. "
                "(Hard-block per the Prior Deliberations section requirement in "
                ".agent/rules/counterpart-review-gate.md.)"
            )
        if first_line in PROJECT_METADATA_STATUSES and not _bridge_kind_is_metadata_exempt(content):
            metadata_gaps = _project_metadata_gaps(content)
            if metadata_gaps:
                return (
                    "[Governance] Implementation bridge proposals must include "
                    "project-linkage metadata lines: missing "
                    f"{', '.join(metadata_gaps)}. Add the absent line(s), or set "
                    f"{PROJECT_METADATA_FORMAT_HINT}"
                    "bridge_kind: spec_intake|governance_review|loyal_opposition_advisory "
                    "for a non-implementation proposal. "
                    "(Hard-block per DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001/"
                    "CLAUSE-PROJECT-METADATA-PRESENT.)"
                )
            membership_gap = _wi_project_membership_gap(content, cwd_path)
            if membership_gap:
                return _project_membership_refusal_message(content, cwd_path, membership_gap)
        if (
            first_line in PROJECT_METADATA_STATUSES
            and _bridge_kind_is_implementation_proposal(content)
            and _target_paths_from_content(content)
        ):
            req_suff_gap = _requirement_sufficiency_section_gap(content)
            if req_suff_gap:
                return (
                    "[Governance] Implementation proposals that request implementation work "
                    "must include a substantive ## Requirement Sufficiency subsection with "
                    "exactly one operative state ('Existing requirements sufficient' or "
                    "'New or revised requirement required before implementation'). "
                    f"Gap: {req_suff_gap}. "
                    "(Hard-block per .agent/rules/file-bridge-protocol.md "
                    "'Mandatory Implementation-Start Authorization Metadata'; WI-3439.)"
                )
            nonimpairment_gap = _nonimpairment_disposition_gap(content) if NONIMPAIRMENT_GOV_ID in content else None
            if nonimpairment_gap is not None:
                _record_gate_denial(
                    "modernization-nonimpairment-disposition-missing",
                    file_path,
                    nonimpairment_gap,
                    root=cwd_path,
                )
                return (
                    "[Governance] Cross-cutting implementation proposals must include one "
                    "structured ## Intuitiveness/Non-Impairment Disposition JSON object. "
                    f"Gap: {nonimpairment_gap}. "
                    "(Hard-block per GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001.)"
                )
        if (
            first_line in PROJECT_METADATA_STATUSES
            and _bridge_kind_is_implementation_proposal(content)
            and _target_paths_touch_harness_surface(content)
            and not _has_concrete_cross_harness_disposition_section(content)
        ):
            _record_gate_denial(
                "cross-harness-disposition-missing",
                file_path,
                "harness-surface target_paths without a Cross-Harness Disposition section",
                root=cwd_path,
            )
            return (
                "[Governance] Implementation proposals whose target_paths touch a harness-surface "
                "file (.claude/settings.json, .codex/hooks.json, .claude/hooks/**, "
                ".codex/gtkb-hooks/**, .claude/skills/**, .codex/skills/**) must include a "
                "non-empty ## Cross-Harness Disposition section declaring, per applicable harness, "
                "behavioral parity or an owner-approved typed waiver. "
                "(Hard-block per DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001 assertion "
                "PARITY-DISPOSITION-GATE; ADR-CROSS-HARNESS-PARITY-001 Q8.)"
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
                        f"preflight={error_msg}. Run "
                        f"python scripts/bridge_applicability_preflight.py --bridge-id {bridge_id} "
                        "for full output. (Hard-block per "
                        "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 "
                        "mechanical enforcement.)"
                    )
                clause_preflight_ok, clause_error_msg = _run_pending_clause_preflight(
                    cwd=cwd_path,
                    file_path=file_path,
                    bridge_id=bridge_id,
                    content=content,
                )
                if not clause_preflight_ok:
                    return (
                        "[Governance] ADR/DCL clause preflight failed for pending bridge write: "
                        f"file_path={file_path}. {clause_error_msg} Run "
                        f"python scripts/adr_dcl_clause_preflight.py --bridge-id {bridge_id} "
                        "for full output. (Hard-block per the mandatory ADR/DCL clause-test preflight gate.)"
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
            synthetic_session_context_id = _synthetic_session_context_id_for_content(content)
            if synthetic_session_context_id:
                return (
                    "[Governance] Bridge artifacts must include a real author_session_context_id, "
                    f"not an unresolvable placeholder {synthetic_session_context_id!r}. The authoring "
                    "session or dispatcher must provide the concrete session context id before the "
                    "bridge file reaches disk. (Hard-block per WI-4940 and WI-7298; "
                    "GOV-DOCUMENT-AUTHOR-PROVENANCE-001.)"
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


def _shell_candidates(payload: dict, root: Path) -> list[dict]:
    """Native-shaped payloads to judge for one incoming payload (WI-7289).

    A native payload expands to itself, so native handling is byte-for-byte the
    code that ran before. A shell payload expands to one synthetic Write per
    recognized write target; an unrecognized command expands to nothing and is
    therefore allowed.
    """
    hooks_dir = str(Path(__file__).resolve().parent)
    if hooks_dir not in sys.path:
        sys.path.insert(0, hooks_dir)
    try:
        from _shell_payload import expand_shell_payload
    except ImportError:
        return [payload]
    try:
        return expand_shell_payload(payload, root)
    except Exception:
        # Extraction must never harden into a new failure mode for the gate.
        return [payload]


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

    cwd = payload.get("cwd", ".")
    cwd_path = Path(cwd).resolve()

    # WI-7289: now that the baseline manifest declares shell_exec for this gate,
    # shell commands that write governed files reach it. Expand each recognized
    # shell write into a native-shaped payload and judge it with the identical
    # code below, so a shell denial reason matches its native counterpart by
    # construction rather than by a parallel implementation that can drift.
    for candidate in _shell_candidates(payload, cwd_path):
        tool_name = candidate.get("tool_name", "")
        tool_input = candidate.get("tool_input", {})

        if tool_name not in WRITE_TOOLS:
            continue

        file_path = tool_input.get("file_path", "")
        if not file_path:
            continue

        work_intent_reason = _bridge_work_intent_deny_reason(cwd_path=cwd_path, file_path=file_path, payload=candidate)
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

        ask_reason = None
        if not (_is_bridge_markdown_file(file_path) or _is_lo_verdict_bridge_file(file_path)):
            ask_reason = _pending_proposal_ask_reason(_canonical_project_root(cwd_path), file_path)
        if ask_reason:
            emit_ask("PreToolUse", ask_reason)
            sys.exit(0)

    emit_pass()
    sys.exit(0)


if __name__ == "__main__":
    main()
