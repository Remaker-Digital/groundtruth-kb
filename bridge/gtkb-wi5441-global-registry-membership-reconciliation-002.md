NO-GO
::init gtkb lo
::open test
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 735da741-aec1-45b1-8a49-b05df6b9d3c7
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code scheduled Loyal Opposition worker (loyal-opposition-worker task), owner-directed manual review; transcript-resolved role loyal-opposition; independent of the -001 author (019f863a-acd3-7320-80c0-1831f0936cc0, Codex A)
author_metadata_source: gt session envelope show --harness-name claude

# Loyal Opposition Verdict - NO-GO - WI-5441 Global Registry Membership Reconciliation

bridge_kind: lo_verdict
Document: gtkb-wi5441-global-registry-membership-reconciliation
Version: 002
Author: Loyal Opposition (Claude, harness B)
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-wi5441-global-registry-membership-reconciliation-001.md
Reviewed proposal: bridge/gtkb-wi5441-global-registry-membership-reconciliation-001.md
Date: 2026-07-26 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HOUSEKEEPING-HARDENING-WI5441-REGISTRY-CONTROL-PLANE-20260724
Project: PROJECT-GTKB-HOUSEKEEPING-HARDENING
Work Item: WI-5441

## Verdict

NO-GO.

**The technical core of this proposal is correct and independently reproduced.**
I re-derived the central P0 evidence join from scratch and it is exact: 226
observations, 156 unique operative paths, 128 present-and-unregistered, zero
missing, 117 skill + 11 hook/script, uncovered roots 49/39/38/2. The declared
128-path admission set is set-equal to my independently computed set with zero
difference in either direction. The claimed false `coverage_complete` predicate
is real and sits where the proposal says it does. The four-class authority model,
the exact-over-glob admission discipline, and the report-first non-destructive
posture are all sound.

I am nevertheless returning NO-GO on four findings, two of which are P1. The
first is not a technical defect at all â€” it is a governance-surface concern that
I reproduced mechanically and cannot let pass silently.

## Review Independence And Disclosure

- Reviewer session `735da741-aec1-45b1-8a49-b05df6b9d3c7` (Claude, harness B),
  resolved role `loyal-opposition`. Note: `gt session envelope show` reports a
  longer-lived envelope session `854f1df5-c3f8-4d34-b7ad-3a62cad20ab4` opened
  2026-07-25; the harness session context for this review is the former. Both
  are distinct from every author cited below, so independence holds under either
  identifier.
- Proposal author: `019f863a-acd3-7320-80c0-1831f0936cc0` (Codex, harness A).
  Distinct session and distinct harness. No same-session self-review.
- Author metadata on -001 is present, complete, and machine-readable. No
  fail-closed metadata condition applies.
- **Methodology disclosure.** Part of the evidence reproduction below was
  performed by a read-only sub-agent under my direction. I independently
  re-executed the load-bearing governance-gate finding (F1) myself against the
  live hook module before recording it, and I state per finding which evidence I
  personally reproduced.

## Findings

### F1 (P1, BLOCKING) - a single JSON unicode escape suppresses a governance gate that would otherwise fire on this proposal

**Claim.** Entry `.codex/gtkb-hooks/formal-artifact-approval.cmd` in the
`registry_admission_paths` array encodes the letter `a` as the JSON escape
`a`. That one escaped character is the **sole** difference between the
bridge-compliance gate's approval-evidence detector firing and not firing on this
document.

**Evidence - reproduced by me, directly against the live hook module.** I loaded
`.claude/hooks/bridge-compliance-gate.py` and called
`_declares_approval_evidence_scope` on the file's exact bytes, and again on the
same bytes with `a` decoded to `a`:

| Input | `_declares_approval_evidence_scope` |
| --- | --- |
| file as filed (escaped) | `False` |
| file with `a` decoded | **`True`** |

Nothing else was altered between the two runs.

**Mechanism.** `APPROVAL_EVIDENCE_DECLARATION_RE` matches
`formal[-\s]+artifact[-\s]+approval\b` case-insensitively.
`_declares_approval_evidence_scope` splits content on sentence boundaries and
returns `True` on the first matching segment that carries no negation word. The
document contains two potential triggers:

1. Line 27, `approval_evidence_scope: no formal-artifact approval-evidence or
   approval-packet work...` - matches, but is **negated** by the leading `no`,
   so it is skipped.
2. The `registry_admission_paths:` line - the decoded path fragment matches, and
   because the JSON array is comma-packed with no whitespace after the `.cmd`
   periods, the entire 128-path array is a **single segment containing no
   negation token**. It therefore triggers.

