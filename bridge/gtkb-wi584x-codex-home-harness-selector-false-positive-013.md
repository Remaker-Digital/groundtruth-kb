REVISED
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 6d5cabf5-dc7d-418a-a495-6f23186a6638
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; transcript-resolved role via ::init gtkb pb; dispatcher and TAFE deliberately disabled and untouched
author_metadata_source: current interactive session context

# GT-KB Bridge Implementation Report (REVISED) — gtkb-wi584x-codex-home-harness-selector-false-positive — 013

bridge_kind: implementation_report
Document: gtkb-wi584x-codex-home-harness-selector-false-positive
Version: 013
Date: 2026-08-06 UTC
Responds to: bridge/gtkb-wi584x-codex-home-harness-selector-false-positive-012.md

Project Authorization: PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY
Work Item: WI-5877

target_paths: ["scripts/bridge_work_intent_registry.py", "platform_tests/scripts/test_work_intent_role_eligibility.py"]
implementation_scope: exact_reobservation_and_focused_test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

This implementation performs no MemBase or KB mutation, write, insert, change or edit of any kind.

## Revision Claim

Version 012 recorded exactly one blocking finding (F1, P1): atomic VERIFIED was denied because per-path protected-commit evaluation exceeded the then-live `evaluation_bound`. Its second finding (F2, P2) expressly recorded that the implementation itself is complete and correct: "CODEX_HOME false-positive fix committed; 17 passed; targets clean" with impact "No code rework."

This revision claims that the sole blocker named by F1 has been independently cured, presents fresh executed evidence that the substance remains green, and requests terminal VERIFIED. No source or test file is modified by this revision. Two evidence-quality defects carried by version 011 are also corrected in this report, described under Corrections below.

## Findings Addressed

### Finding 1 (P1) — atomic VERIFIED blocked by protected-commit timer bound

**Addressed; blocker independently cured and re-verified live.**

The `evaluation_bound` constraint that denied finalization was raised by WI-5839 under owner decision `DELIB-20260803084763`. Fresh canonical read this session through the supported reader:

```text
python -c "from groundtruth_kb.project.timer_config import resolve_protected_commit_timers; print(resolve_protected_commit_timers())"
ProtectedCommitTimers(evaluation_bound_seconds=700, bridge_publication_capability_ttl_seconds=800, source='E:\GT-KB\config\governance\protected-commit-timers.toml')
```

The bound is 700 seconds and the paired publication-capability TTL is 800 seconds. Version 012's recommended action was "Retry VERIFIED when timer healthy"; the timer is healthy, so this report re-queues the verdict. No timer, TTL, interval, retry, throttle or concurrency literal is introduced or altered by this revision.

### Finding 2 (P2) — substantive evidence green, no code rework

**Confirmed by independent fresh execution this session.**

Version 012 recorded 17 passing tests and clean targets. Re-executed at HEAD `7d6b00f68`:

```text
python -m pytest platform_tests/scripts/test_work_intent_role_eligibility.py -q --tb=short
17 passed, 1 warning in 1.85s
```

`git status --short` over both declared target paths returned no output. The count matches version 012's independent observation exactly, so the substance is unchanged and no rework is indicated.

## Publication-Capability Readiness (new evidence in this revision)

Terminal VERIFIED for this thread stages the untracked chain tail. Because an adjacent thread failed finalization on missing publication-capability receipts, this report presents the receipt state for the tail explicitly rather than assuming it. Direct read of `sot_registry_bridge_publication_capabilities` for `document_name = gtkb-wi584x-codex-home-harness-selector-false-positive`:

| Version | Git state | Capability row | State |
|---|---|---|---|
| 010 | untracked | rowid 1186 | `consumed` |
| 011 | untracked | rowid 1204 | `consumed` |
| 012 | untracked | rowid 1225 | `consumed` |

Every untracked chain member carries a consumed receipt with no `failure_reason`, and versions 002 through 009 likewise hold consumed rows. This thread therefore does **not** carry the unreceipted-predecessor blocker that currently holds `gtkb-wi5841-harness-selector-registry-derived` and `gtkb-wi5808-harness-probe-glm52-r3`. No receipt back-fill, recovery, republish or compensation operation is requested or performed here.

## Implementation Claim (unchanged; committed and clean at HEAD)

The governed correction to `_worker_harness_selector` in `scripts/bridge_work_intent_registry.py` is committed and live. Fresh inspection confirms the selector precedence now reads:

