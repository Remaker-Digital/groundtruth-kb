REVISED
author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f6d5c-2017-7d43-902e-b74483f50fff
author_model: GPT-5 Codex
author_model_version: gpt-5
author_model_configuration: Codex Desktop Prime Builder execution worker; user-bounded bridge-only NO-GO revisions

# Revised Project Authorization Remediation - Authority Foundations

bridge_kind: governance_advisory
Document: gtkb-authority-foundations-project-authorization
Version: 005
Responds to: bridge/gtkb-authority-foundations-project-authorization-004.md
Supersedes proposal: bridge/gtkb-authority-foundations-project-authorization-001.md
Date: 2026-07-15 UTC

Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS
Work Item: WI-5277
Related bootstrap defect: WI-5279
Related snapshot-integrity defect: WI-5283
target_paths: ["groundtruth.db"]

## Revision Response - Verified Bootstrap Lifecycle

Prime Builder accepts version 004 finding F1. The dependency is now closed by
`bridge/gtkb-wi5279-project-authorization-bootstrap-lifecycle-004.md`, latest
`VERIFIED`, and MemBase records `WI-5279` as resolved. This revision uses that
verified executable lifecycle; it does not rely on the earlier prose-only
exception path.

This proposal explicitly declares the `project_authorization_bootstrap` marker.
After a fresh independent GO, the exact bootstrap claim command is:

```powershell
python scripts/bridge_claim_cli.py claim-bootstrap gtkb-authority-foundations-project-authorization --owner-decision DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION --project PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS --work-item WI-5277 --authorization-id PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715 --carrier groundtruth.db --session-id $env:CODEX_THREAD_ID
```

The expected persisted `claim_kind` is exactly
`project_authorization_bootstrap`. Ordinary `claim` remains non-authoritative
for this governance-advisory thread.

With that claim held by the same Prime session, the exact implementation-start
command is:

```powershell
python scripts/implementation_authorization.py begin --bridge-id gtkb-authority-foundations-project-authorization --session-id $env:CODEX_THREAD_ID --expires-minutes 60
```

The required schema-v3 packet carries `bootstrap_authority.claim_kind`,
`owner_decision_id`, `project_id`, `work_item_id`, `bridge_id`,
`authorization_id`, `carrier_targets`, `consumed_at`,
`pre_start_packet_hash`, and the complete `work_intent_claim` evidence. The
packet hash binds the full canonical packet, including approved proposal,
exact target list, Prime session, claim evidence, and bootstrap authority; the
pre-start hash is added before final packet hashing. Any field drift, missing
field, wrong session, consumed claim, pre-start hash drift, proposal marker or
owner/authorization citation mismatch, or target other than `groundtruth.db`
fails closed before mutation.

Expected evaluator evidence for the sole carrier target is
`authorized: true` with operation-time reason code
`project_authorization_bootstrap_carrier`. Any other result is a stop condition;
no PAUTH transaction may run. The exact create/readback/revoke sequence and all
other metadata, specification links, quarantine boundaries, and verification
requirements below remain unchanged.

## Revision Claim

Prime Builder accepts all four version 002 findings. The owner has now granted
one explicit, single-use PAUTH remediation bootstrap for this exact bridge
thread. After a fresh independent GO, matching claim, and successful
implementation-start authorization, the bootstrap may perform only two
canonical metadata transactions against `groundtruth.db`:

1. create the exact owner-authorized Authority Foundations PAUTH bound to
   `DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION`; and
2. revoke the quarantined ungoverned
   `PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE`
   row.

The effect is bound by exact before/after canonical row readback and independent
verification. `groundtruth.db` must not be staged or committed. No quarantined
source, test, configuration, or other dirty work is adopted. The exception does
not make terminal governance advisories generally claimable and does not close
WI-5279's durable-bootstrap defect.

## Owner Decisions / Input

- `DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION` records Mike's
  exact project-level authorization, allowed work classes, retained per-slice
  gates, prohibited operations, and quarantine boundary.
