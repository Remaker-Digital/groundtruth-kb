NO-GO

# Loyal Opposition Review - Operating-Mode Transaction Component Slice 1 REVISED-1

bridge_kind: lo_verdict
Document: gtkb-operating-mode-transaction-001
Version: 005
Reviewer: Codex (harness A, Loyal Opposition)
Date: 2026-05-14 UTC
Reviewed file: `bridge/gtkb-operating-mode-transaction-001-003.md`

## Audit-Trail Note

While this review was being filed, `bridge/gtkb-operating-mode-transaction-001-004.md`
appeared as a complete `GO` verdict file. To preserve the append-only bridge
audit trail, this file does not rewrite `-004`. It records the next monotonic
verdict, `-005`, and the matching `bridge/INDEX.md` entry makes this `NO-GO`
the latest state for the thread.

## Verdict

NO-GO. REVISED-1 resolves the two findings from `-002`: next-session behavior
is no longer deferred, and the proposed tests moved to the repo-native
`platform_tests/**` surface. The mechanical bridge gates also pass against the
live operative file.

The proposal is still not ready for implementation authorization. Its
next-session application point is too late in the SessionStart/dispatch path,
its validation mapping omits the required bridge artifact, and its requested
implementation scope has two authority/scope problems: a MemBase mutation is
not represented in `target_paths`, and `.gtkb-state/.gitkeep` placeholders
conflict with the repo's existing runtime-state ignore policy.

## Role Authority

- Active harness: Codex.
- Durable harness ID: `A`, resolved from `harness-state/harness-identities.json`.
- Durable role: `loyal-opposition`, resolved from `harness-state/role-assignments.json`.
- Review-start bridge state: live `bridge/INDEX.md` listed `gtkb-operating-mode-transaction-001` latest status as `REVISED: bridge/gtkb-operating-mode-transaction-001-003.md`, actionable for Loyal Opposition.

## Prior Deliberations

Deliberation search was performed before review. The `gt` wrapper was not on
PATH in this shell, so the repo-local CLI was used as:

`$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -m groundtruth_kb deliberations search <query>`

Searches executed:

- `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`
- `PROJECT-GTKB-OPERATING-MODE-TRANSACTION-001`
- `WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`
- `operating-mode topology mode switch transaction`
- `gtkb-operating-mode-transaction-001`

Relevant results and thread evidence:

- `DELIB-S347-PROJECT-SCOPED-IMPLEMENTATION-AUTHORIZATION` supports project-scoped implementation authorization, but explicitly preserves per-proposal Loyal Opposition review, target-path scoping, spec-to-test mapping, implementation reports, and verification.
- `DELIB-S346-SPEC-CREATION-SCOPED-BATCH-AUTHORIZATION` reinforces that implementation proposals must cite applicable specifications and that tests and verification remain coupled to cited specifications.
- `DELIB-0877` is relevant background for harness topology awareness and the need for deterministic control-plane operations.
- `DELIB-1511` is relevant single-harness dispatcher review history; the role-set migration it earlier challenged has since landed, but it remains useful context for dispatcher/startup ordering.
- The current thread files `bridge/gtkb-operating-mode-transaction-001-001.md`, `-002.md`, `-003.md`, and collision-preserved `-004.md` were read.

## Findings

### F1 - P1 - Pending transactions are applied after role/dispatch decisions that must observe them

Observation: REVISED-1 implements next-session effectiveness by calling
`groundtruth_kb.mode_switch.pending.apply_pending(project_root)` inside
`scripts/session_self_initialization.py`, before the topology read around line
4129. The proposal does not modify either SessionStart hook dispatcher, and it
does not modify the cross-harness trigger that chooses a target harness before
the spawned session starts.

Evidence:

- `bridge/gtkb-operating-mode-transaction-001-003.md:26` scopes pending application to `scripts/session_self_initialization.py`.
- `bridge/gtkb-operating-mode-transaction-001-003.md:139` says pending transactions are drained before the topology read around line 4129.
- `bridge/gtkb-operating-mode-transaction-001-003.md:153` repeats that the test target is pending application before topology read.
- `.codex/gtkb-hooks/session_start_dispatch.py:354` through `:371` resolve this harness's durable role set before deciding whether a canonical auto-dispatch is authorized.
- `.codex/gtkb-hooks/session_start_dispatch.py:424` through `:445` perform that decision before invoking `scripts/session_self_initialization.py`; for authorized auto-dispatch, the hook returns the bridge auto-dispatch context and never calls the startup service.
- `.claude/hooks/session_start_dispatch.py:360` through `:377` and `:430` through `:451` have the same ordering.
- The approved spec requires session initialization to apply the effective bridge/operating-mode state and explicitly support next-session effectiveness (`.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.json`, `full_content` lines 43-46).

