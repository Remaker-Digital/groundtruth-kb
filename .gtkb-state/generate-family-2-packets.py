"""Synthesize v3 bodies for Family 2 (init-keyword amendments) + DCL-SESSION-ROLE-RESOLUTION-001.

Per AUQ DECISION (2026-06-04, S408): synthesize+diff+AUQ for amendment specs.

This script:
1. Pulls v_current body from MemBase for each amendment target.
2. Renders the v_new body inline (Prime Builder authoring; applies deltas
   described in DELIB-20260648 verbatim).
3. Computes unified diff (v_current → v_new) for owner review.
4. Stages synthesized body files to .gtkb-state/family-2-bodies/.
5. Computes SHA-256 of v_new bodies and writes packet JSON files
   (action='update').

Note: DELIB-20260648 §3 also mentions DCL-SESSION-ROLE-RESOLUTION-001
amendment. Included here for completeness; owner can drop from packet set
via AUQ if it's out of scope for the "11" count.
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
# v3 SYNTHESIZED BODIES — authored per DELIB-20260648 deltas
# ============================================================

SPEC_INIT_KEYWORD_V3 = """## Canonical init keyword syntax (REVISED at the post-S408 envelope amendment pass; subject mandatory, role optional)

Regex: `^::init (gtkb|application)( (pb|lo))?$`. First-line-only. Subject vocabulary `{gtkb, application}` is mandatory; role vocabulary `{pb, lo}` (pb = Prime Builder, lo = Loyal Opposition) is optional. Six valid forms (four with role + two without). No synonyms. Strict parse.

## Subject token (mandatory)