- On 2026-07-15 Mike supplied the following explicit single-use bootstrap
  direction for this thread:

  > permit one single-use PAUTH remediation bootstrap for
  > gtkb-authority-foundations-project-authorization after independent GO,
  > limited to canonical groundtruth.db metadata transactions that create the
  > exact DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION PAUTH and
  > revoke the quarantined ...-PROJECT-SCOPE row; require exact before/after
  > readback and independent verification; do not stage or commit
  > groundtruth.db, adopt quarantined source changes, contact harnesses, mutate
  > dispatcher/runtime state, push, deploy, or release.

- This is a per-access exception only. It does not authorize a reusable bypass,
  direct database writes, direct harness contact, or dispatcher/TAFE mutation.

## Findings Addressed

### F1 - No executable non-bypass lifecycle for the first valid PAUTH

Addressed by the explicit owner exception above. This thread remains
`bridge_kind: governance_advisory`; the exception permits exactly one use of the
existing claim and implementation-start controls after independent GO. It does
not change source or make advisory GO generally implementation-claimable.

The claim and start packet must bind this slug, project, owner exception, exact
`groundtruth.db` target, and exact two canonical commands. Any mismatch or
failure ends the attempt without metadata mutation.

### F2 - Dirty shared binary has no focused commit baseline

Addressed by narrowing completion semantics. The owner explicitly prohibits
staging or committing `groundtruth.db` in this bootstrap. Exact row readback,
live sidecar-free `PRAGMA quick_check`, and byte hashes of the seven quarantined
candidate files provide the verification boundary. No clean-blob or focused
binary-commit claim is made.

WI-5283 remains open for the malformed committed snapshot and future
sidecar-free finalization gate. The bootstrap's bridge proposal/report/verdict
may be preserved as independently reviewed evidence, but the live database blob
is not part of a commit from this thread.

### F3 - Exact transaction omitted required linked specifications

Corrected. The exact `gt projects authorize` command below includes every
project-authorization, bridge, nonimpairment, worktree, and artifact-lifecycle
carrier listed in this revision. Empty work-item include/exclude lists preserve
project-level authorization semantics.

### F4 - Activation precedes operation-time enforcement substrate

Addressed only for the circular bootstrap. The owner exception permits creating
the project envelope before WI-5178 is terminal so WI-5178, WI-5277, WI-5279,
and related Authority Foundations repairs can enter their normal per-slice
bridge lifecycle. It does not adopt or authorize any pre-existing dirty hunk.

After activation, every protected slice still requires exact project
membership, exact target paths, independent GO, matching claim, successful
implementation-start authorization, spec-derived tests, independent
verification, and the separately applicable focused-commit gate.

## Exact New PAUTH Envelope

```toml
id = "PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715"
authorization_name = "Authority Foundations project implementation authorization"
project_id = "PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS"
owner_decision_deliberation_id = "DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION"
scope_summary = "Authorize governed Authority Foundations project work under the approved charter. Each protected slice still requires exact project membership, an independent bridge GO, exact target paths, a matching claim, successful implementation-start authorization, executed tests, independent verification, and a separately authorized focused commit. Existing pre-authorization dirty work remains quarantined candidate evidence. Direct harness contact, dispatcher or runtime mutation, credentials, destructive cleanup, unrelated mutation, push, deployment, and release are excluded."
allowed_mutation_classes = ["bridge", "metadata", "source", "test", "configuration", "formal_artifact", "governance_evidence"]
forbidden_operations = ["credential_lifecycle", "destructive_cleanup", "dispatcher_mutation", "dispatcher_configuration", "tafe_mutation", "harness_mutation", "harness_eligibility_mutation", "role_mutation", "manual_routing", "direct_harness_contact", "external_system_mutation", "raw_database_mutation", "git_history_rewrite", "git_push", "production_deployment", "release"]
included_work_item_ids = []
excluded_work_item_ids = []
included_spec_ids = [
  "GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001",
  "GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001",
  "DCL-PROJECT-AUTHORIZATION-ENVELOPE-001",
  "DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001",
  "PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001",
  "GOV-FILE-BRIDGE-AUTHORITY-001",
  "DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001",
  "DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001",
  "DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001",
  "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001",
  "GOV-WORK-TREE-HYGIENE-001",
  "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001",
  "ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001",
  "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001"
]
excluded_spec_ids = []
expires_at = null
plan_incomplete = true
```

`formal_artifact` and `governance_evidence` are listed separately because the
owner explicitly authorized both classes. Focused Git commit is deliberately
not inferred from these classes; each later commit remains governed by its own
mechanical gate.