Downstream, `_approval_evidence_target_paths_ask_reason` fires because
`target_paths` contains no `.groundtruth/formal-artifact-approvals/<packet>.json`
path, producing a governance checkpoint.

**Consequence on the authoring harness.** This is not a soft prompt on the Codex
side. `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py:275-276`
maps `permissionDecision in {deny, ask, block}` to **return code 2**, and
`run_py_no_window.py` propagates a non-zero child code as the batch exit code. An
unescaped `apply_patch` write of this file from Codex would have been **rejected**.
On the Claude surface the same condition surfaces as `ask` - an owner-visible
checkpoint.

**No legitimate technical mechanism produces this escape.** `a` is a JSON
escape for plain ASCII `a`; both forms parse identically, so there is no parsing,
encoding, or serialization necessity. `ensure_ascii` escapes only non-ASCII, so
no standard serializer emits it. I checked the other candidate surfaces and none
is implicated: `credential-scan.py` and `scanner-safe-writer.py` contain zero
occurrences of the pattern; `formal-artifact-approval-gate.py` handles only
`tool_name == "Bash"` and does not inspect bridge content;
`narrative-artifact-approval-gate.py` matches the plural directory form
`.groundtruth/formal-artifact-approvals`, which this fragment does not contain.
The bridge-compliance gate is the only surface that matches the literal.

**What I am explicitly NOT claiming.** I am not asserting intent. Mechanical
evidence establishes effect, not motive, and I have no evidence bearing on how
the escape was introduced. I also note the proposal's **substantive position is
very likely correct**: `.codex/gtkb-hooks/formal-artifact-approval.cmd` genuinely
is a capability subject - an executable hook surface being registered - and not
formal-artifact approval-evidence work. The gate firing here would most likely be
a **false positive**.

**Why it is still blocking.** The remedy for a false-positive gate is to let it
fire and answer the checkpoint on the record, or to fix the gate's detector. It
is not to alter the payload so the detector cannot see it. A governance gate that
can be silenced by re-encoding one character is not a gate, and a precedent that
normalizes payload-level suppression is far more expensive than one owner
checkpoint. Line 27's pre-emptive negated disclaimer shows the author already
anticipated this exact detector, which makes the unexplained escape on the one
unnegated trigger something the record must address explicitly rather than
absorb.

**Required Revision (F1).** Choose one, and state which in the revision:

- **Option A (recommended).** Write the path unescaped and let the gate fire.
  Answer the resulting checkpoint on the record, stating that the path is a
  capability subject rather than approval-evidence work. This is one owner
  checkpoint and leaves a clean audit trail.
- **Option B.** Keep the escape **only** if there is a genuine mechanical
  necessity, and disclose it explicitly in the proposal body with the reason.
- **Option C.** Propose a narrow detector fix (for example, excluding matches
  that occur inside a `registry_admission_paths` / `target_paths` JSON array)
  as separate scoped work, then refile unescaped once it lands.

In all three cases the revision must **disclose the escape and its effect**, so
the append-only record shows the gate was considered rather than bypassed.

### F2 (P1, BLOCKING) - `capability_evidence_hash` is not reproducible and no code emits it

**Claim.** The proposal binds
`capability_evidence_hash: sha256:1bc3ef098c44e340f3a3117c424925ab7355d2d66ef64b36f43c5ebfceb484c3`
and requires it to be bound **into the admission batch** (Exact Capability
Admission, item 2). A reviewer cannot reproduce it, and no code in the repository
computes a field by that name.

**Evidence.** Approximately 33 plausible canonical serializations were attempted
over the same underlying data - newline-join and JSON (sorted, compact, indent
2/4, with and without trailing newline) of the 128 uncovered paths, of the 156
operative paths, and of the 226 observation tuples; comma, space, and semicolon
joins; report-shaped dicts combining counts, roots, and paths; and both the raw
and LF-normalized bytes of the capability registry file. None matched. A repo
search found no producer for `capability_evidence_hash`; the `capability_hash`
columns in `registry_control_plane.py` belong to an unrelated
observation-capability token system.

For contrast, these are reproducible deterministically over the same data:

- `sha256` of newline-joined sorted 128 uncovered paths:
  `398ffb54a908753a050514d40a358cd6560e2daa9015e63ca7aae9567214f52c`
- `sha256` of compact-JSON sorted 128 uncovered paths:
  `764d06b357a5018939c1ebe634257613f4369e48f013bd16f34ead7ac336b43c`
