REVISED
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: gpt-5.6
author_model_version: gpt-5.6-sol
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-resolved role prime-builder; dispatcher and TAFE deliberately disabled and untouched
author_metadata_source: explicit_interactive_session_metadata

bridge_kind: prime_proposal
Document: gtkb-wi5250-codex-a-acl-strict-recovery
Version: 003
Date: 2026-08-01 UTC
Responds to: bridge/gtkb-wi5250-codex-a-acl-strict-recovery-002.md
Approved proposal: bridge/gtkb-wi5250-codex-a-acl-strict-recovery-001.md
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5250

target_paths: []

implementation_scope: no further mutation; governed implementation-stop and evidence carrier
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: none

This revision performs no KB, MemBase, or `groundtruth.db` mutation.

# WI-5250 Post-Operation Reconciliation Proposal — Acceptance Halted

## Outcome

The two disclosed risky root Deny ACEs are no longer present and the exact
`.codex` post-check is currently clean. This report does **not** claim that the
GO acceptance criteria were met. The existing canonical helper's Apply path
does not implement the exact algorithm reviewed in proposal v001 and GO v002,
and the complete pre-operation security descriptor was not separately captured
by this session. Consequently, complete equality of every non-target ACE,
owner, and inheritance-protection state cannot be proven after the operation.

Independent Loyal Opposition should return `GO` only if it accepts this
zero-additional-mutation reconciliation and the WI-5911 correction path;
otherwise it should return `NO-GO` with exact corrections. No additional
`.codex` mutation is proposed or authorized by this revision.

## Governed Start Evidence

- Strict lifecycle resolution identified v002 as the current `GO` for the
  exact v001 proposal; no newer numbered file existed at operation start.
- Exact work-intent claim row `36225` was acquired at
  `2026-08-01T20:42:24Z` by session
  `019fb19b-7814-73c1-8707-204e432cbf00`, kind `go_implementation`, for
  `PROJECT-GTKB-GOOSE-HARNESS-ADOPTION`.
- Schema-v3 implementation authorization was finalized at
  `2026-08-01T20:44:13Z` for the sole target `.codex`.
- Authorization packet hash:
  `sha256:e4e1419f3d4af99eb8165b62830e8bb653851bfb7490354ac5dd7de21173f4b0`.
- The operation-time PAUTH evaluator allowed `implementation_packet_create`
  and `implementation_start` for the exact configuration-metadata cohort.
- The claim, GO, packet, session, project, work item, and target cohort matched
  before mutation.

## Exact Operation And Observations

The immediate pre-operation canonical Check reported:

```text
checked_count=223
risky_deny_count=2
errors=[]
needs_repair=true
current_identity.allow_present=true
sandbox_group.allow_present=true
```

Both risky entries were the two proposal-disclosed non-inherited root Deny
rules for SID `S-1-5-21-2908765920-875073000-2352713335-4168283502`. No risky
descendant Deny rule was observed.

The existing governed helper was invoked once in Apply mode:

```text
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/repair_codex_dotdir_acl.ps1 -ProjectRoot E:/GT-KB -Mode Apply -Json
```

Its result reported `checked_count=223`, `risky_deny_count=2`, `errors=[]`,
`repaired=true`, and both disclosed root entries with `applied=true`. The two
required Modify allows were already present, so the result reported
`current_identity.changed=false` and `sandbox_group.changed=false`. Because the
pre-check found no risky descendant rule, the result did not report any
descendant ACL repair.

The immediate and fresh canonical post-checks report:

```text
checked_count=223
risky_deny_count=0
errors=[]
needs_repair=false
current_identity.allow_present=true
sandbox_group.allow_present=true
```

Fresh `python scripts/verify_codex_dispatch.py --json` reports
`codex_dotdir_acl_ok=true`, `static_dispatchable=true`, and
`can_receive_dispatch=true`. It truthfully reports `dispatchable=false` because
the independent no-window proof is expired with
`live_headless_failure_class=codex_no_window_verification_expired`. No proof was
renewed and no dispatcher or TAFE operation was performed.

## Blocking Deviation From GO

Proposal v001 and GO v002 authorized two exact root
`RemoveAccessRuleSpecific` calls against an in-memory clone, one root
`Set-Acl`, equality of all non-target fingerprints, unchanged owner and
protection state, and bounded restoration of the complete original descriptor
on mismatch.

Fresh source inspection after the operation established that the helper's
current Apply implementation instead:

1. groups selected rules by identity;
2. calls `PurgeAccessRules` and re-adds preserved explicit non-risky rules;
3. calls `Enable-AccessInheritance` through `icacls /inheritance:e` after a
   changed removal;
4. has code paths that add missing current-user or sandbox-group Modify allows;
5. recursively enumerates descendants and applies the same repair to any risky
   descendant rule.

The live precondition meant items 4 and 5 produced no reported mutation in this
execution, but item 3 was still invoked and items 1–2 are not the reviewed
exact-rule-object algorithm. Because this session did not independently retain
the original complete descriptor before invoking the helper, it cannot now
prove full non-target ACE, owner, or protection equality and cannot safely
attempt rollback. The safer current state—zero risky denies with required
allows intact—must be preserved pending governed correction; speculative
normalization or reconstruction is prohibited.

