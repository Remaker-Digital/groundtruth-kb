REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f9b59-52a0-75b2-9973-bd5601f98e9f
author_model: OpenAI Codex Desktop
author_model_version: Codex Desktop interactive runtime; exact foundation-model identifier is not exposed to this task
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb; ordinary per-WI authority only; former CF-10 all-program serialization authority rescinded; dispatcher and TAFE deliberately disabled
author_metadata_source: task-local interactive transcript and current session envelope

bridge_kind: prime_proposal
Document: gtkb-wi5639-scan-helper-exact-numbered-chain-fallback
Version: 005
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5639-scan-helper-exact-numbered-chain-fallback-004.md
Responds-to SHA-256: 746B5FDC9290FD09C6C26BF042F375AAB32336A8A1BE57AD89DEA95693FC51F4

Project Authorization: PAUTH-PROJECT-GTKB-TREE-STABILIZATION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-TREE-STABILIZATION
Work Item: WI-5639
Related Work Items: WI-4618, WI-5068, WI-5638, WI-5662, WI-5665, WI-5666, WI-5761

target_paths: [".claude/skills/gtkb-bridge/helpers/scan_bridge.py", ".codex/skills/gtkb-bridge/helpers/scan_bridge.py"]

implementation_scope: verification_only_rebaseline_after_exact_test_owner_and_lifecycle_repair
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false
source_mutation_expected: false

# Revised Proposal — WI-5639 Renamed Scan-Helper Verification Rebaseline

## Revision Claim

This revision accepts both v004 findings and preserves the safe implemented
predicate. It does not add missing-author provenance to the synthetic
fail-open list and does not mutate the scan helpers again.

The remaining v004 failure has since drifted from one assertion failure to a
deterministic managed-skill rename failure: the full current 32-test module
collects, then records `3 passed, 29 errors` because it still imports the
retired `.codex/skills/bridge/helpers/scan_bridge.py` path. Both approved v001
helper paths were renamed and no longer exist. The current managed helpers are:

- `.claude/skills/gtkb-bridge/helpers/scan_bridge.py`;
- `.codex/skills/gtkb-bridge/helpers/scan_bridge.py`.

Those current files are clean, byte-identical, and already contain the exact
bounded v003 predicate at lines 428-429. WI-5665 v001 historically listed
`platform_tests/scripts/test_scan_bridge.py`, but operative v005 superseded the
broad 29-target cohort with five other named files; current v008 reviews only
that five-file lane. WI-5665 therefore does not currently own the scan test.
WI-5638 v003 explicitly declares the scan test and current v004 is `GO`, so
WI-5638 is the live overlapping owner. WI-5639 must neither duplicate nor race
that target.

After WI-5638 is independently terminal/withdrawn, a later WI-5665 revision or
other governed successor must explicitly acquire and repair the scan test, and
the Tree Stabilization project lifecycle must be coherent through WI-5761 or
its sole governed successor. Only then may WI-5639 request a new independent
`GO` for this renamed two-target rebaseline, a fresh exact claim/start if the
current process requires one, a factual verification-only implementation
report, the full current suite and static/parity evidence, and independent
verification. No source delta is expected or authorized merely because this
revision exists.

## Exact Predecessor Binding

- v004 path:
  `bridge/gtkb-wi5639-scan-helper-exact-numbered-chain-fallback-004.md`;
- v004 status/version: `NO-GO` / `004`;
- v004 SHA-256:
  `746B5FDC9290FD09C6C26BF042F375AAB32336A8A1BE57AD89DEA95693FC51F4`;
- v003 report SHA-256:
  `D85EB9E2CD0738DEE835DCCD5290828B12384216B0DC99B9F237A1FA8FA6789E`;
- v002 independent `GO` remains historical evidence only and does not
  authorize the renamed target cohort or this new verification route.

Any predecessor bytes, live head, role, project, PAUTH, target, ownership, or
test-state drift requires fresh review.

## Finding-By-Finding Correction

### F1 — Full suite was not green

Accepted. WI-5639 remains nonterminal. V003 truthfully reported 31 passed / 1
failed and v004 correctly refused `VERIFIED`. Current evidence is more severe
but differently classified: `python -m pytest
platform_tests/scripts/test_scan_bridge.py -q --tb=short` now reports 3 passed
and 29 setup errors because `HELPER_PATH` still points at the removed
`.codex/skills/bridge/helpers/scan_bridge.py`. This is not evidence that the
current helper predicate regressed; it is exact test-path drift after the
managed skill rename.