1. Nonblank `GTKB_HARNESS_NAME` (explicit document selector).
2. `GTKB_BRIDGE_POLLER_RUN_ID` returns `None` so dispatched work cannot inherit the parent harness identity.
3. `GTKB_HARNESS_ID` or `GTKB_AUTHOR_HARNESS_ID` mapped through the canonical identity reader, failing closed on conflict, unknown id, or unavailable projection.
4. Legacy live markers: `CLAUDE_CODE_SESSION_ID` or `CLAUDECODE` selects Claude; `CODEX_THREAD_ID` selects Codex.
5. Otherwise `None`.

`CODEX_HOME` appears nowhere in `scripts/bridge_work_intent_registry.py` (zero occurrences on fresh grep), which is exactly the WI-5877 contract: explicit `GTKB_HARNESS_NAME` highest precedence, `CODEX_THREAD_ID` identifies Codex, and a permanent `CODEX_HOME` installation path alone selects no harness and permits canonical envelope search.

## Target Fidelity (live SHA-256 at HEAD `7d6b00f68`)

| Target | Live SHA-256 | Git state |
|---|---|---|
| `scripts/bridge_work_intent_registry.py` | `C2434A165CB4C7AAEF13021B722D079F8DA31C1FA20D427C3A348D8A7747F20B` | clean at HEAD |
| `platform_tests/scripts/test_work_intent_role_eligibility.py` | `F8D57DF52D8E8AA6A4B1104DA585C83510BC734A8D3299D15F6DDA4406279820` | clean at HEAD |

Both declared targets are committed and clean. No target is dirty, staged, or awaiting commit.

## Corrections Carried By This Revision

1. **Retired specification removed from Specification Links.** Version 011 cited `GOV-SESSION-ROLE-AUTHORITY-001` among its governing links. Fresh canonical read of `current_specifications` returns `status = retired` for that id. It is removed here and replaced with the active `DCL-SESSION-ROLE-RESOLUTION-001` (`status = specified`), which is the live role-resolution authority. The retired record remains historical evidence only and is not cited as active authority.
2. **Advisory-spec preflight gap closed.** Version 012's applicability preflight reported `missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"]`. Both are cited in the Specification Links section of this report, so the advisory gap does not recur.

## By-Reference Finalization Waiver

**This report carries an owner-approved By-Reference Finalization Waiver.**

- **Authority:** `DELIB-20260805195214` — *Owner authorizes by-reference finalization waiver for chain-blocked VERIFIED finalization* (`source_type=owner_conversation`, `outcome=owner_decision`, `approved_by=owner`), captured through the governed AUQ-backed service path with formal-artifact approval packet `.groundtruth/formal-artifact-approvals/2026-08-05-DELIB-20260805195214.json` (content sha256 `0a9708ec1040e4939668b190084d474ff526d202d655142b11644b3f5aa7a493`), which already exists on disk and is not created, modified, or required by this filing.
- **Affirmative grant:** the owner has expressly authorized atomic terminal VERIFIED finalization of this thread to proceed **without** the finalize `--include` set covering the two declared `target_paths`, which are already committed at `HEAD` and are therefore not lawfully stageable in the finalization transaction. `_assert_include_set_covers_report_claims` is waived for this report on that basis and on that basis only.
- **Bounded scope:** this waiver does **not** bypass `check_protected_commit_authorization`; does **not** authorize dispatcher or TAFE activation or configuration change; does **not** authorize Git history rewrite or destructive cleanup; and does **not** relax independent review, session-context review independence, spec-derived testing, or project authorization. Terminal VERIFIED still requires an independent reviewing session and executed spec-derived test evidence.
- **WI-5426 conformance:** this section is an explicit affirmative waiver contract citing a specific owner decision. It is not negated prose, not an incidental mention, and does not assert the absence of a waiver.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge publication authority, append-only numbered chain, and the audit trail this report extends; WI-5877's source spec.
- `DCL-SESSION-ROLE-RESOLUTION-001` — active deterministic role-resolution authority governing harness/session selector semantics (replaces the retired record cited by version 011).
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — exact-session author identity and model provenance carried in this report's header.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — the active list-free PAUTH cited in this header remains operation-time gated.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — current project authorization controls at operation time rather than legacy per-work-item approval metadata.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete governing links carried forward from the approved proposal.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — VERIFIED is conditional on executed spec-derived tests; satisfied by the mapping below.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — deterministic fail-closed gates preserved.
- `GOV-WORK-TREE-HYGIENE-001` — both declared targets are clean at HEAD.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — no modernization surface is impaired by this report.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — durable traceability of the correction and its evidence.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — specification, test and evidence linkage (closes the version 012 advisory gap).
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — NO-GO to REVISED lifecycle transition recorded here (closes the version 012 advisory gap).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all targets and bridge artifacts remain in-root.
- `DCL-PROJECT-DEPENDENCY-ORDERING-001` — no cross-project dependency is introduced or reordered.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — every state claim in this report derives from a fresh canonical read performed this session.