## Exact Canonical Transactions

After independent GO, exact claim, and implementation-start authorization,
execute the create command as one invocation:

```text
gt projects authorize PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS --id PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715 --owner-decision DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION --name "Authority Foundations project implementation authorization" --scope "Authorize governed Authority Foundations project work under the approved charter. Each protected slice still requires exact project membership, an independent bridge GO, exact target paths, a matching claim, successful implementation-start authorization, executed tests, independent verification, and a separately authorized focused commit. Existing pre-authorization dirty work remains quarantined candidate evidence. Direct harness contact, dispatcher or runtime mutation, credentials, destructive cleanup, unrelated mutation, push, deployment, and release are excluded." --allowed-mutation bridge --allowed-mutation metadata --allowed-mutation source --allowed-mutation test --allowed-mutation configuration --allowed-mutation formal_artifact --allowed-mutation governance_evidence --forbid credential_lifecycle --forbid destructive_cleanup --forbid dispatcher_mutation --forbid dispatcher_configuration --forbid tafe_mutation --forbid harness_mutation --forbid harness_eligibility_mutation --forbid role_mutation --forbid manual_routing --forbid direct_harness_contact --forbid external_system_mutation --forbid raw_database_mutation --forbid git_history_rewrite --forbid git_push --forbid production_deployment --forbid release --include-spec GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 --include-spec GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001 --include-spec DCL-PROJECT-AUTHORIZATION-ENVELOPE-001 --include-spec DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001 --include-spec PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001 --include-spec GOV-FILE-BRIDGE-AUTHORITY-001 --include-spec DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001 --include-spec DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 --include-spec DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 --include-spec GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001 --include-spec GOV-WORK-TREE-HYGIENE-001 --include-spec GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 --include-spec ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 --include-spec DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 --plan-incomplete --changed-by prime-builder/codex/A --change-reason "Single-use bootstrap remediation authorized by Mike on 2026-07-15 after independent GO; exact envelope DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION." --json
```

Only after exact create readback passes, execute:

```text
gt projects revoke-authorization PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-AUTHORITY-FOUNDATIONS-20260715-PROJECT-SCOPE --changed-by prime-builder/codex/A --change-reason "Revoke quarantined ungoverned Authority Foundations PAUTH after exact owner-authorized replacement was created and read back under the single-use bootstrap remediation." --json
```

No raw SQL, SQLite writer, file copy, WAL/SHM manipulation, binary overwrite,
staging, or commit is authorized.

## Exact Before/After Binding

Before mutation, capture and retain:

1. canonical JSON readback showing the exact new PAUTH ID is absent;
2. canonical JSON readback of the quarantined row at version 1/status active;
3. canonical JSON readback of the exact owner deliberation;
4. the project's active authorization list and completion guards;
5. read-only `PRAGMA quick_check` on the live database;
6. SHA-256 for all seven quarantined candidate files; and
7. `git status --short -- groundtruth.db` showing the pre-existing dirty blob.

After mutation, require:

1. the exact new PAUTH exists once at version 1/status active;
2. project ID, owner decision, name, scope, allowed classes, forbidden
   operations, linked specifications, empty WI filters, and null expiry exactly
   match this revision;
3. the quarantined PAUTH current version is revoked;
4. the live database still passes read-only `PRAGMA quick_check`;
5. all seven candidate hashes are byte-identical;
6. no dispatcher, harness, TAFE, bridge runtime, lease, config, Git index,
   commit, push, deployment, or release state changed; and
7. the single-use claim is released or allowed to expire after report filing.

The quarantined row's existing plan-incomplete guard may remain because current
revocation does not atomically deactivate it. That separate defect is already
tracked by WI-5188. The stale guard grants no implementation authority and must
be reported explicitly; this bootstrap does not mutate it outside the owner's
two authorized transactions.

## Quarantined Candidate Evidence

The following files remain evidence only and must be byte-identical before and
after the metadata transaction:

- `config/governance/project-authorization-operation-taxonomy.toml`
- `groundtruth-kb/src/groundtruth_kb/governance/project_authorization_operation_time.py`
- `groundtruth-kb/tests/test_project_authorization_operation_time_enforcement.py`
- `scripts/implementation_authorization.py`
- `scripts/bridge_work_intent_registry.py`
- `platform_tests/scripts/test_implementation_authorization.py`
- `platform_tests/scripts/test_bridge_work_intent_registry.py`

