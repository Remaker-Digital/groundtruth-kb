"""Claude Design GUI-Refresh Intake — KB artifact insertion (Slices A/B/C).

Implements D1–D6 from the GO'd bridge
``bridge/agent-red-claude-design-gui-refresh-intake-implementation-002.md``.

D7 (DA registration procedure) is recorded here too as a KB op-procedure.
The procedure's companion script is ``scripts/archive_claude_design_handoff.py``.

Idempotent by design: re-running skips any artifact already present in the KB
(by id). No KB mutations happen without an existing Codex GO on this bridge.

Scope guardrails (per Codex review binding conditions in bridge -002):
  - No writes to ``widget/**``, ``src/**``, GT-KB, or ``.github/workflows/**``.
  - D5 (``GOV-CD-PRESERVATION``) ships with six machine-checkable assertions.
  - D5 I1 evidence cites ``tests/widget/test_widget_consent_ordering.py``, which
    this bridge also creates.
  - The 2026-04-18 seed DA row is NOT inserted here — it is produced by
    ``scripts/archive_claude_design_handoff.py`` after this script has run,
    before the post-implementation report.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "knowledge-db"))

from db import KnowledgeDB  # noqa: E402

BRIDGE_GO = "bridge/agent-red-claude-design-gui-refresh-intake-implementation-002.md"
CHANGED_BY = f"Prime Builder (Opus 4.7) — {BRIDGE_GO} GO"
CHANGE_REASON = (
    "Claude Design GUI-Refresh Intake implementation bridge — "
    "D1–D7 KB artifacts per GO'd bridge -002 binding conditions."
)


# ---------------------------------------------------------------------------
# D1 — Handoff Packet Format Spec (type=protocol)
# ---------------------------------------------------------------------------

D1_ID = "SPEC-CD-HANDOFF-FORMAT-001"
D1_TITLE = "Claude Design Handoff Packet Format"
D1_DESCRIPTION = """\
Defines the mandatory and optional contents of a Claude Design
(``claude.ai/design``) handoff bound for Agent Red.

Mandatory contents
------------------
* ``{root}/README.md`` — Claude Design's receiving-agent instructions.
* ``{root}/project/`` subdirectory containing at minimum:
  - An HTML entry (``index.html`` or equivalent) that bootstraps the prototype.
  - A CSS file with a ``:root`` design-token block (accent, surface, bubble,
    density, size families).
  - At least one JSX or component file representing the prototype.

Optional contents
-----------------
* ``{root}/project/uploads/`` — reference screenshots pasted by the owner.
* Edit-mode markers (``EDITMODE-BEGIN`` / ``EDITMODE-END``) in the HTML entry
  plus a ``postMessage`` listener in the root component that implements the
  bidirectional ``__activate_edit_mode`` / ``__edit_mode_set_keys`` protocol.

Claude Design observables captured from the 2026-04-18 worked example
---------------------------------------------------------------------
1. React 18 UMD runtime + Babel standalone (design medium is prototype JSX,
   not production code).
2. Design-token system in ``:root`` (accent family, surface dark+light, bubble
   shape map, density map, size map, shadow + radius).
3. ``data-*`` attribute-driven theming on the widget root.
4. ``postMessage`` edit-mode protocol between the prototype and a parent frame.
5. Inline demo-brand placeholder copy (e.g., ``Ember Studio``) that is NOT to
   be treated as production content.

Contract boundary
-----------------
Per the handoff README, the authoritative artifacts are (a) CSS tokens,
(b) visual output, and (c) UX flow — NOT the JSX source structure. Receiving
agents recreate visual output in the target stack; they do not port prototype
structure unless it happens to fit.

Assertion
---------
An incoming artifact claiming to be a Claude Design handoff MUST contain at
minimum ``README.md`` + ``project/index.html``. This is the structural
assertion enforced by D2's triage procedure.