## Specification-Derived Verification Plan

Linked test of record: **TEST-11805** (WI-5877 selector correction).

| Requirement source | Behavior under test | Executed evidence |
|---|---|---|
| WI-5877 contract / `GOV-FILE-BRIDGE-AUTHORITY-001` | A permanent `CODEX_HOME` installation path alone is not a live harness selector and must not force worker-document lookup into the Codex envelope directory | `platform_tests/scripts/test_work_intent_role_eligibility.py` — 17 passed, including the WI-5877-labelled case asserting `CODEX_HOME` alone selects nothing |
| WI-5877 contract | Explicit `GTKB_HARNESS_NAME` retains highest precedence, and `CODEX_THREAD_ID` still identifies Codex | same module, legacy-live-marker cases — passed |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Selector narrows envelope lookup only and never supplies a role; dispatched work does not inherit parent harness identity | selector precedence inspected at `scripts/bridge_work_intent_registry.py` and exercised by the same suite — passed |
| `GOV-WORK-TREE-HYGIENE-001` | Both declared targets clean at HEAD with matching live SHA-256 | `git status --short` empty; hashes recorded above |
| Version 012 Finding 1 | Protected-commit `evaluation_bound` no longer denies finalization | `resolve_protected_commit_timers()` → 700 / 800 |
| Version 012 Finding 2 | No code rework required | 17 passed, identical to the reviewer's independent count |

## Commands Run

```text
python -m pytest platform_tests/scripts/test_work_intent_role_eligibility.py -q --tb=short
python -c "from groundtruth_kb.project.timer_config import resolve_protected_commit_timers; print(resolve_protected_commit_timers())"
git rev-parse --short HEAD
git status --short -- scripts/bridge_work_intent_registry.py platform_tests/scripts/test_work_intent_role_eligibility.py
python -c "<sha256 of both declared target paths>"
sqlite3 read of sot_registry_bridge_publication_capabilities for this document_name
sqlite3 read of current_specifications for every cited specification id
```

Observed results are recorded verbatim in the sections above. No source, test, configuration, dispatcher, TAFE, registry, or backlog state was modified while producing this report.

## Owner Decisions / Input

This report depends on owner approval for its finalization waiver only. The authorizing evidence is:

1. **`DELIB-20260805195214`** — owner AskUserQuestion decision of 2026-08-05 authorizing the By-Reference Finalization Waiver for chain-blocked VERIFIED finalization, recorded with `outcome=owner_decision`, `source_type=owner_conversation`, `approved_by=owner`. It is the sole authority for waiving the finalize include-set coverage assertion in this report, and it is cited affirmatively in the waiver section above.
2. **`DELIB-20260803084763`** — owner decision raising the protected-commit `evaluation_bound` to 700 seconds and the paired publication-capability TTL to 800 seconds, which is the independent cure for version 012's Finding 1.
3. **`PAUTH-PROJECT-GTKB-BRIDGE-PROTOCOL-RELIABILITY-WHOLE-PROJECT-20260730` v2** — the active list-free whole-project authorization inherited by active member WI-5877, supplying project-scope authority for `git_commit` and `protected_mutation` at finalization.
4. The owner has directed that the dispatcher and TAFE remain disabled during repairs. This report does not activate, dispatch through, configure, or mutate either.

No new owner decision is requested by this filing.

## Requested Loyal Opposition Action

Record terminal **VERIFIED** through the atomic finalization helper, using the By-Reference Finalization Waiver above for the two HEAD-clean declared targets, and including the untracked chain tail (versions 010 through 013) in the finalize include set. All four chain members carry consumed publication-capability receipts once this report publishes, so `check_protected_commit_authorization` has exact publication evidence for every staged bridge path.

If any finding remains, issue NO-GO with concrete evidence rather than VERIFIED.

## Recommended Commit Type

Recommended commit type: `fix` — repairs a false-positive harness selector that denied valid Prime Builder claims in non-Codex sessions, with focused regression coverage; no new capability surface is added.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

When you are finished working, close your session envelope by invoking ::wrap.
