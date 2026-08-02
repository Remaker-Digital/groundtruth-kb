REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb1f2-2f91-7b82-ac15-acdd56e13d1e
author_model: GPT-5
author_model_version: GPT-5 Codex desktop runtime
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; manual physical-bridge continuation; dispatcher and TAFE deliberately disabled
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: prime_proposal
Document: gtkb-wi584x-codex-home-harness-selector-false-positive
Version: 005
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi584x-codex-home-harness-selector-false-positive-004.md
Controlling GO: bridge/gtkb-wi584x-codex-home-harness-selector-false-positive-002.md

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5877
Linked Test: TEST-11805

target_paths: ["scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_work_intent_role_eligibility.py"]
implementation_scope: exact_reobservation_source_and_focused_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

KB Mutation: This proposal performs no MemBase or `groundtruth.db` write or mutation. The already-created WI-5877 and TEST-11805 records are cited as current authority only.

# REVISED Proposal — Bind the CODEX_HOME Selector Repair to WI-5877

## Revision Claim

Accept NO-GO v004 F1 and F2 while correcting its now-collided work-item
reference. `WI-5842` already canonically identifies a different
`cloud_harness_base._dispatch_write` defect in
`PROJECT-GTKB-CLOUD-HARNESS-TEMPLATE`; it cannot lawfully be repurposed for
this thread. The exact selector defect is now captured as active project member
`WI-5877`, with linked `TEST-11805`, under the active list-free Bridge Protocol
Reliability PAUTH version 2.

The one-line source correction proposed in v001 is already present as a foreign,
uncommitted exact hunk. This revision neither overwrites nor silently attributes
that byte. After a fresh independent GO and a fresh exact claim/start packet,
Prime Builder will re-observe the source by exact SHA-256 and exact one-line
diff, adopt it only if unchanged, and add the missing focused regression in the
declared test target. Any drift beyond that hunk fails closed and returns for
review.

No protected source or test mutation is authorized by this revision itself.

## Requirement Sufficiency