See also
--------
* D2 (``intake-triage-claude-design``) — classifies incoming handoffs.
* D3 (``token-extraction-claude-design``) — extracts the ``:root`` token system.
* D5 (``GOV-CD-PRESERVATION``) — invariants that survive any refresh.
"""


# ---------------------------------------------------------------------------
# D2–D4, D6, D7 — Operational procedures
# ---------------------------------------------------------------------------

D2_ID = "intake-triage-claude-design"
D2_TITLE = "Claude Design Handoff Intake Triage"
D2_STEPS = [
    {
        "step": 1,
        "action": (
            "Receive handoff artifact (typically a zip). Verify it conforms to "
            "SPEC-CD-HANDOFF-FORMAT-001 (README.md + project/index.html present)."
        ),
        "verify": "Handoff opens cleanly; mandatory files enumerated.",
    },
    {
        "step": 2,
        "action": (
            "Classify the handoff into exactly one of four triage outcomes:\n"
            "  (a) Token-only adoption — CSS tokens map cleanly; no new UX behavior.\n"
            "  (b) Per-feature visual refresh — existing component(s) receive "
            "visual updates.\n"
            "  (c) Net-new feature proposal — handoff introduces UX behaviors "
            "not in the current widget.\n"
            "  (d) Full redesign (rare) — multi-phase workstream with explicit "
            "phase gates."
        ),
        "verify": "Outcome recorded in the intake bridge with evidence.",
    },
    {
        "step": 3,
        "action": (
            "Route each classified item to its appropriate bridge template:\n"
            "  (a) → ``agent-red-widget-design-token-adoption-NNN`` (narrow scope, "
            "     CSS custom-property updates only, no component restructuring).\n"
            "  (b) → per-component visual-refresh bridges, one per affected component.\n"
            "  (c) → GOV-01 spec-first + GOV-09 input-classification pipeline: "
            "     one spec + WI + test per net-new feature.\n"
            "  (d) → multi-phase workstream bridge with per-phase GO gates."
        ),
        "verify": "Target bridge identifier(s) recorded in triage output.",
    },
    {
        "step": 4,
        "action": (
            "Cite D5 (GOV-CD-PRESERVATION) invariants I1–I6 and show which "
            "invariants apply to each routed item. Any apparent violation is "
            "raised as a separate owner-decision item before routing."
        ),
        "verify": "Invariant applicability recorded; no silent violations.",
    },
    {
        "step": 5,
        "action": (
            "Emit a triage output row for the Deliberation Archive via D7 "
            "(``archive-claude-design-handoff``). The handoff becomes a durable, "
            "searchable decision record regardless of outcome."
        ),
        "verify": "DA row visible via ``search_deliberations('Claude Design')``.",
    },
    {
        "step": 6,
        "action": (
            "Worked example — 2026-04-18 ``AR-Widget-handoff.zip``: classified as "
            "BOTH (a) token-only candidate (design tokens cleanly adoptable via "
            "D3 runbook) AND (c) net-new feature proposals (teaser, history, "
            "menu, rich card, reactions, rating, handoff-to-human, tweaks panel "
            "each require their own spec + WI + test)."
        ),
        "verify": (
            "Worked-example row archived in DA via D7 as the seed record for "
            "this bridge."
        ),
    },
]


D3_ID = "token-extraction-claude-design"
D3_TITLE = "Claude Design Token Extraction Runbook"
D3_STEPS = [
    {
        "step": 1,
        "action": (
            "Open the handoff ``project/styles.css`` and locate the ``:root`` "
            "block. Extract the token families (accent / surface / bubble / "
            "density / size / shadow / radius). Record each token's name + "
            "value + attribute-selector variants."
        ),
        "verify": "Token catalog captured in the adoption bridge.",
    },
    {
        "step": 2,
        "action": (
            "Owner decision: map tokens automatically (adopt handoff names 1:1) "
            "vs. curated (rename via Agent Red's theme vocabulary). Default: "
            "curated. Produce a rename map explicit in the bridge."
        ),
        "verify": "Rename map recorded; owner decision recorded in DA.",
    },
    {
        "step": 3,
        "action": (
            "Apply tokens via ``data-*`` attributes on the widget root. Do NOT "
            "modify component source; adopted tokens live in the theme layer."
        ),
        "verify": (
            "Chromatic baseline captured; no DOM structure changes in the diff."
        ),
    },
    {
        "step": 4,
        "action": (
            "Run the Chromatic baseline diff. Existing flows MUST show zero "
            "visual regressions (token adoption is additive; behavior unchanged)."
        ),
        "verify": (
            "Chromatic diff review gate per D6 passes; no unreviewed visual deltas."
        ),
    },
    {
        "step": 5,
        "action": (
            "Guard: this runbook produces a proposal, NOT a PR. Every token "
            "adoption still passes through a bridge before merge. No "
            "``widget/src/**`` writes occur from this runbook alone."
        ),
        "verify": (
            "Bridge entry exists for the token adoption; Codex review complete."
        ),
    },
]


D4_ID = "feature-to-spec-claude-design"
D4_TITLE = "Claude Design Feature-to-Spec Pipeline"
D4_STEPS = [
    {
        "step": 1,
        "action": (
            "For each net-new feature identified by D2 triage outcome (c): "
            "trigger GOV-09 input classification. Owner confirms the feature "
            "is in scope for the product."
        ),
        "verify": "Owner decision recorded in DA via D7.",
    },
    {
        "step": 2,
        "action": (
            "Prime creates a specification per GOV-01 and a work item per "
            "GOV-12. The spec references the handoff as ``source_paths`` and "
            "cites D1's handoff-format assertion."
        ),
        "verify": "Spec + WI rows visible via ``list_specs`` / ``list_work_items``.",
    },
    {
        "step": 3,
        "action": (
            "Prime authors a test per GOV-03 before implementation begins. "
            "The test must produce an unambiguous PASS/FAIL."
        ),
        "verify": "Test row visible via ``get_tests_for_spec``; PASS/FAIL clarity confirmed.",
    },
    {
        "step": 4,
        "action": (
            "WI enters the backlog. Backlog prioritization determines "
            "implementation order."
        ),
        "verify": "Backlog snapshot includes the WI.",
    },
    {
        "step": 5,
        "action": (
            "Implementation happens only through a bridge with explicit Codex "
            "GO, per ``.claude/rules/codex-review-gate.md``. No Claude-Design-"
            "derived code lands without D5 invariant coverage demonstrated."
        ),
        "verify": "Bridge VERIFIED; D5 assertion run passes after implementation.",
    },
    {
        "step": 6,
        "action": (
            "Worked example — 2026-04-18 candidates: teaser, conversation "
            "history, header menu, rich card, handoff-to-human, per-message "
            "reactions, end-chat rating, tweak-controls panel. Each is a "
            "pre-filled input-classification row; actual spec creation waits "
            "for explicit owner approval per feature."
        ),
        "verify": "Candidates cited in the DA seed row for 2026-04-18.",
    },
]


D6_ID = "review-gate-claude-design"
D6_TITLE = "Claude Design Refresh Review Gate"
D6_STEPS = [
    {
        "step": 1,
        "action": (
            "Loyal Opposition review checks (per ``.claude/rules/file-bridge-"
            "protocol.md``): (a) handoff-packet-format compliance vs D1; "
            "(b) intake-triage classification vs D2; (c) D5 invariant coverage; "
            "(d) required-evidence completeness per "
            "``.claude/rules/report-depth-prime-builder-context.md``."
        ),
        "verify": "Bridge review file saved; verdict GO or NO-GO; findings addressed.",
    },
    {
        "step": 2,
        "action": (
            "Pre-merge visual artifact — recommended combination:\n"
            "  D6-a: Storybook static build attached to the Claude-Design-"
            "        derived PR (separate future CI bridge authorizes the "
            "        workflow step).\n"
            "  D6-b: Local before/after screenshots captured by the bridge "
            "        author and inlined into the bridge document.\n"
            "Minimum for every Claude-Design-derived PR: at least D6-b."
        ),
        "verify": "Bridge document contains inline before/after evidence.",
    },
    {
        "step": 3,
        "action": (
            "Note: the current ``.github/workflows/chromatic.yml`` is push-only "
            "on ``develop`` — it captures post-merge baselines, not pre-merge "
            "diffs. Upgrading Chromatic to PR-build (option D6-c) is deferred "
            "to a future bridge ``agent-red-chromatic-pr-gate-NNN``. This "
            "bridge does NOT modify ``.github/workflows/**``."
        ),
        "verify": (
            "Git diff stat shows zero ``.github/workflows/**`` writes in this "
            "bridge's commit."
        ),
    },
    {
        "step": 4,
        "action": (
            "Owner visual review — explicit owner sign-off gate before merge. "
            "Default cadence: per-feature-batch, with Chromatic + axe-core on "
            "every PR as the always-on regression gate."
        ),
        "verify": "Owner decision row exists in DA for each batch.",
    },
    {
        "step": 5,
        "action": (
            "Protected-behavior gate: after implementation, rerun the KB "
            "assertion runner (``python tools/knowledge-db/assertions.py``). "
            "All six D5 invariants (I1–I6) MUST continue to pass. Any "
            "regression blocks merge."
        ),
        "verify": (
            "Assertion summary shows ``GOV-CD-PRESERVATION`` PASS; no regressions."
        ),
    },
]


D7_ID = "archive-claude-design-handoff"
D7_TITLE = "Claude Design Handoff DA Registration Procedure"
D7_STEPS = [
    {
        "step": 1,
        "action": (
            "Invoke ``python scripts/archive_claude_design_handoff.py --apply "
            "--handoff-path <path-to-zip-or-dir> --owner-decision <outcome> "
            "--session-id <session> --date <YYYY-MM-DD>``. The script inspects "
            "the handoff (file list, not bytes), runs the KB redaction pipeline, "
            "and emits one DA row per logical decision (handoff inspection + any "
            "mid-handoff owner decisions)."
        ),
        "verify": (
            "Script exit code 0; DA row ids printed; ``search_deliberations`` "
            "returns the new row(s)."
        ),
    },
    {
        "step": 2,
        "action": (
            "The script writes ``source_type='report'`` for Prime's inspection "
            "record — the KB enforces a closed source_type set (bridge_thread, "
            "lo_review, owner_conversation, proposal, report, session_harvest), "
            "so Prime inspection records are classified as ``report``. Mid-"
            "handoff owner decisions use ``source_type='owner_conversation'`` "
            "via subsequent invocations. Each row carries "
            "``changed_by='archive_claude_design_handoff.py'`` and a "
            "``change_reason`` naming the D7 procedure id."
        ),
        "verify": (
            "Row fields visible via ``KnowledgeDB.get_deliberation`` match the "
            "schema."
        ),
    },
    {
        "step": 3,
        "action": (
            "Content-hash idempotence: same handoff + same inspection produces "
            "the same content_hash; re-runs skip with no new row. The check "
            "queries ``current_deliberations`` for ``(source_ref, "
            "content_hash)`` before insert — same pattern as "
            "``scripts/harvest_session_deliberations.py``."
        ),
        "verify": "Second run of the same handoff prints ``skipped``.",
    },
    {
        "step": 4,
        "action": (
            "Redaction: the script calls ``KnowledgeDB.redact_content`` on the "
            "inspection content (same pipeline the harvest script uses). "
            "Binary artifact bytes are never inlined — only a file list + "
            "metadata + inspection observations. The handoff zip itself stays "
            "on OneDrive as the authoritative source."
        ),
        "verify": (
            "Inspection content contains no raw credential patterns; only "
            "metadata + observations."
        ),
    },
    {
        "step": 5,
        "action": (
            "Archival of the 2026-04-18 seed handoff is the last implementation "
            "slice of the bridge that introduces this procedure (Slice E in "
            "bridge -002). It happens AFTER the D7 procedure + script exist and "
            "BEFORE the post-implementation verification report. It is NOT "
            "deferred until after Codex VERIFIED."
        ),
        "verify": (
            "Post-implementation report cites the DA row id for the 2026-04-18 "
            "seed; order of events is observable in git history."
        ),
    },
]


# ---------------------------------------------------------------------------
# D5 — GOV-CD-PRESERVATION (protected_behavior) with 6 DCL assertions
# ---------------------------------------------------------------------------

D5_ID = "GOV-CD-PRESERVATION"
D5_TITLE = "Claude Design Refresh Preservation Contract"
D5_DESCRIPTION = """\
Machine-checkable invariants that MUST survive any Claude-Design-driven
refresh of the Agent Red widget. This is a NEW topic-specific governance
artifact (per Codex review F2 preference), cross-linked to — not modifying —
GOV-01 (CLAUDE.md line budget), GOV-09 (owner input classification), and
GOV-12 (WI triggers tests).