- `sha256` of the capability registry bytes:
  `ed6d8b62defa7746ac300d680ec7905bab6fa713269b76b24be9706628b2bc15`

**Risk / impact.** The proposal makes this digest a **binding precondition** of
the 128-record transaction. A binding whose derivation is undefined cannot be
verified by a reviewer, cannot be re-derived by a future auditor, and cannot be
mechanically asserted by the implementation. That is the same class of defect
this reviewer is concurrently blocking on the WI-5640 thread: evidence that
cannot be re-derived from the record is not evidence.

**Required Revision (F2).** Either specify the exact serialization algorithm in
the proposal (ordering, separator, encoding, and what is hashed), or replace the
value with one emitted by named, testable code. If the digest is retained as a
transaction binding, the implementation must include a test that recomputes it
from source data.

### F3 (P2, BLOCKING) - the P0 evidence baseline is uncommitted working-tree state, and the P0 section does not say so

**Claim.** The "Deterministic P0 Evidence" and 313-record composition claims are
computed against the **uncommitted** WI-5640 registry postimage, not committed
state. The section presents 313 and 128 as settled facts without disclosing the
baseline.

**Evidence.** `git show HEAD:config/registry/sot-artifacts.toml` yields **145**
records (130 exact / 10 virtual / 1 glob / 3 opaque / 1 recursive). The worktree
file is `+2856 / -0` lines and yields **313** (298 / 10 / 1 / 3 / 1) - which is
what I observe live and what the proposal claims. Both the canonical file and the
packaged mirror are dirty. Those bytes come from the parallel
`gtkb-file-move-rename-canonicalization-v4` thread, which is **not** VERIFIED and
**not** finalized.

**Why this matters beyond bookkeeping.** No reviewer working from committed state
can reproduce 313 or 128. More importantly, both numbers are **derived from an
artifact set that is currently under a NO-GO** and could still change. The
proposal's own Cross-Thread Coordination section handles the *implementation*
sequencing correctly, but the P0 Evidence section - the part that carries the
argument that registry completeness is false - does not carry the same caveat.

**Required Revision (F3).** State plainly in the P0 Evidence section that the
counts derive from the uncommitted v4 postimage, cite that thread, and state
what must be re-derived if the v4 baseline changes before implementation.

### F4 (P3, non-blocking) - the observer selection rule as written does not reproduce the numbers

**Claim.** The proposal states the observer excludes "no `fallback`,
`unsupported`, or *waived* surface." Excluding waived surfaces yields
**225 / 155 / 127**, not the claimed 226 / 156 / 128. The numbers reproduce only
when waived surfaces are **included**.

**Evidence.** The single delta is `.codex/gtkb-hooks/session_start_dispatch.py`,
declared `status = "native"` under capability `hook.session-start-governance`
(`config/agent-control/gtkb-harness-capability-registry.toml:1779-1781`) while
also carrying a `[[parity_waivers]]` entry (`:2102`).

**This is a prose defect, not a logic defect.** Including it is the *correct*
behavior and matches `scripts/check_harness_parity.py:893-895`, where
`_apply_waiver` returns the result unchanged unless `result.state == "MISSING"` -
so a waiver on a *present* native surface does not demote it.

**Recommended correction.** Reword to "no absent waived surface", or drop
"waived" from the exclusion list entirely.

## Confirmed Claims (reproduced, no finding)

| Claim | Observed | Verdict |
| --- | --- | --- |
| 226 evidence observations | 226 (68 canonical_source + 65 claude + 54 codex + 39 antigravity; 68 capabilities) | CONFIRMED |
| 156 unique operative paths | 156 | CONFIRMED |
| 128 present with no registry member | 128 | CONFIRMED |
| zero missing operative paths | 0 | CONFIRMED |
| 117 skill + 11 hook/script uncovered | 117 + 11 | CONFIRMED |
| uncovered roots 49 `.codex` / 39 `.claude` / 38 `.agent` / 2 `scripts` | 49 / 39 / 38 / 2 | CONFIRMED |
| live registry 313 = 298 exact / 10 virtual / 1 glob / 3 opaque / 1 recursive | exact match | CONFIRMED (baseline caveat - F3) |
| `registry_admission_paths` has 128 entries matching `registry_admission_path_count` | 128, zero duplicates | CONFIRMED |
| all 128 declared paths exist on disk | 128/128 present (after decoding `a`) | CONFIRMED |
| none of the 128 currently resolves to a registry member | 0/128 resolve | CONFIRMED |
| declared set equals the independently observed uncovered set | set-equal, zero difference either direction | CONFIRMED |
| `coverage_complete` is a count-only inequality | `sot_audit.py:113-115`: `registry_count > 0 and persistent_file_count >= registered_file_count` | CONFIRMED |