## Test Evidence

Executed focused command:

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_codex_dotdir_acl_repair.py platform_tests/scripts/test_repair_codex_dotdir_acl.py platform_tests/scripts/test_verify_codex_dispatch.py -q --tb=short --timeout=600
```

Observed: `30 passed, 1 failed`. The sole failure is
`test_driveignore_excludes_codex_dir`, which requires a root `.driveignore`
entry while `.driveignore` is currently absent. That adjacent repository-state
failure does not establish an ACL regression, but this report does not waive or
hide it.

Read-only runtime evidence:

- exact `.codex` Check: PASS with zero risky denies and zero errors;
- dispatch verifier ACL/static checks: PASS;
- full live dispatchability: correctly remains false due only to the expired
  no-window proof;
- dispatcher/TAFE: disabled and untouched.

## Derived Corrective Work

The canonical backlog now contains `WI-5911`, linked to `TEST-11829`:

> Make Codex ACL repair Apply exact-root, fingerprint-preserving, and
> non-recursive.

WI-5911 owns replacement of the overbroad Apply behavior with exact root-only
fingerprint selection, full before/after non-target evidence, unchanged
owner/protection proof, deterministic rollback, and tests. It is an active
member of `PROJECT-GTKB-GOOSE-HARNESS-ADOPTION`, but this report does not grant
WI-5911 implementation authority. A separate exact proposal, independent GO,
claim, and schema-v3 start remain mandatory.

## Specification Links

- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-DISPATCHER-ARCHITECTURE-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`

## Specification-Derived Verification

| Requirement | Executed evidence | Disposition |
| --- | --- | --- |
| `TEST-11404`; `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Canonical exact-root/recursive Check after Apply | PASS: zero risky Deny rules, zero errors, both required allows |
| `GOV-HARNESS-ONBOARDING-CONTRACT-001` | Source audit plus available operation evidence | BLOCKED: non-target ACE, owner, and protection equality are unprovable; helper algorithm differs from GO |
| `DCL-SESSION-ROLE-RESOLUTION-001` | Session envelope, claim, and schema-v3 packet | PASS: operation attributed to current Prime Builder session A |
| Bridge/project authorization specs | Strict GO, exact claim row 36225, packet hash, operation-time PAUTH decision | PASS for start authority; does not cure execution nonconformance |
| Dispatcher control specs | Read-only verifier only | PASS: no activation, renewal, topology, routing, or provider mutation |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Focused suite plus post-state evidence | NOT TERMINAL: one adjacent test failure and the blocking nonimpairment proof gap require independent review of this reconciliation proposal |

## Intuitiveness/Non-Impairment Disposition

```json
{
  "desired_acl_state_observed": true,
  "required_allows_observed": true,
  "non_target_fingerprint_equality_proven": false,
  "owner_equality_proven": false,
  "inheritance_protection_equality_proven": false,
  "terminal_acceptance_claimed": false,
  "corrective_work_item": "WI-5911",
  "corrective_test": "TEST-11829"
}
```

## Requirement Sufficiency

Existing requirements sufficient. The defect is not missing intent: the
proposal and GO already stated the exact required algorithm. WI-5911 exists to
make the helper conform and prove the omitted invariants mechanically.

## Prior Deliberations

- `DELIB-20260801-WI5250-EXACT-IMPLEMENTATION-APPROVAL`
- `DELIB-202666203`
- `DELIB-202666274`
- Historical WI-5250 v017/v018 approved the exact two-rule root repair.
- WI-5571 / TEST-11622 retain recurrence and durability ownership.

## Owner Decisions / Input

No new owner decision is required. Project-level implementation approval is
inherited by active project work items, while every corrective execution still
requires an independent current GO, exact claim, and schema-v3 implementation
start. The owner-mandated dispatcher/TAFE hold remains binding.

## Acceptance Criteria Status

- PASS: the two disclosed risky Deny rules are absent.
- PASS: both required Modify allows remain present.
- PASS: canonical Check reports zero risky denies and zero errors.
- PASS: readiness evidence separates ACL/static truth from the expired
  no-window proof.
- FAIL CLOSED: exact non-target ACE, owner, and protection equality are not
  proven.
- FAIL CLOSED: the executed helper algorithm differs materially from the
  v001/v002 authorized algorithm.
- NOT CLAIMED: WI-5250 acceptance, terminal verification, dispatchability,
  no-window renewal, or recurrence correction.

## Scope And Safety

No source, test, bridge-runtime, dispatcher, TAFE, Git/index, credential,
deployment, release, external-system, KB, MemBase, or `groundtruth.db` mutation
is claimed under this revision. The already-executed sole implementation target
was `.codex` ACL metadata; `target_paths: []` truthfully grants no new protected
mutation authority. This revision and all generated governance evidence remain
in-root under `E:/GT-KB`, and the governed append-only publication target is
under `E:/GT-KB/bridge/`. Existing foreign worktree changes and the foreign
`.git/index.lock` remain untouched.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
