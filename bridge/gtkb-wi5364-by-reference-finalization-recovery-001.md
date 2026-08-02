NEW
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb353-983b-7383-b57e-3b9fc6410af5
author_model: GPT-5 Codex
author_model_version: GPT-5
author_model_configuration: Codex Desktop interactive Prime Builder; owner-declared role via ::init gtkb pb; dispatcher/TAFE deliberately disabled
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: prime_proposal
Document: gtkb-wi5364-by-reference-finalization-recovery
Version: 001
Date: 2026-08-01 UTC
Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-ASSURANCE
Work Item: WI-5364
target_paths: ["bridge/gtkb-wi5364-by-reference-finalization-recovery-003.md"]
implementation_scope: governance_evidence_only
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
dispatcher_or_tafe_activation_in_scope: false

# WI-5364 By-Reference Finalization Recovery — Codex Hook Batch Parity

## Summary

Recover the already-committed WI-5364 behavior through a fresh, role-correct, no-code finalization cycle. The original thread is latest NO-GO v004 after its 2026-07-16 implementation-start packet collided with an unrelated thread. That historical mechanical blocker no longer describes the current implementation: all four approved target paths are clean committed blobs, Codex hook parity passes, and all 14 focused tests pass.

This proposal authorizes only a future governance-evidence implementation report at the declared target path. It does not authorize source, test, configuration, hook, dispatcher/TAFE, harness, registry, database, Git, credential, release, deployment, cleanup, or external-system mutation.

## Historical Chain Quarantine

- `gtkb-wi5364-codex-hook-batch-parity` remains append-only at NO-GO v004. Its v002 GO approved the four-path design; v003 correctly failed closed when no named schema-v3 start packet was produced; v004 required the packet-isolation defect to be resolved before another implementation attempt.
- The current bytes must not be represented as having been implemented under that failed start. They entered current HEAD through later custodial commits that also contain adjacent work.
- `gtkb-wi5370-missing-targets-wi5364-codex-hook-batch-parity` remains NO-GO v004 because its archive target was ignored rather than durably tracked. This recovery neither relies on nor rewrites that failed archive path.
- `gtkb-wi5370-no-responds-wi5364-codex-hook-batch-parity` is WITHDRAWN v002 and supplies no terminal authority.
- WI-5364's MemBase `resolved` state and reconciler completion evidence are stale derived metadata because no role-correct independent VERIFIED exists on the implementation thread.

## Current Exact Evidence Cohort

Current HEAD: `75decbfa704fe50288aecbc5669def329a0825df`.

| Read-only evidence path | Git blob | SHA-256 | State |
| --- | --- | --- | --- |
| `.codex/config.toml` | `cd126532e0c5d2b339fbac0661c01d1224fc4362` | `D5CC947C2F1E7C88ECB11248F250879ECB47F7A0941DE68DB07EFFF13983DF97` | clean |
| `.codex/gtkb-hooks/session_wrapup_trigger_dispatch.py` | `34890d2888810790d8829c8163467fbb446544ea` | `DF65D664B2A1B60206FCA4F693DF5EF832997CBDDFA4C9F0E89A8BDA7042437E` | clean |
| `scripts/check_codex_hook_parity.py` | `3c6e78386ddcfc3c69b2bc125b2c203907317833` | `DB9AEB62F66428F3CDE16ADB567094E5A206D6F55F6092ED0749397EFC52C519` | clean |
| `platform_tests/scripts/test_codex_hook_parity.py` | `2330ae7de4f414a1921097c27d6c254195b68dee` | `662C3E1F94ABB4020B3D54CB5A8BB9B5A645A3ADB6B432F8EB12EDD06D28B9F9` | clean |

The current config has `hooks = true`; the wrap-up dispatcher contains no `--role-profile` override; the checker imports the shared batch-aware `enumerate_hook_surfaces` parser and fails closed on missing, unreadable, malformed, or incomplete batch evidence. Any hash or scoped-worktree drift before the future report fails closed and returns this proposal for revision.

## By-Reference Procedure After Independent GO

1. Acquire a fresh exact claim for this recovery slug and obtain a schema-v3 implementation-start packet whose only mutable target is `bridge/gtkb-wi5364-by-reference-finalization-recovery-003.md`.
2. Re-read the original and both WI-5370 repair heads, current WI/project/PAUTH state, current HEAD, the four hashes/blobs, and exact scoped Git status.
3. Execute the specification-derived read-only test plan below.
4. File a factual implementation report through the governed writer with exact observed counts, hashes, warnings, and attribution exclusions.
5. Submit the report for independent Loyal Opposition VERIFIED/NO-GO review.

No source/config/test edit, source/config/test claim, backfill, cherry-pick, amend, rebase, staging, commit, push, runtime activation, or cleanup is authorized. The future report is not itself terminal verification.

## Requirement Sufficiency

Existing requirements are sufficient. The original approved proposal already maps live Windows hooks, batch-aware single execution, canonical role discovery, no-window containment, and parity enforcement. This recovery changes no product behavior; it restores truthful governed evidence for current committed behavior.

## Specification Links

- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `SPEC-CODEX-HARNESS-GOVERNANCE-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-HARNESS-ROLE-PORTABILITY-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-RELEASE-READINESS-GOVERNED-TESTING-001`
- `DCL-PROJECT-DEPENDENCY-ORDERING-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`

## Prior Deliberations