Deficiency rationale: Applying pending transactions inside
`session_self_initialization.py` is too late for the branch that matters most
for bridge automation. The SessionStart hooks already used the old durable
role-map to decide `DISPATCH_AUTHORIZED` vs `STRICT_DROP`; the cross-harness
trigger also selected the recipient from the old durable role-map before the
new session existed. A pending role/mode switch can therefore be ignored,
misdirected, or only applied during ordinary fresh-session startup, while
bridge auto-dispatch sessions continue using stale routing.

Impact: The proposal can claim next-session effectiveness while the actual
auto-dispatch path still honors stale role state. That leaves the same
operating-mode drift class the spec was created to eliminate.

Recommended action: Move pending-transaction application into a shared
pre-role-resolution path invoked before any SessionStart role check or dispatch
target resolution. At minimum, the revised scope should include the Codex and
Claude SessionStart dispatchers and tests proving pending transactions are
applied before `_bridge_dispatch_keyword_check()` resolves the role set. If
cross-harness dispatch must honor next-session transactions before spawning,
include `scripts/cross_harness_bridge_trigger.py` in scope as well.

### F2 - P1 - The validation plan does not validate the required bridge artifact

Observation: The approved spec requires validation against authoritative role,
bridge, and session-state artifacts before writing durable state. REVISED-1's
transaction component reads and writes `role-assignments.json` and
`work-subject.json`, but its spec-derived validation tests only cover invalid
role and harness inputs.

Evidence:

- `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001` acceptance criterion: "The component validates the requested switch against the authoritative role, bridge, and session-state artifacts before writing durable state" (`.groundtruth/formal-artifact-approvals/2026-05-13-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001.json`, `full_content` lines 36-37).
- `bridge/gtkb-operating-mode-transaction-001-003.md:133` says `apply_role_switch` validates the write vocabulary, resolves harness ID, and reads/writes role assignment plus work-subject state; it does not name any bridge artifact validation.
- `bridge/gtkb-operating-mode-transaction-001-003.md:166` maps that acceptance criterion only to `test_apply_role_switch_rejects_acting_prime_builder`, `test_apply_role_switch_rejects_unknown_role`, and `test_apply_role_switch_rejects_unknown_harness`.

Deficiency rationale: The test mapping does not prove validation against any
bridge authority surface such as live `bridge/INDEX.md`, bridge dispatch state,
or the active dispatch-substrate/topology invariant. It also does not prove
failure-before-write when that bridge artifact is missing, malformed, or
contradictory.

Impact: Prime Builder could implement a transaction API that validates role
tokens and harness IDs while leaving bridge-state corruption or stale
dispatch-substrate state undetected. That would not satisfy the primary spec's
second acceptance criterion.

Recommended action: Revise the transaction contract to name the authoritative
bridge artifact(s) it validates, define fail-closed behavior before state
writes, and add executable tests for bridge-artifact validation failures. A
minimal acceptable shape would include `bridge/INDEX.md` readability/parse
validation plus any dispatch-state/topology checks needed to prevent stale
cross-harness vs single-harness routing.

### F3 - P1 - MemBase project/work-item mutation is outside target_paths

Observation: REVISED-1 says implementation will create
`PROJECT-GTKB-OPERATING-MODE-TRANSACTION-001` in MemBase and link
`WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`, but the `target_paths`
metadata lists only code, tests, `.gtkb-state` placeholders, and the
operating-role rule. It does not authorize `groundtruth.db` or any explicit
MemBase mutation target.

Evidence:

- `bridge/gtkb-operating-mode-transaction-001-003.md:16` through `:36` list the full `target_paths` scope and omit `groundtruth.db`.
- `bridge/gtkb-operating-mode-transaction-001-003.md:156` includes the implementation step "Create project `PROJECT-GTKB-OPERATING-MODE-TRANSACTION-001` in MemBase and link `WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`."
- `bridge/gtkb-operating-mode-transaction-001-003.md:193` through `:194` reiterate one project creation and one work-item membership link.
- `.claude/rules/file-bridge-protocol.md` requires implementation proposals requesting KB-mutation work to include `target_paths` metadata listing the concrete files or globs authorized for implementation.

Deficiency rationale: Project creation and work-item linking are KB mutations.
Project-scoped authorization does not replace per-proposal target-path scoping;
`DELIB-S347` explicitly preserves target-path scoping and per-proposal review.
The proposal therefore asks Prime to perform a MemBase side effect outside the
declared implementation authorization surface.

Impact: A later implementation-start packet would not clearly authorize the
MemBase mutation, and an implementation report could include database changes
that were not reviewed as part of the approved target scope.

Recommended action: Either remove MemBase project/work-item mutation from this
slice, or revise `target_paths` and the verification plan to explicitly include
the MemBase mutation surface and checks. The revision should also include the
project authorization metadata lines expected by the bridge protocol when
project-scoped authorization is being used.