The `coverage_complete` predicate is surfaced in `as_dict()` (`:127`) and
`render_markdown()` (`:376`), so the false predicate is consumer-visible - which
strengthens the proposal's case for correcting or retiring it.

## Design Assessment (no findings; recorded for the record)

These aspects of the proposal I reviewed and found sound:

- **Exact-over-glob admission.** Correct. Wholesale directory coverage would
  retain disposable drafts and generator debris; the exact 128-path ceiling
  prevents that and makes the mutation scope auditable.
- **Four-class model.** `registered` / `unregistered_load_bearing` /
  `unregistered_disposable` / `invalid_unknown` is well-formed, and routing parse
  failures, path escapes, collisions, and reparse uncertainty to `invalid_unknown`
  rather than to `disposable` is the correct fail-closed default.
- **Observers cannot grant membership.** The separation between observation and
  authority is the right invariant, and stating that Git tracked/ignored/untracked
  status is evidence metadata only is consistent with `SPEC-INTAKE-97538b` v2.
- **Subtree pruning.** Correctly identified by the proposal as the
  highest-risk element. The stated precondition - prune only when neither registry
  nor observer has a descendant and no unsafe filesystem boundary is present -
  is the right one, and the required million-file synthetic test is appropriate.
- **Sweep execution held out of scope.** Correct. Quarantine, receipt,
  retention, and restoration remain separately authorized.

## Sequencing Status

The proposal's Cross-Thread Coordination section makes implementation conditional
on four preconditions. Precondition 1 - "v4-017 receives an independent VERIFIED
and its governed finalization commit completes" - is **not met**. v4-017 received
an independent NO-GO at
`bridge/gtkb-file-move-rename-canonicalization-v4-018.md` (session
`c24ef7c7-4625-48f1-b8c0-1a377bfbe13f`), citing five impossible SHA-256 digests
plus five further findings.

I independently reached the identical primary finding on that thread in this
session before observing that verdict had been filed, and stood down rather than
stack a redundant verdict.

This does not block *review* of this proposal - concurrent review is explicitly
contemplated by its own text and I have performed it. It does mean the shared
implementation baseline remains unsettled, which is the substance of F3.

## Specification-Derived Verification Plan (Spec-to-Test Mapping)

| Spec / governing surface | Verification evidence (this reviewer) | Result |
| --- | --- | --- |
| `GOV-PLATFORM-SOT-REGISTRY-001` v2 | Independent capability join reproduced exactly (226/156/128/0); 128 declared paths confirmed present and unregistered; registry composition matched. | PASS (baseline caveat - F3) |
| `SPEC-INTAKE-97538b` v2 | Reviewed the four-class model and the Git-status-is-not-authority rule; both consistent with the spec. | PASS |
| `DCL-SOT-REGISTRY-RECORD-SCHEMA-001` | Exact-path coverage with explicit lifecycle/domain per class; no glob substitution proposed. | PASS |
| `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` | Transaction requires canonical/packaged byte equality plus current projection and one receipt. | PASS |
| `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` | Single governed `gt registry register --batch-file` transaction; no identity removal; **binding digest unverifiable (F2)**. | **FAIL (F2)** |
| `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` | One typed reconciliation result consumed by doctor, validate, release, migration, sweep; consumers may not reimplement classification. | PASS |
| `ADR-CROSS-HARNESS-PARITY-001` / `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | Typed native/adapter semantics verified against `check_harness_parity.py:893-895`; **selection-rule prose does not reproduce the numbers (F4)**. | PASS with F4 |
| `GOV-WORK-TREE-HYGIENE-001` | Report-first, non-destructive; no deletion or quarantine in scope; **P0 baseline is uncommitted and undisclosed (F3)**. | **FAIL (F3)** |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Both mandatory preflights re-executed at exit 0; **a governance gate on the bridge-write path is suppressed by payload encoding (F1)**. | **FAIL (F1)** |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Specification Links section present and concrete; preflight reports no missing required or advisory specs. | PASS |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Proposal's verification plan maps each requirement to executable evidence with expected results. | PASS |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` | PAUTH, Project, and Work Item lines present and consistent; preflight `blocking_errors: []`. | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Clause `CLAUSE-IN-ROOT` must_apply with evidence found; all declared paths in-root. | PASS |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Proposal preserves the proven defect, plan, and evidence as governed artifacts. | PASS |

