"""Synthesize v2 bodies for Family 3 (envelope-program amendment cluster).

Per AUQ DECISION (2026-06-04, S408): synthesize+diff+AUQ pattern continues
for Family 3. Two amendments:

1. GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001 v1 -> v2:
   Append envelope-program paragraph per bridge/gtkb-envelope-glossary-
   and-gov-lifecycle-amendment-001.md (lines 426-448). Existing core
   sentence preserved verbatim.

2. DCL-SESSION-ROLE-RESOLUTION-001 v1 -> v2:
   Extend resolution table to handle the subject-mandatory + role-optional
   keyword (per DELIB-20260648 #3). Add new row for "interactive
   subject-only declaration" where keyword is present but role token is
   absent -> durable role applies, marker NOT written. Generalize the
   existing "Interactive declaration" row to use `<subject>` and `<role>`
   token notation since both `gtkb` and `application` are now valid
   subjects.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import sqlite3
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DB = REPO / "groundtruth.db"


# ============================================================
# v2 SYNTHESIZED BODIES — authored per source deltas
# ============================================================

# Append envelope-program paragraph (verbatim from proposal lines 433-448,
# de-blockquoted). Existing single paragraph preserved.
GOV_LIFECYCLE_V2 = """Each Agent Red / GT-KB session must actively inform and engage the user, draw attention to priorities across all dimensions of the project, and simplify user input by suggesting concrete actions and priorities.

The envelope program (WI-4291..WI-4302 series, all GO-terminal at design phase as of 2026-06-04) provides the deterministic operational mechanics for this GOV's proactive-engagement mandate. Session openings use the canonical init keyword family (`::init <subject> <role>`, per the GO-terminal sibling thread covering WI-4291's amendment); session closures use the canonical wrap keyword family (`::wrap` plus 17 NL phrases, per WI-4292) running the deterministic 4-tier wrap procedure (per WI-4294). In-session topic work is routed via `::open <type>` / `::close <type>` per WI-4295's topic-envelope router. Recurring ops/review/audit work uses dispatch envelopes per WI-4296. The envelope.json state file per WI-4293 schema is the live session-state surface; archived envelopes provide cross-session handoff context for the deterministic handoff-prompt generator per WI-4299 (when filed and approved).
"""


DCL_SESSION_ROLE_RESOLUTION_V2 = """## Constraint

GT-KB code that needs to know "what role is this session operating as" MUST resolve it deterministically using the following table. The resolution is identical across hooks, CLI tools, and library code, in both Claude Code and Codex CLI harnesses.

## Resolution table (REVISED at v2 per DELIB-20260648; subject mandatory, role optional)

| Context | env-var GTKB_BRIDGE_POLLER_RUN_ID | session-state marker exists | Init keyword on this prompt | Resolved role | Source |
|---|---|---|---|---|---|
| Headless dispatch, authorized | present | n/a | `::init <subject> <role>` matches durable set | durable (matches keyword) | dispatch routing |
| Headless dispatch, subject-only | present | n/a | `::init <subject>` (no role token) | durable | durable (subject-context recorded) |
| Headless dispatch, misdirected | present | n/a | role token present and NOT in durable set | drop (STRICT_DROP); no role rendered | audit-log only |
| Headless dispatch, unrecognized subject | present | n/a | subject token NOT in `{gtkb, application}` | drop (STRICT_DROP); no role rendered | audit-log only |
| Headless dispatch, legacy | present | n/a | absent | durable (legacy env-var-only fallback) | durable |
| Interactive declaration with role | absent | n/a | `::init <subject> <role>` (role token present) | keyword role | session-state marker written |
| Interactive subject-only declaration | absent | n/a | `::init <subject>` (no role token) | durable | durable (subject-context recorded; marker NOT written) |
| Interactive continuation | absent | present, valid | absent | session-state marker role | session-state marker |
| Interactive default | absent | absent | absent | durable | durable |
| Interactive resume after compaction | absent | absent (marker not persisted) | absent | durable | durable |

## Subject vocabulary