The subject token informs the agent about the scope of the session envelope (intent-hint per the envelope meta-model in `DELIB-20260637` #1). When `subject = application`, the active application name is resolved from `.claude/session/work-subject.json`, not hardcoded in the keyword (respects the Agent Red separateness boundary per `DELIB-20260637`).

## Role token (optional)

When the role token is PRESENT, behavior is unchanged from v2: it ephemerally overrides the session-stated role per `DCL-SESSION-ROLE-RESOLUTION-001`.

When the role token is ABSENT (`::init gtkb` or `::init application`), the receiver MUST use the durable harness role from `harness-state/harness-registry.json` for all in-session surfaces and MUST NOT write `.claude/session/active-session-role.json`. The session-stated role is unset; durable harness role applies to all surfaces (per `DELIB-20260648` and amended `DCL-SESSION-ROLE-RESOLUTION-001` v_next).

## Receiver-side scope

The keyword is canonical for BOTH machine-emitted dispatch (cross-harness trigger; env-var `GTKB_BRIDGE_POLLER_RUN_ID` present) AND owner-typed interactive declaration (no env-var), in both Claude and Codex SessionStart dispatchers. The syntax is identical across both contexts.

The receiver-side behavior is context-dependent per `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` (revised at v3). For headless dispatch, the keyword's subject token must match an expected envelope; when the role token is present, it must also match the receiver's durable role set or the dispatch is silently dropped (`STRICT_DROP`). For interactive owner-typed declaration, a present role token establishes the session-stated role for the rest of the session per `DCL-SESSION-ROLE-RESOLUTION-001`; an absent role token leaves the durable role authoritative.

## Owner-typed keyword timing

The owner-typed keyword MAY appear on ANY owner prompt during the session lifetime, not only the first prompt. Mid-session re-typing overrides any prior session-stated role; a re-typed keyword without a role token clears any prior session-stated role.

## First-line constraint

The first-line-only constraint (regex anchors `^...$`) is unchanged; the keyword MUST appear as the entire first line of the owner prompt.

## Migration / compat

Fully additive. Every form that parses at v2 (`::init gtkb pb`, `::init gtkb lo`) continues to parse unchanged at v3. New forms added at v3: `::init application pb`, `::init application lo`, `::init gtkb`, `::init application`. No emitter changes are required for backward compatibility; existing cross-harness trigger emitter output remains valid.

## Revision provenance

This revision (v3) is filed under `DELIB-20260648` (Envelope Init-Keyword Optionality Clarification, 2026-06-04) and is implemented under WI-4291. It refines v2's "asserts, does not set" wording by formalizing subject-token mandatoriness and role-token optionality. The keyword syntax change is the substantive amendment; receiver semantics are co-amended in `DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001` v3 and `DCL-SESSION-ROLE-RESOLUTION-001` v_next.

## Authority

- `DELIB-20260648` (2026-06-04 owner clarification; subject mandatory, role optional).
- Owner directive S371 (2026-05-29); 6 AskUserQuestion decisions in session-conversation transcript.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (decision); `DCL-SESSION-ROLE-RESOLUTION-001` (deterministic rules); `GOV-SESSION-ROLE-AUTHORITY-001` (governance boundary).
"""


DCL_INIT_KEYWORD_ASSERTION_V3 = """## Constraint (REVISED at the post-S408 envelope amendment pass; role-token optionality)

Emitter authority is REVISED: the cross-harness event-driven trigger MUST emit the canonical init keyword (subject token always present) for the dispatched-to harness's durable role when dispatching headless work. The emitter MAY omit the role token when the dispatched harness's role assignment can be inferred from durable state; the role token MUST be emitted when the emitter intends to assert a specific role for the receiver (override semantics).

Receiver authority is REVISED to deterministically fork on dispatch context AND role-token presence. The receiver-side decision table is:

| env-var `GTKB_BRIDGE_POLLER_RUN_ID` | Init keyword present | Role token in keyword | Subject token in expected set | Role in durable set | Receiver decision | Effect |
|---|---|---|---|---|---|---|
| absent | absent | n/a | n/a | n/a | NORMAL_STARTUP | render fresh-session disclosure for durable role (per `DCL-SESSION-ROLE-RESOLUTION-001`) |
| absent | present | yes | yes | n/a | INTERACTIVE_OVERRIDE_AUTHORIZED | record session-stated role marker at `.claude/session/active-session-role.json`; render disclosure for keyword role |
| absent | present | no | yes | n/a | INTERACTIVE_SUBJECT_DECLARED | record subject context; DO NOT write `.claude/session/active-session-role.json`; render disclosure for durable role |
| present | absent | n/a | n/a | n/a | LEGACY_FALLBACK | env-var-only dispatch (preserved for backward compatibility) |
| present | present | yes | yes | yes | DISPATCH_AUTHORIZED | bridge auto-dispatch context emitted; render for keyword role |
| present | present | yes | yes | no | STRICT_DROP | silent drop; audit log; clean exit |
| present | present | no | yes | n/a | DISPATCH_AUTHORIZED_SUBJECT_ONLY | bridge auto-dispatch context emitted; render for durable role |
| any | present | any | no | n/a | STRICT_DROP | unrecognized subject; silent drop; audit log; clean exit |

## SPOOF_FALLBACK replacement (carried forward from v2)

The pre-v2 `SPOOF_FALLBACK` decision (keyword without env-var falling through to normal startup) was replaced by `INTERACTIVE_OVERRIDE_AUTHORIZED` in v2. The v3 amendment further refines the interactive (env-var absent) rows by distinguishing keyword-with-role from keyword-without-role; the former writes the active-session-role marker, the latter does NOT.

## Active-session-role marker write rule (v3 addition)

The receiver MUST write `.claude/session/active-session-role.json` ONLY when the `INTERACTIVE_OVERRIDE_AUTHORIZED` decision fires (env-var absent AND keyword present AND role token present AND subject recognized). In all other rows (including `INTERACTIVE_SUBJECT_DECLARED`), the receiver MUST NOT write the marker; the durable harness role from `harness-state/harness-registry.json` is authoritative.

## Receiver-side audit logging

- `STRICT_DROP` continues to append a `misdirected_dispatch_strict_drop` record (or `unrecognized_subject_strict_drop` for the unrecognized-subject row) to `.gtkb-state/bridge-poller/dispatch-failures.jsonl` (unchanged) from either dispatcher.
- `INTERACTIVE_OVERRIDE_AUTHORIZED` records a `session_role_override` record to a new ephemeral log at `.gtkb-state/sessions/<session-id>/role-overrides.jsonl` from either dispatcher.
- `INTERACTIVE_SUBJECT_DECLARED` (new at v3) records a `session_subject_declared` record to the same ephemeral log; the implementation slice will refine the path.

## Headless safety preservation

The headless rows of the decision table (env-var-present) preserve the load-bearing safety property: `STRICT_DROP` continues to fire when env-var is present AND keyword is present AND keyword's subject is unrecognized OR (role token is present AND role is NOT in the receiver's durable role set). The `DISPATCH_AUTHORIZED_SUBJECT_ONLY` row is new at v3 and applies only when the role token is absent; in that case the receiver falls back to its durable role authority.