Correction: WI-5638's v003/v004 chain currently owns the test module. WI-5639
waits for that `GO` lane to become independently terminal or governed
withdrawn without an overlapping claim/start. A later WI-5665 revision or
other exact governed successor must then explicitly reacquire the test and
update all intended helper/template path assertions. After that exact owner is
terminal, WI-5639 reruns all 32 tests against the current helper pair and may
not request verification unless every test passes.

### F2 — Missing-author fail-open would violate provenance

Accepted without qualification. The current helpers fail open only for these
two exact missing-chain diagnostics:

```python
"Bridge document not found as exact numbered files" in message
or "Bridge document not found as versioned files" in message
```

They do not match missing `author_identity`, wrong roles, malformed metadata,
stale history, arbitrary alternate messages, or unauthorized GO chains.
WI-5665's test repair must make synthetic fixtures structurally valid by
supplying the required canonical author metadata and current paths where the
test intends an activatable proposal. It must not weaken production helper
logic or assert that provenance-free history is activatable.

## Current Renamed Target Evidence

| Target | Bytes | SHA-256 | Git state | Last containing commit |
| --- | ---: | --- | --- | --- |
| `.claude/skills/gtkb-bridge/helpers/scan_bridge.py` | 25967 | `5DBE98DBA6E6EEE97648ADB57F35E6B5E711ECC5AF6762BEF8A6AE7232D3FB23` | clean | `3e7626a415a1190927c2771159c3fd4fa543a72c` |
| `.codex/skills/gtkb-bridge/helpers/scan_bridge.py` | 25967 | `5DBE98DBA6E6EEE97648ADB57F35E6B5E711ECC5AF6762BEF8A6AE7232D3FB23` | clean | `a4430de5251921a1720292f030b920470cf7e84b` |

The former `.claude/skills/bridge/helpers/scan_bridge.py` and
`.codex/skills/bridge/helpers/scan_bridge.py` targets are absent and must not
be recreated. Their historical v003 implementation was carried forward by the
governed skill rename into the clean current files at the exact shared hash.

Current `platform_tests/scripts/test_scan_bridge.py` is clean at 23,452 bytes,
SHA-256
`9258F55569B8976841A02943EC62D47D252AC5AA03075E0BE5C1C4EAB53F8B30`,
last containing commit `e570af0e77f28bc167c58a38b58a141ab27aab3b`. Its module header still names
`.codex/skills/bridge/helpers/scan_bridge.py`, and its template constant still
names the retired `skills/bridge` template. This exact test target was in
WI-5665's superseded 29-target v001 cohort, is absent from its operative
five-file lane, and is explicitly targeted by WI-5638 v003 under current v004
`GO`. It is verification input only for WI-5639.

## Test Ownership, WI-5638 Overlap, And Lifecycle Gate

WI-5665's current canonical physical head is v008 `NO-GO` at
`bridge/gtkb-wi5665-skill-rename-test-recovery-008.md`, SHA-256
`5010D80E3617B796E2D12B75B3F87471EB211811099334A34CE3D6163FEFA134`.
Its operative v005/v008 lane owns only five named files and does not include
the scan test.

WI-5638 v003 targets `platform_tests/scripts/test_scan_bridge.py`; current
v004 is `GO` at SHA-256
`61D9F780A8CB8CFA99E2B5C47CE983415D797998596C2F411293E46BB967CC4B`.
WI-5639 must not receive implementation authority until WI-5638 is either:

1. independently terminal with its exact test postimage and ownership ledger
   accepted; or
2. governed `WITHDRAWN`/superseded with an independent exact non-overlapping
   ownership ledger explicitly assigning the scan test repair elsewhere.

A later WI-5665 revision or other governed successor must then explicitly
reacquire the scan test and repair the retired imports before WI-5639 uses it
as verification evidence. Historical WI-5665 v001 scope is not authority.

The Tree Stabilization project is also lifecycle-scarred: v3 reports `active`
while retaining `completed_at=2026-07-29T06:09:06Z`. WI-5761 governs this
status-only authorization defect. WI-5761 or its sole governed successor must
be independently terminal with a coherent project lifecycle before any
WI-5639 `GO`, claim, or schema-v3 start. A mechanically `allowed` applicability
result does not waive this hold.

