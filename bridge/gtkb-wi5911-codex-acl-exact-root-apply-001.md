NEW
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
Document: gtkb-wi5911-codex-acl-exact-root-apply
Version: 001
Date: 2026-08-01 UTC
Project Authorization: PAUTH-PROJECT-GTKB-GOOSE-HARNESS-ADOPTION-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-GOOSE-HARNESS-ADOPTION
Work Item: WI-5911
Related Work Items: WI-5250, WI-5571

target_paths: ["scripts/repair_codex_dotdir_acl.ps1", "platform_tests/scripts/test_repair_codex_dotdir_acl.py", "platform_tests/scripts/test_codex_dotdir_acl_repair.py"]

implementation_scope: source and tests
requires_review: true
requires_verification: true
kb_mutation_in_scope: false
Recommended commit type: none

This proposal performs no KB, MemBase, or `groundtruth.db` mutation.

# WI-5911 — Exact-Root, Fingerprint-Preserving Codex ACL Apply

## Summary

Correct `scripts/repair_codex_dotdir_acl.ps1` so Apply performs only exact
root-rule removal against the `.codex` access-control list. It must preserve
the full non-target descriptor, owner, group, and inheritance-protection state;
must never normalize inheritance or synthesize allow rules; must perform no
descendant write; and must restore the complete original descriptor if
immediate readback violates any invariant.

No protected implementation is authorized by this proposal alone. Work may
start only after a fresh independent `GO`, an exact current claim, a schema-v3
implementation-start packet for all three declared paths, current overlap
clearance, and re-observation that the three target bytes remain clean or are
otherwise exactly attributed.

## Scope

The complete implementation cohort is the existing PowerShell helper plus its
two focused platform-test modules. The change is limited to root-rule
selection, descriptor preservation/proof, bounded rollback, compatible JSON
evidence, and deterministic tests. Live `.codex` metadata, dispatcher/TAFE,
the dispatch verifier, environment configuration, Git/index, and all other
source/test files are excluded.

## Defect Evidence

WI-5250 v001/v002 authorized removal of two exact root Deny rule objects with
complete non-target fingerprint equality, unchanged owner/protection, one
`Set-Acl`, and bounded rollback. During governed WI-5250 execution, source
inspection established that the helper's existing Apply path instead:

1. groups selected rules by identity;
2. calls `PurgeAccessRules` and re-adds preserved explicit rules;
3. unconditionally calls `Enable-AccessInheritance` through
   `icacls /inheritance:e` after a changed removal;
4. can add current-user or `CodexSandboxUsers` Modify allows; and
5. recursively enumerates descendants and applies repairs to them.

The live WI-5250 precondition happened to contain required allows and no risky
descendant rule, so no allow addition or descendant write was reported in that
operation. The inheritance command was still invoked, and the complete
original descriptor was not independently retained by the calling session.
WI-5250 v003 therefore truthfully records that its desired ACL state is
observed but complete nonimpairment is unprovable and terminal acceptance is
not claimed.

The current exact `.codex` post-state is stable: canonical Check reports 223
objects checked, zero risky Deny rules, zero errors, both required Modify
allows present, and `needs_repair=false`. This proposal changes helper behavior
and tests; it does not authorize another live `.codex` ACL mutation or a
no-window proof renewal.

## Current Target Baseline

All three declared targets are currently clean against Git and have these
fresh SHA-256 identities:

| Target | SHA-256 |
| --- | --- |
| `scripts/repair_codex_dotdir_acl.ps1` | `D104B292822C6CC2190F0599AFF559DA98CCD5B2F1886AC6782FFFEDFB16ED38` |
| `platform_tests/scripts/test_repair_codex_dotdir_acl.py` | `670AB079B540B1BA62487C3357BF50051C06E0DEA408484DF23B4F74940A2B06` |
| `platform_tests/scripts/test_codex_dotdir_acl_repair.py` | `56C4AEE8F293283A33F80712245FE815CA903C3CE3416988406495B6E32F1747` |

Any drift before implementation-start requires reclassification and a revised
proposal or exact hunk attribution. Foreign changes must be preserved.

## Exact Implementation Design

### 1. Preserve Check As Read-Only

Check mode may continue to inspect root and descendant ACLs for diagnostic
coverage, but it must not invoke `Set-Acl`, `icacls`, access-rule mutators, or
any other write path. Existing JSON compatibility fields remain available.
Additional evidence fields may be additive and closed-schema.

### 2. Root-Only Apply Preconditions

Apply must:

- resolve the project root and exact `.codex` target as it does today;
- read exact root `.codex` once for its authoritative preimage;
- require zero ACL-read errors;
- require both current-user and `CodexSandboxUsers` Modify allows already
  present, failing without mutation when either is absent;