Future per-feature Claude Design refresh bridges MUST cite this artifact and
demonstrate how the refresh satisfies each invariant, or propose an explicit
owner-ratified exception. The assertion runner (``tools/knowledge-db/
assertions.py``) checks these at session start and on the pre-build gate.

Invariants (I1–I6)
------------------
* **I1** ConsentBanner renders before any chat message post-init. Tenant-
  configurable via ``consent_collection_enabled``; the ordering is structural
  in ``widget/src/components/Panel.tsx`` (ConsentBanner block precedes
  MessageList). Evidence: ``tests/widget/test_widget_consent_ordering.py``.
* **I2** OTP-gated flows require both email and phone verification where
  specified. Evidence: ``tests/unit/test_widget_otp_verification.py``,
  ``tests/chat/test_identity_preprocessor.py``.
* **I3** axe-core CI gate passes at WCAG 2.1 AA. Evidence: the workflow
  ``.github/workflows/accessibility.yml`` exists and is referenced by D6.
* **I4** Tenant isolation preserved. Evidence:
  ``tests/flows/test_flow_auth_boundaries.py``.
* **I5** Pact contracts unchanged unless explicitly re-generated. Evidence:
  ``widget/package.json`` depends on ``@pact-foundation/pact``.
* **I6** Widget builds clean under strict TypeScript. Evidence:
  ``widget/tsconfig.json`` declares ``strict`` mode; ``widget/package.json``
  exposes ``tsc --noEmit`` via the ``typecheck`` script.