No proposal prose, stale MemBase status detail, untracked draft, historical
scope, or current `GO` alone substitutes for the exact ownership and lifecycle
predicates above. No current claim exists for WI-5638, WI-5665, or WI-5639.

## Revised Scope

The implementation cohort is the two current renamed managed helper files.
The expected implementation delta is empty: their bytes already implement the
bounded message predicate and are clean/identical. They are retained as target
scope so the later report can bind and independently verify the exact deployed
helper contract rather than claiming ownership of the separately governed test
change.

After dependency closure, the Prime Builder must:

1. revalidate v005 approval, current PAUTH/project membership, null claims,
   exact target hashes, coherent WI-5761 project-lifecycle evidence, terminal
   WI-5638 disposition, the later exact test-owner postimage, and zero target
   overlap;
2. acquire only the exact current WI-5639 claim/start authority required by
   the approved verification-only route;
3. make no source edit unless a new defect is independently reviewed and a
   later proposal explicitly authorizes it;
4. run the complete current scan-helper suite against the current helper and
   template paths, plus provenance-negative tests, parity, Ruff, format,
   `py_compile`, and exact Git status/hash checks;
5. file a factual report stating zero target mutation when the hashes remain
   unchanged; and
6. obtain independent `VERIFIED` before treating WI-5639 as terminal.

The test module is not a WI-5639 target and may change only under the current
WI-5638 lane or a later explicitly accepted exact ownership successor.
Resolver, implementation
authorization, dispatcher/TAFE, registry, MemBase, Git/index/ref, credentials,
deployment, release, and unrelated files remain outside scope.

## Cross-Harness Disposition

- **Claude:** applicable. `.claude/skills/gtkb-bridge/helpers/scan_bridge.py`
  remains at the exact declared hash and bounded predicate.
- **Codex:** applicable. `.codex/skills/gtkb-bridge/helpers/scan_bridge.py`
  remains byte-identical to the Claude copy at the exact declared hash and
  bounded predicate.
- **Cursor, Antigravity, Goose, Ollama, OpenRouter, and other harnesses:** no
  distinct helper target is declared by this verification-only cohort. They
  consume the governed shared bridge behavior and receive no typed waiver or
  harness-specific divergence from WI-5639.