- select only explicit root Deny rule objects satisfying the existing risky
  rule predicate;
- derive a stable fingerprint for every root ACE from resolved-or-raw SID,
  access-control type, numeric rights, inheritance flags, propagation flags,
  and inherited state; and
- capture full security-descriptor rollback bytes or an equivalent complete
  SDDL representation including owner, group, DACL, SACL where readable, and
  access-rule protection state.

Apply must not enumerate descendants as mutation candidates. A descendant
finding belongs to Check diagnostics and a separately governed repair, not to
this root-only writer.

### 3. Exact In-Memory Transformation

Create a new in-memory descriptor from the complete captured preimage. For
each selected exact rule object, call `RemoveAccessRuleSpecific` once. Do not
call `PurgeAccessRules`, `RemoveAccessRuleAll`, `SetAccessRule`,
`ResetAccessRule`, `AddAccessRule`, inheritance APIs, `icacls`, or identity-
wide reconstruction.

Before any write, prove mechanically that:

- every selected target fingerprint is absent exactly once;
- every non-target root fingerprint and its multiplicity are unchanged;
- no new fingerprint exists;
- owner, group, and access-rule protection state equal the preimage; and
- both required Modify allows remain present and unchanged.

Any mismatch fails closed with zero writes.

### 4. One Root Write And Immediate Proof

Apply the transformed descriptor exactly once with `Set-Acl -LiteralPath` on
the exact root `.codex` path. Immediately read back the root and require:

- all selected target fingerprints absent;
- complete multiset equality for non-target fingerprints;
- unchanged owner, group, and protection state;
- both required Modify allows unchanged;
- no descendant path written; and
- an exact write count of one.

Successful JSON must expose the target fingerprints, stable pre/post non-target
fingerprint digests and counts, owner/group/protection equality, required-allow
equality, root write count, descendant write count zero, and rollback status.

### 5. Bounded Rollback

If the root `Set-Acl` succeeds but readback violates any invariant, restore the
complete captured original descriptor once to exact root `.codex`, read it
back, and report whether full restoration was proven. A rollback failure must
remain a typed, visible failure and must not trigger retries, normalization,
descendant writes, dispatcher action, or speculative reconstruction.

## Test Design

`TEST-11829` is the linked integration contract. Tests must be deterministic
and must not mutate the repository's live `.codex` ACL.

| Requirement | Test evidence |
| --- | --- |
| Exact rule-object removal | A controlled temporary ACL fixture contains two selected explicit root Deny rules plus same-identity non-target allow/deny rules; only selected fingerprints disappear. |
| Full descriptor preservation | Before/after multisets, owner, group, and protection state remain exactly equal for every non-target property. |
| No broad APIs | Static/source contract rejects `PurgeAccessRules`, `Enable-AccessInheritance`, Apply-path `icacls`, and allow-synthesis calls. |
| Root-only behavior | A descendant fixture with independent ACL state remains byte/fingerprint identical; Apply reports `descendant_write_count=0`. |
| Missing allow fail-closed | Absence of either required Modify allow produces zero writes and a typed precondition failure. |
| Prewrite mismatch fail-closed | Injected transformation drift produces zero writes. |
| Readback mismatch rollback | Injected post-write drift causes one bounded restoration and proves the original complete descriptor restored. |
| Rollback failure visibility | Injected restoration failure is typed and does not retry or touch descendants. |
| Check nonmutation | Check runs against root/descendant fixtures with all write primitives instrumented to fail if invoked. |
| Regression compatibility | Existing focused helper and dispatch-verifier tests pass; ACL readiness truth remains separate from no-window proof currency. |

Where Windows ACL integration behavior cannot be exercised on a non-Windows
runner, static and mocked contract nodes must still run, and the Windows node
must have a deterministic skip reason rather than a false pass.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `SPEC-DISPATCHER-CONTROL-SURFACE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-STANDING-BACKLOG-001`

## Specification-Derived Verification

| Requirement | Required command/evidence | Acceptance |
| --- | --- | --- |
| `TEST-11829`; `GOV-HARNESS-ONBOARDING-CONTRACT-001` | `pytest platform_tests/scripts/test_repair_codex_dotdir_acl.py platform_tests/scripts/test_codex_dotdir_acl_repair.py --timeout=600` | Exact root-only transformation, preservation, rollback, and Check nonmutation nodes pass. |
| Source quality | `ruff check` and `ruff format --check` on both Python test targets | Zero findings. |
| PowerShell validity | Parse and execute Check against an isolated deterministic fixture; compile/parse under supported Windows PowerShell and PowerShell 7 where available | No syntax/runtime incompatibility; Check produces closed JSON and zero writes. |
| Nonimpairment | Instrument every writer plus full before/after descriptor comparison | One permitted root write on success; zero descendant/allow/inheritance writes; rollback exact on injected mismatch. |
| Dispatch boundary | `python scripts/verify_codex_dispatch.py --json` read-only after tests | Report ACL/static and no-window currency independently; do not renew or invoke a harness. |
| Governance | Fresh strict GO, exact claim, schema-v3 packet, applicability and clause gates, current collision scan | All pass before the first protected edit. |