No current hunk in those files is approved, adopted, reported, verified, staged,
or committed by this thread.

## Specification Links

- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `GOV-PROJECT-REQUIRES-LINKED-SPECIFICATIONS-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Prior Deliberations

- `DELIB-20260715-AUTHORITY-FOUNDATIONS-PROJECT-AUTHORIZATION` - exact owner project envelope and quarantine boundary.
- Owner message dated 2026-07-15 - exact single-use bootstrap remediation exception quoted above.
- `DELIB-20260710-GTKB-MODERNIZATION-AUTHORITY-FOUNDATIONS-CHARTER` - approved project charter.
- `DELIB-20260710-GTKB-PLATFORM-MODERNIZATION-PARENT-CHARTER` - parent project boundary.
- `bridge/gtkb-authority-foundations-project-authorization-001.md` - original activation proposal.
- `bridge/gtkb-authority-foundations-project-authorization-002.md` - controlling NO-GO findings addressed here.
- WI-5279 - durable reusable bootstrap lifecycle remains open.
- WI-5188 - stale completion-guard revocation remains open.
- WI-5283 - malformed committed MemBase snapshot/finalization gate remains open.

## Specification-Derived Verification Plan

| Requirement | Verification |
| --- | --- |
| Exact owner/project binding | Canonical readback matches the exact ID, project, DELIB, name, and scope. |
| Project-level semantics | New PAUTH has empty WI include/exclude arrays and applies only through active project membership. |
| Linked specifications | Canonical readback contains exactly the 14 listed governing specifications. |
| Mutation/forbidden envelope | Canonical readback exactly matches the seven allowed classes and 16 forbidden operation IDs. |
| Single-use non-bypass lifecycle | Independent GO, matching claim, and implementation-start packet precede both canonical commands. |
| Quarantined row removal | Current readback for `...-PROJECT-SCOPE` is revoked only after exact replacement readback passes. |
| Shared database integrity | Live read-only `PRAGMA quick_check` returns `ok` before and after; database is neither staged nor committed. |
| Quarantine preservation | Seven candidate SHA-256 values are identical before and after. |
| Runtime isolation | Read-only dispatcher status before/after shows no mutation; no worker, lease, config, eligibility, or role operation is invoked. |
| Independent completion | NEW implementation report carries exact outputs and receives independent VERIFIED before the PAUTH is counted as governed evidence. |

## Acceptance Criteria

1. A fresh independent GO explicitly approves this single-use exception and
   exact two-command transaction.
2. Matching claim and implementation-start authorization pass before mutation.
3. The exact new PAUTH exists once, version 1, active, and matches every field
   in this revision.
4. The quarantined `...-PROJECT-SCOPE` row is revoked after replacement
   readback succeeds.
5. The live database passes integrity before and after and is not staged or
   committed.
6. All seven quarantined files remain byte-identical and unadopted.
7. No direct harness contact, source/test/config mutation, dispatcher/TAFE or
   runtime mutation, credentials, destructive cleanup, unrelated mutation,
   push, deployment, or release occurs.
8. Independent verification confirms the exact readback. WI-5279, WI-5188,
   and WI-5283 remain open for their durable systemic repairs.

## Risk / Rollback

The transaction changes shared live metadata while the tracked database blob
is already dirty. The owner has accepted a row-readback verification boundary
and prohibited binary staging/commit. Create must succeed and be read back
exactly before revocation begins. If create fails or readback differs, stop and
leave the quarantined row active. If revocation fails after exact creation,
report both active rows and obtain a new governed remediation; do not retry by
raw SQL.

Rollback of the exact new PAUTH requires a separately governed canonical
revocation. Append-only owner, PAUTH, bridge, report, verdict, and guard evidence
remains preserved.

## Requested Loyal Opposition Disposition

- `GO` authorizes only the single-use lifecycle and exact two canonical
  metadata commands after claim/start authorization.
- `NO-GO` must identify any remaining mismatch in owner evidence, exact
  envelope, command vocabulary, before/after binding, quarantine, or isolation.
- No source implementation or live harness proof is authorized here.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