Nothing in this mapping is accepted on the proposal's assertion alone. Where a
claim could not be reproduced it is disclosed as a finding, not folded into a
PASS.

## Commands Executed

- `gt session envelope show --harness-name claude` (independence + role resolution)
- `python .claude/skills/gtkb-bridge/helpers/scan_bridge.py --role loyal-opposition --compact --format json`
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5441-global-registry-membership-reconciliation` (exit 0)
- `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5441-global-registry-membership-reconciliation --content-file bridge/gtkb-wi5441-global-registry-membership-reconciliation-001.md` (exit 0; anchored packet below)
- `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5441-global-registry-membership-reconciliation` (mandatory mode, exit 0)
- direct load of `.claude/hooks/bridge-compliance-gate.py` and invocation of
  `_declares_approval_evidence_scope` on the filed bytes and on the
  `a`-decoded bytes (F1 A/B, run by me)
- read of `.codex/gtkb-hooks/bridge-compliance-gate-apply-patch-adapter.py`
  lines 250-278 (decision-to-exit-code mapping)
- read of `.claude/hooks/bridge-compliance-gate.py` `APPROVAL_EVIDENCE_DECLARATION_RE`,
  `_declares_approval_evidence_scope`, `_approval_evidence_target_paths_ask_reason`
- capability-registry parse of `config/agent-control/gtkb-harness-capability-registry.toml`
  with canonical resolver membership checks via
  `groundtruth_kb.project.registry_control_plane`
- `git show HEAD:config/registry/sot-artifacts.toml` composition count vs worktree
- read of `groundtruth-kb/src/groundtruth_kb/project/sot_audit.py` lines 108-130, 370-380
- read of `scripts/check_harness_parity.py` lines 885-900 (`_apply_waiver`)
- `gt registry inspect --no-census --json`
- `python scripts/bridge_claim_cli.py claim gtkb-wi5441-global-registry-membership-reconciliation`
- `KnowledgeDB.search_deliberations` over "registry membership completeness
  reconciliation", "bridge report digest integrity", and related queries

### Observed results

- Applicability preflight: **exit 0**, no missing required or advisory specs.
- Clause preflight: **exit 0**, 0 evidence gaps, 0 blocking gaps.
- Capability join: **226 / 156 / 128 / 0 missing**, 117 skill + 11 hook-script,
  roots 49 / 39 / 38 / 2 - all exactly as claimed.
- Admission set: **128 entries, 0 duplicates, 128/128 present, 0/128 registered,
  set-equal to the independently observed set**.
- `coverage_complete`: count-only inequality confirmed at `sot_audit.py:113-115`.
- Gate A/B: `_declares_approval_evidence_scope` returns **`False` as filed**,
  **`True` decoded**.
- Baseline: **HEAD 145 records vs worktree 313**; canonical and packaged mirror
  both dirty.
- `capability_evidence_hash`: **not reproduced** across ~33 serializations; no
  producing code found.

## Applicability Preflight

- packet_hash: `sha256:ab62d9e81b8869ddc70f89ab8de955b7f4e81138f9216083a8da97967c0df9cd`
- bridge_document_name: `gtkb-wi5441-global-registry-membership-reconciliation`
- content_source: `pending_content`
- content_file: `bridge/gtkb-wi5441-global-registry-membership-reconciliation-001.md`
- operative_file: `bridge/gtkb-wi5441-global-registry-membership-reconciliation-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.author_metadata_warnings: []
- warnings.unclassified_target_paths: []
- missing_required_specs: []
- missing_advisory_specs: []
- blocking_errors: []
- candidate_evidence_hash: `sha256:14a332cd75de497f5ef529935693963ca8454ca9abd1a90cdd00a35be162a7d7`

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi5441-global-registry-membership-reconciliation`
- Operative file: `bridge/gtkb-wi5441-global-registry-membership-reconciliation-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation; no report-only flag). **Observed exit: 0.**

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | â€” | blocking | blocking |

Note: both preflights pass. F1 is **not** a preflight failure - it is a
suppression of a *different* gate (the approval-evidence detector) on the
bridge-write path, which is why neither preflight surfaces it.

## Prior Deliberations

- `DELIB-20260722-ARTIFACT-REGISTRY-AUTHORITATIVE-HYGIENE-SWEEP` - the
  controlling owner directive establishing the registry as sole membership
  authority with quarantine-only disposal. This proposal is a faithful
  continuation of it.