## Requirement Sufficiency

Existing requirements sufficient. WI-5250 v001/v002 already state the exact
nonimpairment behavior, and WI-5911 / TEST-11829 isolate the helper defect and
mechanical regression proof. No new architecture or owner tradeoff is needed.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "behavioral_change": "replace broad ACL normalization with exact root rule-object removal",
  "root_write_count_on_success": 1,
  "descendant_write_count": 0,
  "allow_synthesis": false,
  "inheritance_mutation": false,
  "full_non_target_equality_required": true,
  "bounded_rollback_required": true,
  "dispatcher_or_tafe_mutation": false,
  "live_codex_acl_mutation_in_test": false
}
```

## Prior Deliberations

- `DELIB-20260801-WI5250-EXACT-IMPLEMENTATION-APPROVAL` approved the exact
  bounded WI-5250 root-rule correction whose execution exposed this helper
  mismatch.
- `DELIB-202666203` authorizes governed restoration of Codex A readiness while
  preserving bridge and dispatcher-state boundaries.
- `DELIB-202666274` is the owner decision behind the active list-free Goose
  project PAUTH.
- `bridge/gtkb-wi5250-codex-a-acl-strict-recovery-003.md` is the canonical
  nonterminal reconciliation evidence and explicitly delegates helper
  correction to WI-5911 / TEST-11829.
- WI-5571 / TEST-11622 separately retain ACL recurrence and durability
  ownership; this proposal does not duplicate them.

## Related Work Items

- `WI-5250` — live incident correction and nonterminal reconciliation.
- `WI-5571` — ACL recurrence causation/durability; not implemented here.
- `WI-5911` / `TEST-11829` — exact helper correction owned by this proposal.

## Owner Decisions / Input

No new owner decision is required. WI-5911 is an active member of
`PROJECT-GTKB-GOOSE-HARNESS-ADOPTION` and inherits the current project-level
approval under the owner's list-free authorization model. Legacy
`work_item.approval_state` is not operation-time authority. Independent GO,
claim, schema-v3 start, nonimpairment, and independent verification remain
mandatory.

## Explicit Exclusions

- No live `.codex` ACL mutation in this proposal or its tests.
- No dispatcher/TAFE configuration, activation, topology, routing, role,
  eligibility, lease, worker, provider, harness, or proof-renewal action.
- No descendant ACL write, recursive repair, inheritance normalization,
  identity-wide purge, allow synthesis, or unrelated ACL cleanup.
- No edits to `scripts/verify_codex_dispatch.py`, `.codex`, `.driveignore`,
  environment files, credentials, Git/index, foreign `.git/index.lock`,
  deployment, release, or external systems.
- No KB/MemBase mutation; no raw database or registry write.
- No adoption, overwrite, or cleanup of foreign worktree changes.

## Acceptance Criteria

1. Apply removes only exact selected root risky Deny rule objects.
2. Every non-target root ACE fingerprint and multiplicity remains equal.
3. Owner, group, inheritance-protection state, and required allows remain
   equal.
4. Success performs exactly one root `Set-Acl` and zero other ACL writes.
5. Apply never calls broad purge, allow-synthesis, inheritance, `icacls`, or
   descendant mutation paths.
6. Prewrite drift fails with zero writes; post-write drift triggers one bounded
   complete-descriptor rollback with explicit proof.
7. Check remains read-only and diagnostically compatible.
8. `TEST-11829` and the focused suite pass with deterministic evidence.
9. No excluded surface is mutated, and no live dispatchability is overstated.
10. Independent Loyal Opposition verification remains required before terminal
    acceptance.

## Risk And Rollback

ACL mutation is high consequence because broad identity or inheritance APIs
can silently change access outside the selected rules. The design minimizes
that risk with exact object selection, full descriptor evidence, one root
write, immediate readback, and a bounded complete-descriptor rollback. Source
rollback is a scoped revert of the three implementation targets; numbered
bridge artifacts remain append-only.

All proposal, test, and future implementation artifacts remain in-root under
`E:/GT-KB`; the governed numbered proposal will reside under
`E:/GT-KB/bridge/`.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