Existing requirements are sufficient. Session-role authority must come from the
current validated session envelope; a permanent installation path cannot be a
live harness selector. No requirement amendment or owner clarification is
needed for this two-file correction.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5877; TEST-11805; NO-GO v004; DELIB-202667732; owner-approved exact re-observation",
  "canonical_authority": "GOV-SESSION-ROLE-AUTHORITY-001, DCL-SESSION-ROLE-RESOLUTION-001, GOV-FILE-BRIDGE-AUTHORITY-001, and PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730 v2",
  "primary_route": "Use an explicit GTKB_HARNESS_NAME first, live harness-specific session signals second, and canonical envelope search when no selector is justified; never treat CODEX_HOME as a live session signal.",
  "before_behavior": "A permanent CODEX_HOME installation path forced every otherwise-unselected worker lookup into the Codex envelope directory and could reject a valid non-Codex Prime Builder session.",
  "after_behavior": "CODEX_HOME alone selects no harness; CODEX_THREAD_ID still selects Codex; explicit GTKB_HARNESS_NAME remains highest precedence; the validated session envelope remains the only role authority.",
  "self_descriptive_naming": "Existing selector and environment names remain unchanged; tests name installation-only CODEX_HOME, live CODEX_THREAD_ID, and explicit Goose precedence directly.",
  "obsolete_guidance_disposition": "The collided WI-5842 placeholder and quarantined illegal successor remain historical evidence only and are not reused as live authority.",
  "history_preservation": "The numbered bridge chain, quarantined forensic artifact, canonical WI-5842 record, new WI-5877 record, foreign source hunk, and unrelated worktree changes are preserved append-only or byte-for-byte.",
  "baseline": {
    "source_head_sha256": "792f3fb422706f40819c443eb691ec90874b68c13209030ab7d8fbd2f9484655",
    "source_current_sha256": "633e22acff0e6e5b9964827ccac40a3299d7fd513918f24c90469ac9a338f1e3",
    "test_sha256": "d45d755a1cbbbe65b122919b058f52fa2486ea379edd1442334ffa4d1c88ac05",
    "source_diff": "One line removes only the CODEX_HOME disjunct from Codex selection."
  },
  "expected_result": {
    "role_authority": "A matching non-Codex session envelope can be found when only CODEX_HOME is present, and its validated role controls claim eligibility.",
    "codex_compatibility": "CODEX_THREAD_ID continues to select Codex.",
    "explicit_precedence": "GTKB_HARNESS_NAME=goose remains authoritative as a document selector.",
    "scope": "Only the exact reviewed source hunk and focused test additions appear in the two declared paths."
  },
  "rollback": {
    "instructions": "Preserve this proposal/report/verdict chain, then perform a separately governed two-path revert; do not restore the collided WI-5842 linkage or quarantined illegal successor.",
    "test": "Re-run the focused selector and work-intent role-eligibility suite after rollback."
  },
  "hard_invariants": [
    "Session-envelope provenance remains the only role authority",
    "Explicit harness declaration remains highest precedence",
    "CODEX_THREAD_ID remains the live Codex selector",
    "No dispatcher or TAFE activation or mutation",
    "No destructive rewrite of foreign or quarantined evidence"
  ],
  "fail_closed_conditions": [
    "Source SHA-256 or diff differs from the reviewed exact hunk",
    "Test target becomes dirty or claimed by another implementation",
    "Project PAUTH, GO, claim, or start packet is missing or stale",
    "Any focused regression, lint, format, compile, or exact-scope check fails"
  ],
  "essential_context_preservation": "Keep explicit declaration and live-session signals distinct from permanent installation paths, retain canonical envelope validation as role authority, and preserve every unrelated worktree byte."
}
```

## Findings Addressed

### F1 — Active GO misclassified as stale carrier (P1)

Accepted. The implementation is not abandoned and the GO-002 design remains
the selected one-line correction. Because its placeholder `WI-5842` has
collided with a different canonical work item, this v005 binds the work to new
approved-project carrier `WI-5877` and requests a fresh independent GO before
implementation. Prime Builder will not claim implementation authority from the
obsolete placeholder metadata.

### F2 — Illegal REVISED already quarantined (P3)

Accepted. The quarantined illegal successor remains untouched as forensic
evidence. This is the first lawful post-NO-GO REVISED successor to live v004;
it uses exact `Responds to` metadata and does not use `Replaces:`.

## Exact Scope and Current Baseline

| Path | HEAD SHA-256 | Current SHA-256 | Disposition |
| --- | --- | --- | --- |
| `scripts/bridge_work_intent_registry.py` | `792f3fb422706f40819c443eb691ec90874b68c13209030ab7d8fbd2f9484655` | `633e22acff0e6e5b9964827ccac40a3299d7fd513918f24c90469ac9a338f1e3` | Foreign one-line hunk only: remove `or os.environ.get("CODEX_HOME")`; exact re-observation required after GO. |
| `platform_tests/scripts/test_work_intent_role_eligibility.py` | `d45d755a1cbbbe65b122919b058f52fa2486ea379edd1442334ffa4d1c88ac05` | same | Clean focused test target. |

The source hunk is allowed to remain only if its current bytes and diff remain
exactly as recorded above. The implementation will not reset, rewrite, or claim
unrelated foreign work.

## Exact Implementation Plan

1. Revalidate this v005 as the independently approved proposal and acquire a
   current-session exact claim plus schema-v3 implementation-start packet for
   both declared paths.
2. Re-observe the source target: current SHA-256 must remain
   `633e22acff0e6e5b9964827ccac40a3299d7fd513918f24c90469ac9a338f1e3`,
   and `git diff` must remain the single removal of the `CODEX_HOME` disjunct.
3. If exact, preserve/adopt that hunk without a destructive rewrite. If not
   exact, stop and file a new revision with the new evidence.
4. Add focused tests proving `CODEX_HOME` alone returns no harness selector,
   `CODEX_THREAD_ID` selects Codex, and explicit `GTKB_HARNESS_NAME=goose`
   retains highest precedence. Exercise envelope lookup so the test proves
   role authority still comes from the validated session document.
5. Run focused and adjacent work-intent eligibility tests, Ruff lint/format,
   compile, diff check, and exact two-path scope verification.
6. File a factual REVISED implementation report for independent verification;
   release the claim. Do not activate or mutate TAFE/dispatcher state.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — exact append-only chain, independent GO,
  current claim, and implementation-start authority.
- `GOV-SESSION-ROLE-AUTHORITY-001` and
  `DCL-SESSION-ROLE-RESOLUTION-001` — session-envelope provenance controls
  worker role; installation variables do not.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — active
  project membership, PAUTH, and exact targets are rechecked at operation time.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete
  requirement-to-change linkage.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — executed behavioral
  evidence is mandatory before VERIFIED.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — selector
  precedence and envelope lookup are tested mechanically.
- `GOV-WORK-TREE-HYGIENE-001` — foreign bytes are preserved and adopted only
  through exact reviewed evidence.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — Codex, Claude, poller, and
  explicit-harness selection remain intact.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the collided placeholder,
  replacement work item, proposal, test, report, and verdict remain a durable
  append-only lifecycle graph.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all dependencies and evidence
  remain within `E:/GT-KB`.

## Specification-Derived Verification Plan

| Requirement | Deterministic evidence |
| --- | --- |
| Installation path is not session authority | With only `CODEX_HOME` set, `_worker_harness_selector()` returns `None`. |
| Live Codex signal remains supported | With `CODEX_THREAD_ID` set, selector returns `codex`. |
| Explicit declaration wins | With `GTKB_HARNESS_NAME=goose` plus Codex installation variables, selector returns `goose`. |
| Envelope remains role authority | Claim resolution locates the matching Goose envelope and uses its validated role; no registry/default role supplies authority. |
| Existing behavior remains intact | Focused work-intent eligibility suite, adjacent claim tests, Ruff, format, and compile pass. |
| Exact worktree ownership | Final diff contains only the reviewed selector hunk and focused tests in the two declared paths. |

Planned commands:

```powershell
groundtruth-kb\.venv\Scripts\python.exe -m pytest platform_tests/scripts/test_work_intent_role_eligibility.py -q --tb=short
groundtruth-kb\.venv\Scripts\ruff.exe check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_work_intent_role_eligibility.py
groundtruth-kb\.venv\Scripts\ruff.exe format --check scripts/bridge_work_intent_registry.py platform_tests/scripts/test_work_intent_role_eligibility.py
groundtruth-kb\.venv\Scripts\python.exe -m py_compile scripts/bridge_work_intent_registry.py platform_tests/scripts/test_work_intent_role_eligibility.py
git --no-optional-locks diff --check -- scripts/bridge_work_intent_registry.py platform_tests/scripts/test_work_intent_role_eligibility.py
```

## Prior Deliberations

- `DELIB-202667732` — list-free whole-project Bridge Protocol Reliability
  authorization; normal proposal, GO, claim, start, report, and VERIFIED gates
  remain mandatory.
- `DELIB-20260801-GTKB-PARALLEL-CONTENTION-TIMER-TOLERANCE` — contention is
  re-observed generously and does not authorize duplicate work.
- Owner approval of exact re-observation in this session — unchanged foreign
  bytes may be adopted only when their exact reviewed hash and hunk remain
  stable under live authority.

## Pre-Filing Preflight

The strict target-coverage, applicability, and clause preflights must all pass
against this completed draft immediately before filing. Their fresh results are
the publication gate, not this statement.

## Risk and Rollback

- Risk: a concurrent writer changes the source after review. Mitigation: exact
  SHA-256 plus exact-diff re-observation after GO and immediately before report.
- Risk: removing `CODEX_HOME` masks a true Codex session without
  `CODEX_THREAD_ID`. Mitigation: explicit `GTKB_HARNESS_NAME` remains highest
  precedence, and the test suite covers the supported live signal and
  canonical envelope search fallback.
- Rollback: preserve the bridge/report/verdict history, then use a separately
  governed two-path revert. Re-run the same focused selector and claim-role
  suite. Never restore the collided `WI-5842` reference or quarantined illegal
  bridge successor.