Any Claude/Codex byte, predicate, path, test, or outcome divergence fails
closed before report or verification. No harness is silently excluded and no
owner waiver is requested.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — new review is required for renamed
  targets and later independent verification.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — missing author provenance remains a
  fail-closed defect; synthetic fixtures must become structurally valid.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — current numbered chains, managed paths,
  hashes, commits, claims, PAUTH, and test ownership control.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — no verification until
  the complete current suite passes.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` and
  `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — all governing links,
  exact targets, project, PAUTH, and WI remain explicit.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` and
  `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — current
  project/PAUTH/operation/target gates remain conjunctive.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — Claude/Codex managed copies remain
  byte-identical and native Windows governance is self-enforced.
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` and
  `ADR-CROSS-HARNESS-PARITY-001` — the exact Claude/Codex helper pair and
  outcomes remain behaviorally identical; no applicable harness waiver exists.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — no retired path recreation,
  provenance weakening, duplicate test ownership, or foreign-byte absorption.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the rename, dependency, reports, and
  results remain durable and forward-only.
- `GOV-STANDING-BACKLOG-001` — WI-5638 owns the current overlapping test lane;
  WI-5665's operative lane excludes the test; WI-5761 owns the lifecycle
  repair; WI-5639 retains only the two-helper verification scope.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — every target/evidence path stays
  inside `E:/GT-KB`.

## Prior Deliberations

- `DELIB-2503` — scanner-fix/project-authorization context.
- `DELIB-20265389` — WI-4618 synthetic inline-GO compatibility contract.
- `DELIB-202666024` — earlier scan-helper parser verification evidence.
- WI-5639 v003/v004 — exact partial implementation report and independent
  NO-GO preserving provenance fail-closed behavior.
- WI-5638 v003/v004 — current explicit scan-test ownership and exact `GO`
  overlap that must become terminal or governed withdrawn first.
- WI-5665 v001/v005/v008 — historical broad scope, operative five-file
  supersession, and current `NO-GO`; no current scan-test ownership.
- WI-5761 — open project-reactivation invariant repair for Tree Stabilization's
  `active` plus non-null `completed_at` lifecycle scar.

No prior deliberation is interpreted as permission to recreate retired skill
paths, mutate WI-5665 targets, or fail open on missing provenance.

## Owner Decisions / Input

No new owner decision is requested. The technical ownership boundary is
deterministic: WI-5638 currently owns the stale test path, a later exact
successor must reacquire it after that lane closes, WI-5761 owns the lifecycle
repair, and WI-5639 owns only verification of the two clean helper postimages.
Existing Tree Stabilization PAUTH remains proposal/review evidence only and
forbids Git commit, dispatcher mutation, deployment, release, and other
separately gated operations.

## Requirement Sufficiency

Existing requirements are sufficient. The original WI-5639 work item,
TEST-11684, v003/v004 findings, current renamed helper bytes, WI-5638's current
test ownership, WI-5665's operative exclusion, WI-5761's lifecycle repair, and
governing provenance/parity/testing specifications determine the correction.
No new owner policy or source behavior is required.

## Specification-Derived Verification Plan

| Requirement | Evidence required after ownership and lifecycle closure |
| --- | --- |
| Missing-chain compatibility | all positive fixtures for exact/current and legacy missing-chain diagnostics pass |
| Provenance fail-closed | missing/wrong author, wrong role, malformed history, stale and unauthorized GO cases remain blocked |
| Full regression | all 32 current `test_scan_bridge.py` tests pass with no deselection or fixture bypass |
| Managed parity | Claude and Codex helper bytes equal exact approved hash or a later independently approved hash |
| Rename correctness | no test or runtime dependency reads retired `.*/skills/bridge/helpers/scan_bridge.py` paths |
| Static quality | Ruff check, Ruff format check, and `py_compile` pass on both current helpers |
| Scope integrity | current helper Git status/hashes and exact WI-5665 changed-path ledger prove no WI-5639 source/test mutation |
| Governance | current GO/claim/start/report/independent verification and append-only chain readback all pass |

## Intuitiveness / Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5639 v003/v004; WI-5638 v003/v004; WI-5665 v001/v005/v008; WI-5761; TEST-11684; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "canonical_authority": "Current status-bearing numbered bridge chains, versioned MemBase project lifecycle, exact project authorization evaluation, and clean Git/object bytes",
  "primary_route": "Close or withdraw the WI-5638 overlap, reconcile project lifecycle through WI-5761, assign an explicit scan-test owner, then perform a zero-delta WI-5639 verification cycle",
  "before_behavior": "The renamed helpers already preserve the bounded safe predicate, but the 32-test module imports a retired path; WI-5638 currently owns that test under GO; WI-5665 no longer owns it; and Tree Stabilization is active with a retained completed_at value.",
  "after_behavior": "An exact governed owner repairs the test after WI-5638 disposition and lifecycle reconciliation, all 32 tests pass against unchanged parity-identical helpers, and WI-5639 reports a factual zero-source-delta result for independent verification.",
  "self_descriptive_naming": "current_helper_paths, retired_helper_paths, exact_missing_chain_diagnostics, test_owner_work_item, project_lifecycle_version, completed_at, helper_sha256, test_sha256, and predecessor_sha256",
  "obsolete_guidance_disposition": "Historical WI-5665 v001 ownership is superseded by its five-file v005 lane; retired skills/bridge paths are not recreated; mechanically allowed PAUTH output does not waive the WI-5761 lifecycle hold.",
  "history_preservation": "WI-5639 v001-v004, the WI-5638 and WI-5665 chains, renamed helper commits, current failing test evidence, and lifecycle scar remain durable and are not rewritten.",
  "baseline": {
    "helper_pair": "clean, byte-identical, 25967 bytes each, SHA-256 5DBE98DBA6E6EEE97648ADB57F35E6B5E711ECC5AF6762BEF8A6AE7232D3FB23",
    "focused_test": "3 passed and 29 setup errors from retired helper path",
    "scan_test_owner": "WI-5638 v003 under current v004 GO",
    "tree_stabilization_lifecycle": "v3 active with completed_at 2026-07-29T06:09:06Z"
  },
  "expected_result": {
    "helper_pair": "unchanged, byte-identical, bounded exact diagnostics only",
    "focused_test": "32 passed with no deselection, xfail, timeout suppression, or provenance weakening",
    "scan_test_owner": "explicit governed successor after WI-5638 terminal or withdrawn disposition",
    "tree_stabilization_lifecycle": "coherent active lifecycle independently accepted through WI-5761 or sole successor"
  },
  "rollback": {
    "instructions": "This proposal authorizes no source or test mutation and no commit; unexpected deltas stop for a separately reviewed proposal. Any later test repair rolls back only through its own exact governed owner.",
    "verification": "Recheck both helper hashes and parity, retired-path absence, full test result, project lifecycle, PAUTH, exact ownership chains, claims, start packets, and Git status."
  },
  "hard_invariants": [
    "missing or wrong author provenance remains fail closed",
    "only the two exact missing-chain diagnostics are compatibility fail-open cases",
    "retired helper paths are never recreated",
    "WI-5639 never mutates the separately owned test module",
    "WI-5638 overlap and WI-5761 lifecycle hold close before WI-5639 GO, claim, or start",
    "the two managed helper copies remain byte-identical",
    "no dispatcher, TAFE, registry, database, Git index/ref, credential, deployment, release, or unrelated mutation"
  ],
  "fail_closed_conditions": [
    "WI-5638 remains GO or has an active claim/start over the scan test",
    "no exact later governed owner has reacquired and repaired the scan test",
    "Tree Stabilization remains active with a non-null completed_at or lifecycle evidence is stale",
    "either helper hash, path, parity, predicate, Git state, project membership, or PAUTH drifts",
    "any of the 32 tests fails, errors, is deselected, xfailed, or depends on a retired path",
    "missing-author or malformed-history behavior becomes activatable",
    "verification would require a source/test mutation or Git commit"
  ],
  "essential_context_preservation": "Preserve exact v004 finding and hash, renamed and retired paths, helper and test hashes, 3/29 failure classification, WI-5638 current GO ownership, WI-5665 scope supersession, WI-5761 lifecycle scar, project/PAUTH evidence, provenance-negative behavior, and the zero-delta requirement."
}
```