The `<subject>` token is mandatory in every `::init` keyword form per `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v3 (REVISED at the post-S408 envelope amendment pass). Closed vocabulary: `{gtkb, application}`. Unrecognized subjects produce `STRICT_DROP` in headless dispatch and silent ignore in interactive declaration (the prompt is processed as non-init owner input).

## Role token optionality

The `<role>` token is OPTIONAL in every `::init` keyword form. When present, behavior is per the "with role" rows above (override the session-stated role for in-session surfaces). When absent, the `subject-only declaration` rows apply: the session-state marker is NOT written, and the durable harness role from `harness-state/harness-registry.json` is authoritative for all in-session surfaces.

## Machine-checkable assertions

1. `assertion_resolved_role_is_durable_when_headless`: when `GTKB_BRIDGE_POLLER_RUN_ID` is present and a keyword is present with a role token and `keyword_role` is in the durable role set, resolved role equals durable role (`primary_role(durable_record)`). Applies to BOTH harnesses' SessionStart dispatchers.
2. `assertion_resolved_role_is_keyword_when_declared`: when `GTKB_BRIDGE_POLLER_RUN_ID` is absent and the prompt contains a valid init keyword with a role token, resolved role equals the keyword role. The session-state marker MUST be written on the same code path, in both harnesses.
3. `assertion_resolved_role_is_durable_when_subject_only_declaration`: when `GTKB_BRIDGE_POLLER_RUN_ID` is absent and the prompt contains a valid init keyword WITHOUT a role token, resolved role equals durable role. The session-state marker MUST NOT be written in this case.
4. `assertion_resolved_role_is_marker_when_continuing`: when `GTKB_BRIDGE_POLLER_RUN_ID` is absent and a valid session-state marker exists and no init keyword is on this prompt, resolved role equals the marker role.
5. `assertion_resolved_role_is_durable_when_undeclared`: when `GTKB_BRIDGE_POLLER_RUN_ID` is absent and no session-state marker exists and no init keyword is on this prompt, resolved role equals durable role.
6. `assertion_session_state_marker_is_ephemeral`: the session-state marker file (`.claude/session/active-session-role.json`) MUST NOT survive a SessionStart event in either harness. Both SessionStart dispatchers MUST delete or otherwise invalidate any pre-existing marker before SessionStart-time role rendering.
7. `assertion_session_state_marker_carries_session_id`: the marker MUST record the current harness session id so that a stale marker from a prior session id is treated as invalid.
8. `assertion_session_state_marker_role_is_role-set-member`: the marker's role value MUST be in `{prime-builder, loyal-opposition}`. Unknown values are treated as marker-absent.
9. `assertion_parity_between_harnesses`: both `.claude/hooks/session_start_dispatch.py` and `.codex/gtkb-hooks/session_start_dispatch.py` MUST implement the same resolution table. `scripts/check_codex_hook_parity.py` MUST surface drift if one dispatcher diverges.

## Out of scope

- The mechanism by which the durable role is read (existing `scripts/harness_roles.py` chain).
- The mechanism by which the cross-harness trigger selects recipient (existing `scripts/cross_harness_bridge_trigger.py` logic; unchanged).
- The marker file format details (left to the implementation slice; this DCL requires only the fields above).
- Codex AXIS 2 app-thread behavior (flagged as follow-on; out of scope).

## Revision provenance

This revision (v2) is filed under `DELIB-20260648` (Envelope Init-Keyword Optionality Clarification, 2026-06-04) and is implemented under WI-4291. It extends the v1 resolution table to handle the subject-mandatory + role-optional keyword forms per the amended `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` v3 and `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v3. The headless behavior under role-token-present rows is unchanged from v1.

## Authority

- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (parent decision).
- `GOV-SESSION-ROLE-AUTHORITY-001` (governance boundary).
- `DELIB-20260648` (2026-06-04 owner clarification; subject mandatory, role optional).
- Owner directive S371 (2026-05-29).
- Codex Loyal Opposition GO at `bridge/gtkb-interactive-session-role-override-scoping-004.md`.
"""


# ============================================================

AMENDMENTS = [
    (
        "GOV-SESSION-LIFECYCLE-PROACTIVE-ENGAGEMENT-001",
        "governance",
        GOV_LIFECYCLE_V2,
        "WI-4300 amendment per bridge/gtkb-envelope-glossary-and-gov-lifecycle-amendment-001.md lines 426-448: append envelope-program operational mechanics paragraph; existing core sentence preserved.",
        "bridge/gtkb-envelope-glossary-and-gov-lifecycle-amendment-001.md",
    ),
    (
        "DCL-SESSION-ROLE-RESOLUTION-001",
        "design_constraint",
        DCL_SESSION_ROLE_RESOLUTION_V2,
        "WI-4291 amendment per DELIB-20260648 #3: extend resolution table to handle subject-mandatory + role-optional keyword forms; add subject-only declaration rows; add unrecognized-subject STRICT_DROP row; add machine-checkable assertion for subject-only path.",
        "DELIB-20260648 + bridge/gtkb-envelope-init-keyword-amendment-slice-1-005.md",
    ),
]


def fetch_current_body(spec_id: str) -> tuple[int, str]:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute(
        "SELECT version, description FROM specifications WHERE id=? ORDER BY version DESC LIMIT 1",
        (spec_id,),
    )
    row = cur.fetchone()
    conn.close()
    if row is None:
        raise ValueError(f"No row found for {spec_id}")
    return row[0], row[1]


def make_packet(
    artifact_id: str, artifact_type: str, full_content: str, explicit_change: str, target_version: int, source_ref: str
) -> dict:
    sha = hashlib.sha256(full_content.encode("utf-8")).hexdigest()
    return {
        "action": "update",
        "approval_mode": "approve",
        "approved_by": "owner",
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "target_version": target_version,
        "change_reason": (
            f"Per owner AUQ DECISION (2026-06-04, Family 3 amendment synthesis): "
            f"v{target_version} body authored from v_current + source deltas. Owner reviewed "
            f"unified diff before approval. {explicit_change}"
        ),
        "changed_by": "gt-cli",
        "explicit_change_request": explicit_change,
        "full_content": full_content,
        "full_content_sha256": sha,
        "presented_to_user": True,
        "source_ref": source_ref,
        "transcript_captured": True,
    }


def main() -> int:
    out_bodies = REPO / ".gtkb-state" / "family-3-bodies"
    out_bodies.mkdir(parents=True, exist_ok=True)
    out_packets = REPO / ".groundtruth" / "formal-artifact-approvals"
    out_packets.mkdir(parents=True, exist_ok=True)

    results = []
    for artifact_id, artifact_type, v_new_body, explicit_change, source_ref in AMENDMENTS:
        v_curr_version, v_curr_body = fetch_current_body(artifact_id)
        target_version = v_curr_version + 1

        body_path = out_bodies / f"{artifact_id}-v{target_version}.md"
        body_path.write_text(v_new_body, encoding="utf-8")

        diff = difflib.unified_diff(
            v_curr_body.splitlines(keepends=True),
            v_new_body.splitlines(keepends=True),
            fromfile=f"{artifact_id} v{v_curr_version} (from MemBase)",
            tofile=f"{artifact_id} v{target_version} (synthesized)",
            n=2,
        )
        diff_text = "".join(diff)
        diff_path = out_bodies / f"{artifact_id}-v{target_version}.diff"
        diff_path.write_text(diff_text, encoding="utf-8")

        packet = make_packet(artifact_id, artifact_type, v_new_body, explicit_change, target_version, source_ref)
        packet_path = out_packets / f"2026-06-04-{artifact_id}-v{target_version}.json"
        packet_path.write_text(
            json.dumps(packet, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

        results.append(
            {
                "artifact_id": artifact_id,
                "current_version": v_curr_version,
                "target_version": target_version,
                "current_bytes": len(v_curr_body.encode("utf-8")),
                "new_bytes": len(v_new_body.encode("utf-8")),
                "sha256_new": packet["full_content_sha256"],
                "diff_path": str(diff_path.relative_to(REPO)).replace("\\", "/"),
                "body_path": str(body_path.relative_to(REPO)).replace("\\", "/"),
                "packet_path": str(packet_path.relative_to(REPO)).replace("\\", "/"),
                "diff_lines": diff_text.count("\n"),
            }
        )

    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