- `DELIB-0836` — original Codex hook fallback stance, later refined by live-Windows hook authority.
- `DELIB-CODEX-HARNESS-PARITY-SPEC-BUNDLE-2026-05-05` — mechanical Codex governance parity.
- `DELIB-202666274` — modernization project authorization while retaining independent GO, claim/start, report, and VERIFIED gates.
- `bridge/gtkb-wi5364-codex-hook-batch-parity-001.md` — complete four-path design and acceptance map.
- `bridge/gtkb-wi5364-codex-hook-batch-parity-004.md` — historical implementation-start collision and required fail-closed disposition.
- `bridge/gtkb-wi5370-missing-targets-wi5364-codex-hook-batch-parity-004.md` — failed ignored-archive repair quarantined here.

## Owner Decisions / Input

No new owner decision is required. The active project authorization permits governed bridge evidence while retaining every independent gate. This proposal does not infer approval from stale `resolved` metadata and does not widen source/config/test authority.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5364; approved original proposal v001 and GO v002; current committed four-path evidence",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 and the governed numbered bridge chain",
  "primary_route": "python scripts/check_codex_hook_parity.py",
  "before_behavior": "The original governed implementation start failed before mutation, while later custodial commits left the intended behavior present but without a lawful independent terminal evidence chain.",
  "after_behavior": "A fresh report-only bridge cycle verifies the exact current committed behavior by reference without changing source, configuration, tests, hooks, or runtime state.",
  "self_descriptive_naming": "The recovery title, WI, exact evidence paths, hashes, test mapping, and target-only future report state the complete effect.",
  "obsolete_guidance_disposition": "The original packet-collision remediation is historical evidence; it is not treated as an instruction to reimplement already-present behavior.",
  "history_preservation": "All original and WI-5370 bridge files remain append-only; no historical artifact or implementation path is rewritten.",
  "baseline": {
    "current_head": "75decbfa704fe50288aecbc5669def329a0825df",
    "evidence_paths": 4,
    "focused_tests_passed": 14,
    "hook_parity": "PASS"
  },
  "expected_result": {
    "summary": "Truthful independent finalization evidence for the already-committed WI-5364 behavior.",
    "source_config_test_mutations": 0,
    "independent_verified_required": true
  },
  "rollback": {
    "instructions": "Use only an additive bridge correction; do not alter the four read-only evidence paths.",
    "verification": "Repeat exact hashes, scoped Git status, focused tests, checker, Ruff, and bridge preflights."
  },
  "hard_invariants": [
    "No handler is registered or executed twice.",
    "No hook command escapes the existing no-window batch topology.",
    "No forced role-profile override is reintroduced.",
    "No stale derived backlog state substitutes for independent VERIFIED."
  ],
  "fail_closed_conditions": [
    "Any evidence hash or scoped worktree state changes.",
    "Any focused test, checker, Ruff, claim, packet, or preflight gate fails.",
    "Any proposal or report expands beyond the single bridge-report target."
  ],
  "essential_context_preservation": "The approved hook-parity behavior, historical start failure, custodial-commit attribution limit, exact current evidence, and independent-verification requirement remain explicit."
}
```

## Specification-Derived Verification Plan

| Obligation | Read-only verification | Required result |
| --- | --- | --- |
| Live supported Codex hooks | Parse `.codex/config.toml`; run `python scripts/check_codex_hook_parity.py` | `hooks = true`; checker PASS |
| Batch-aware parity and omission denial | `python -m pytest platform_tests/scripts/test_codex_hook_parity.py -q --tb=short` | all collected tests pass |
| Dynamic role authority | Inspect dispatcher command construction and run relevant focused wrap-up/session-role tests named by the report-time repository | no `--role-profile`; tests pass |
| No-window/single-execution non-impairment | Run existing focused hook registration and no-window batch tests selected at report time | all selected tests pass; no duplicate route |
| Source quality | Ruff check and format check on the three Python evidence files | PASS |
| Candidate identity | SHA-256, Git blob, scoped status, and `git diff --check` on all four evidence paths | exact current identities; clean |
| Bridge/project authority | candidate/live applicability and clause preflights plus exact claim/packet readback | PASS; zero blocking gaps |

Current pre-proposal baseline: Codex hook parity PASS; 14 focused tests PASS; Ruff check PASS; Ruff format check PASS; exact four-path diff check PASS.

## Acceptance Criteria

1. Both historical WI-5364/WI-5370 chains remain append-only nonterminal evidence rather than false completion authority.
2. Current project/PAUTH, current open-or-terminal-truth WI state, and current bridge heads are revalidated at report time.
3. The four evidence paths remain clean and match the exact current hashes/blobs above.
4. Hooks remain enabled through the existing no-window declarative batch topology.
5. Every required governance/lifecycle handler remains reachable exactly once through a valid direct or batch route.
6. Missing, malformed, unreadable, or incomplete batch evidence fails parity closed.
7. The wrap-up dispatcher contains no forced role-profile override and relevant session-role tests pass.
8. Focused pytest, Ruff check, Ruff format check, and scoped diff checks pass with exact results disclosed.
9. Attribution is limited to the acceptance-mapped current behavior; no whole custodial commit or unrelated hunk is relabeled as WI-5364.
10. Only the declared future report path may be created after GO/start; no source, config, test, hook, dispatcher/TAFE, registry, database, Git, credential, release, deployment, cleanup, or external mutation occurs.
11. Independent Loyal Opposition VERIFIED is required before WI-5364 may be treated as truly resolved.

## Risk And Rollback

The primary risk is over-attributing broad custodial commits. Exact current identities, behavior-level test mapping, and explicit whole-commit exclusion contain it. A second risk is treating stale derived backlog state as terminal; live bridge status and independent review remain controlling.

Rollback is append-only. If any evidence drifts or independent review finds a gap, file a numbered correction; do not rewrite source/config/test files or bridge history.

## Recommended Commit Type

No source commit. A later independently verified bridge-only finalization may use the repository's governed bridge finalization convention.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