Scope boundary
--------------
This spec is the authority for Claude-Design-driven refresh invariants only.
It does NOT redefine ordering for other UI workstreams, and it does NOT
authorize any widget/source change on its own — changes still require a
per-feature bridge with explicit Codex GO.
"""

D5_ASSERTIONS = [
    {
        "type": "grep",
        "file": "widget/src/components/Panel.tsx",
        "pattern": "ConsentBanner",
        "min_count": 1,
        "description": (
            "I1: ConsentBanner is rendered by Panel.tsx (ordering enforced by "
            "tests/widget/test_widget_consent_ordering.py)."
        ),
    },
    {
        "type": "file_exists",
        "file": "tests/unit/test_widget_otp_verification.py",
        "description": (
            "I2: OTP verification regression suite exists (email + phone gates)."
        ),
    },
    {
        "type": "file_exists",
        "file": ".github/workflows/accessibility.yml",
        "description": "I3: axe-core WCAG 2.1 AA CI workflow exists.",
    },
    {
        "type": "file_exists",
        "file": "tests/flows/test_flow_auth_boundaries.py",
        "description": "I4: tenant-isolation auth boundary tests exist.",
    },
    {
        "type": "grep",
        "file": "widget/package.json",
        "pattern": "@pact-foundation/pact",
        "min_count": 1,
        "description": "I5: Pact contract tooling remains a declared dependency.",
    },
    {
        "type": "grep",
        "file": "widget/tsconfig.json",
        "pattern": '"strict": true',
        "min_count": 1,
        "description": "I6: widget TypeScript config retains strict mode.",
    },
]


# ---------------------------------------------------------------------------
# Insertion orchestration
# ---------------------------------------------------------------------------


def _insert_spec_if_absent(db: KnowledgeDB, *, id: str, title: str,
                           description: str, type: str, status: str,
                           assertions: list[dict] | None = None,
                           tags: list[str] | None = None) -> str:
    """Insert a spec if it doesn't already exist. Returns action verb."""
    if db.get_spec(id) is not None:
        return "skipped"
    db.insert_spec(
        id=id,
        title=title,
        status=status,
        changed_by=CHANGED_BY,
        change_reason=CHANGE_REASON,
        description=description,
        type=type,
        assertions=assertions,
        tags=tags,
    )
    return "created"