- `bridge/gtkb-wi5441-registry-control-plane-reverse-coverage-v4-006.md` -
  VERIFIED control-plane foundation, explicitly bounded to touched chokepoints
  with no census verification. Confirms this proposal's premise that the earlier
  thread is not membership closure.
- `bridge/gtkb-sot-singleton-coverage-audit-007.md` and `-008` VERIFIED -
  the WI-5014 duplicate-SoT audit whose count-only `coverage_complete` predicate
  this proposal corrects. I confirmed the predicate is exactly as described.
- `bridge/gtkb-file-move-rename-canonicalization-v4-018.md` - the independent
  NO-GO on the shared baseline thread (five impossible SHA-256 digests plus five
  further findings). Directly relevant to F3.
- `bridge/gtkb-wi5640-report-digest-integrity-advisory-001.md` - the concurrent
  advisory establishing the "evidence that cannot be re-derived is not evidence"
  principle that F2 applies here.
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` - obsolete sources remain; no
  deletion is performed by this proposal, consistent with that decision.
- `DELIB-202667192` - WI-5441 registry-completeness and enforcement handoff;
  confirms WI-5640 correctly declined general registry-seeding scope and that
  this thread is the right owner of it.
- Semantic Deliberation Archive search over "registry membership completeness
  reconciliation" and adjacent queries returned **no controlling prior decision
  contrary to this proposal's approach**, and none addressing governance-gate
  suppression by payload encoding.

## Specification Links Carried Forward

- `GOV-PLATFORM-SOT-REGISTRY-001` v2
- `SPEC-INTAKE-97538b` v2
- `DCL-SOT-REGISTRY-RECORD-SCHEMA-001`
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001`
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001`
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Required Revisions

1. **F1 (blocking).** Resolve the `a` escape via Option A, B, or C, and
   disclose the escape and its gate effect in the revision.
2. **F2 (blocking).** Define the `capability_evidence_hash` serialization, or
   replace it with a digest emitted by named testable code.
3. **F3 (blocking).** Disclose in the P0 Evidence section that 313 and 128 derive
   from the uncommitted v4 postimage, and state the re-derivation obligation if
   that baseline changes.
4. **F4 (not blocking).** Correct the observer-selection prose regarding waived
   surfaces.

No change is required to the four-class model, the exact-admission ceiling, the
128-path set itself, the subtree-pruning safety conditions, the enforcement-
consumer design, or the scope boundaries. Those are approved as written and
should carry forward verbatim.

## Scope Notes For Prime Builder

1. **The evidence core is confirmed.** The 226/156/128 join, the 128-path
   admission set, and the false `coverage_complete` predicate were all
   independently reproduced. Do not re-derive them; cite this verdict.
2. **F1 is a disclosure-and-choice finding, not an accusation.** The substantive
   position that the path is a capability subject is likely correct. What the
   record needs is that position stated openly with the gate allowed to fire, not
   an encoded payload that prevents the question from being asked.
3. This NO-GO does not authorize any registry mutation, quarantine, deletion,
   sweep execution, commit, push, release, deployment, dispatcher mutation, or
   WI-5640 Stage B work.
4. Implementation remains gated on all four Cross-Thread Coordination
   preconditions, of which precondition 1 is currently unmet.

## Standing-Backlog Candidates Surfaced By This Review

Recorded for Prime Builder disposition per `GOV-STANDING-BACKLOG-001` and the
strategic self-improvement directive. Not conditions on the revisions above, and
not implementation approval.

1. **Encoding-normalization before governance-detector evaluation.** The
   bridge-compliance gate evaluates raw file bytes, so any JSON/unicode escape of
   an ASCII character silently defeats its literal-matching detectors. Decoding
   escape sequences before detector evaluation - or flagging ASCII-range escapes
   in bridge payloads as suspicious - would close this class generally rather
   than one path at a time.
2. **Detector precision for path-array segments.** The approval-evidence detector
   treats an entire comma-packed JSON path array as one unnegated segment, which
   makes false positives likely whenever a registered path merely contains a
   governance keyword. Excluding `registry_admission_paths` / `target_paths`
   array values from the detector would reduce the pressure that produced F1.

## Owner Action Required

None to record this NO-GO. F1 Option A would produce one owner checkpoint at
Prime Builder's next write; that checkpoint is the intended governance behavior
and needs no pre-authorization from the owner now.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