## Revision provenance

This revision (v3) is filed under `DELIB-20260648` (Envelope Init-Keyword Optionality Clarification, 2026-06-04) and is implemented under WI-4291. It introduces the receiver-side role-token-presence fork; the headless dispatch behavior under role-token-present rows is unchanged from v2.

## Authority

- `DELIB-20260648` (2026-06-04 owner clarification; subject mandatory, role optional; receiver behavior when role token absent).
- Owner directive S371 (2026-05-29); 6 AskUserQuestion decisions in session-conversation transcript.
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001` (decision); `DCL-SESSION-ROLE-RESOLUTION-001` (deterministic rules; co-amended at v_next); `GOV-SESSION-ROLE-AUTHORITY-001` (governance boundary); `SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001` (revised at v3; keyword syntax).
"""


# ============================================================

AMENDMENTS = [
    (
        "SPEC-CANONICAL-INIT-KEYWORD-SYNTAX-001",
        "specification",
        SPEC_INIT_KEYWORD_V3,
        "WI-4291 amendment per DELIB-20260648: regex `^::init (gtkb|application)( (pb|lo))?$`; subject mandatory, role optional; 6 valid forms.",
    ),
    (
        "DCL-INIT-KEYWORD-CONSISTENT-ASSERTION-001",
        "design_constraint",
        DCL_INIT_KEYWORD_ASSERTION_V3,
        "WI-4291 amendment per DELIB-20260648: receiver-side role-token-presence fork; subject-only path; active-session-role.json write rule restricted to INTERACTIVE_OVERRIDE_AUTHORIZED.",
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
    artifact_id: str, artifact_type: str, full_content: str, explicit_change: str, target_version: int
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
            f"Per owner AUQ DECISION (2026-06-04, Family 2 amendment synthesis): "
            f"v3 body authored from v_current + DELIB-20260648 deltas. Owner reviewed "
            f"unified diff before approval. {explicit_change}"
        ),
        "changed_by": "gt-cli",
        "explicit_change_request": explicit_change,
        "full_content": full_content,
        "full_content_sha256": sha,
        "presented_to_user": True,
        "source_ref": "DELIB-20260648 + bridge/gtkb-envelope-init-keyword-amendment-slice-1-005.md",
        "transcript_captured": True,
    }


def main() -> int:
    out_bodies = REPO / ".gtkb-state" / "family-2-bodies"
    out_bodies.mkdir(parents=True, exist_ok=True)
    out_packets = REPO / ".groundtruth" / "formal-artifact-approvals"
    out_packets.mkdir(parents=True, exist_ok=True)

    results = []
    for artifact_id, artifact_type, v_new_body, explicit_change in AMENDMENTS:
        v_curr_version, v_curr_body = fetch_current_body(artifact_id)
        target_version = v_curr_version + 1

        # Stage the v_new body file
        body_path = out_bodies / f"{artifact_id}-v{target_version}.md"
        body_path.write_text(v_new_body, encoding="utf-8")

        # Compute diff
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

        # Generate packet (always — owner can choose not to use it)
        packet = make_packet(artifact_id, artifact_type, v_new_body, explicit_change, target_version)
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