## Acceptance Criteria

1. WI-5638 is independently terminal or governed withdrawn, WI-5761 or its
   sole successor has made the Tree Stabilization lifecycle coherent, and a
   later exact owner has repaired `platform_tests/scripts/test_scan_bridge.py`
   without weakening provenance.
2. All 32 current scan-helper tests pass without deselection, xfail, timeout
   suppression, or broad missing-author fail-open logic.
3. The two current managed helpers remain byte-identical and contain only the
   exact current/legacy missing-chain compatibility predicate.
4. Missing/wrong author metadata and every real malformed or unauthorized GO
   chain remain `blocked_non_activatable` with exact reasons.
5. Retired helper paths are not recreated; tests and runtime consumers use the
   current `gtkb-bridge` paths.
6. WI-5639 makes no test, resolver, authorization, dispatcher/TAFE, registry,
   database, Git/index/ref, credential, deployment, release, or unrelated
   mutation.
7. A factual verification-only report binds current target hashes and executed
   results, then a distinct Loyal Opposition session independently verifies.

## Risks And Rollback

- **Ownership race:** any WI-5638, later test-owner, WI-5761, claim, head,
  target, or project-lifecycle drift keeps WI-5639 held.
- **False green:** fixture changes must add valid provenance/current paths; they
  may not weaken assertions or production denial.
- **Rename regression:** any dependency on retired helper paths is a failure,
  not authority to recreate them.
- **Unexpected source delta:** stop and revise before mutation; do not absorb it
  into a verification-only report.
- **Rollback:** this revision makes no source change. The existing predicate is
  preserved; any future rollback requires a separately governed source change
  and full negative/positive parity verification.

## Candidate Pre-Filing Gates

Before governed filing, rerun exact candidate applicability, mandatory clause,
credential, collision, duplicate-thread, citation, pattern, project/PAUTH,
claim, target-currentness, and writer-compliance checks. Filing must use a
short exact draft claim and receipt-backed writer, then prove live hash/status,
consumed capability, released claim, and no pending sidecar.

## Files Expected To Change

None during the verification-only implementation. The exact governed target
cohort whose unchanged deployed behavior must be verified is:

- `.claude/skills/gtkb-bridge/helpers/scan_bridge.py`
- `.codex/skills/gtkb-bridge/helpers/scan_bridge.py`

## Recommended Commit Type

N/A — this verification-only route expects no mutation and the PAUTH forbids
`git_commit`. Any future source or test delta requires a separate governed
proposal and authority.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