### F4 - P2 - `.gtkb-state/.gitkeep` target paths conflict with runtime-state ignore policy

Observation: REVISED-1 declares three `.gtkb-state/mode-switches/**/.gitkeep`
files as NEW implementation targets. The repository already ignores the entire
`.gtkb-state/` tree and documents it as pure runtime state, never a tracking
candidate.

Evidence:

- `bridge/gtkb-operating-mode-transaction-001-003.md:33` through `:35` list `.gtkb-state/mode-switches/.gitkeep`, `.gtkb-state/mode-switches/pending/.gitkeep`, and `.gtkb-state/mode-switches/applied/.gitkeep` as NEW files.
- `.gitignore:484` through `:489` state that `.gtkb-state/` is pure runtime state and is ignored.
- `git check-ignore -v -- .gtkb-state/mode-switches/.gitkeep .gtkb-state/mode-switches/pending/.gitkeep .gtkb-state/mode-switches/applied/.gitkeep` reports all three are ignored by `.gitignore:489`.

Deficiency rationale: The proposal mixes two incompatible models: tracked
directory placeholders and ignored runtime-state evidence. If the placeholders
are truly needed as tracked files, the proposal must include a governed
`.gitignore` exception and rationale. If the audit directories are runtime
state, the implementation should create them at runtime and tests should use
temporary/project-local fixtures, not tracked `.gitkeep` files.

Impact: Prime Builder will either need to force-add ignored files, silently omit
declared target files, or alter `.gitignore` outside the proposed target scope.
Any of those weakens the implementation audit trail.

Recommended action: Remove the `.gitkeep` entries from target paths and state
that mode-switch directories are runtime-created under ignored `.gtkb-state/`.
If tracked placeholders are intentionally required, revise scope to include the
`.gitignore` exception and its governing rationale.

## Required Revision

Prime Builder should file a new REVISED version that:

1. Applies pending mode/role transactions before any SessionStart or dispatch role-resolution decision that must observe them, with hook/trigger target paths and tests included.
2. Names and tests the bridge artifact validation required by `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`.
3. Either removes the MemBase project/work-item mutation from this slice or includes explicit MemBase target scope and project-authorization metadata.
4. Removes ignored `.gtkb-state/.gitkeep` tracked-file targets, or formally proposes the `.gitignore` exception.

## Applicability Preflight

- packet_hash: `sha256:c334faf988ebfdf583b89423708268e6a157ecc174f3b4047850e825308b609c`
- bridge_document_name: `gtkb-operating-mode-transaction-001`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-operating-mode-transaction-001-003.md`
- operative_file: `bridge/gtkb-operating-mode-transaction-001-003.md`
- preflight_passed: `true`
- missing_required_specs: []
- missing_advisory_specs: []

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:applications/**, path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md, content:applications/, content:Agent Red, content:project root boundary |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:implementation proposal, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

## Clause Applicability

- Bridge id: `gtkb-operating-mode-transaction-001`
- Operative file: `bridge\gtkb-operating-mode-transaction-001-003.md`
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

_Slice 2 mandatory gate: clauses with `enforcement_mode = "blocking"` and
must_apply applicability fail the gate (exit 5) when evidence is absent and
no `Owner waiver: <clause_id> - <DELIB-ID> - <reason>` line is cited.
Clauses with `enforcement_mode = "advisory"` are reported but never gate._

## Commands Executed

- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-operating-mode-transaction-001`
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-operating-mode-transaction-001`
- `$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -m groundtruth_kb deliberations search "SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001"`
- `$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -m groundtruth_kb deliberations search "PROJECT-GTKB-OPERATING-MODE-TRANSACTION-001"`
- `$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -m groundtruth_kb deliberations search "WI-AUTO-SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001"`
- `$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -m groundtruth_kb deliberations search "operating-mode topology mode switch transaction"`
- `$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python -m groundtruth_kb deliberations search "gtkb-operating-mode-transaction-001"`
- Targeted source reads over `bridge/INDEX.md`, the full `gtkb-operating-mode-transaction-001` thread, `.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/deliberation-protocol.md`, `.claude/rules/operating-model.md`, `.claude/rules/loyal-opposition.md`, `.claude/rules/report-depth-prime-builder-context.md`, `scripts/session_self_initialization.py`, `.codex/gtkb-hooks/session_start_dispatch.py`, `.claude/hooks/session_start_dispatch.py`, `scripts/cross_harness_bridge_trigger.py`, `scripts/workstream_focus.py`, `scripts/single_harness_bridge_dispatcher.py`, `scripts/harness_roles.py`, `.gitignore`, and the spec approval packet for `SPEC-BRIDGE-MODE-CONFIG-TRANSACTIONS-001`.

## Copyright

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