def _insert_procedure_if_absent(db: KnowledgeDB, *, id: str, title: str,
                                steps: list[dict],
                                type: str = "operational") -> str:
    if db.get_op_procedure(id) is not None:
        return "skipped"
    db.insert_op_procedure(
        id=id,
        title=title,
        changed_by=CHANGED_BY,
        change_reason=CHANGE_REASON,
        type=type,
        steps=steps,
    )
    return "created"


def main() -> int:
    db = KnowledgeDB()
    actions: list[tuple[str, str, str]] = []

    # D1 — specification (protocol)
    actions.append((
        D1_ID, "specification (protocol)",
        _insert_spec_if_absent(
            db,
            id=D1_ID, title=D1_TITLE, description=D1_DESCRIPTION,
            type="protocol", status="implemented",
            tags=["claude-design", "handoff-format", "bridge-intake"],
        ),
    ))

    # D2–D4 — procedures
    for pid, ptitle, psteps in [
        (D2_ID, D2_TITLE, D2_STEPS),
        (D3_ID, D3_TITLE, D3_STEPS),
        (D4_ID, D4_TITLE, D4_STEPS),
    ]:
        actions.append((
            pid, "procedure",
            _insert_procedure_if_absent(
                db, id=pid, title=ptitle, steps=psteps,
            ),
        ))

    # D5 — governance (protected_behavior) with 6 assertions
    actions.append((
        D5_ID, "governance (protected_behavior)",
        _insert_spec_if_absent(
            db,
            id=D5_ID, title=D5_TITLE, description=D5_DESCRIPTION,
            type="protected_behavior", status="implemented",
            assertions=D5_ASSERTIONS,
            tags=["claude-design", "preservation-contract", "gov-preservation"],
        ),
    ))

    # D6 — procedure
    actions.append((
        D6_ID, "procedure",
        _insert_procedure_if_absent(
            db, id=D6_ID, title=D6_TITLE, steps=D6_STEPS,
        ),
    ))

    # D7 — procedure (the companion script lives in scripts/archive_claude_design_handoff.py)
    actions.append((
        D7_ID, "procedure",
        _insert_procedure_if_absent(
            db, id=D7_ID, title=D7_TITLE, steps=D7_STEPS,
        ),
    ))

    print("Claude Design GUI-Refresh Intake — KB artifact insertion")
    print("=" * 64)
    created = 0
    skipped = 0
    for artifact_id, kind, action in actions:
        mark = "+" if action == "created" else "="
        print(f"  {mark} {action:<8}  {artifact_id:<36}  {kind}")
        if action == "created":
            created += 1
        elif action == "skipped":
            skipped += 1
    print("-" * 64)
    print(f"  created={created}  skipped={skipped}  total={len(actions)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
