NEW
::init gtkb pb
::open build

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex Desktop interactive Prime Builder; transcript-defined ::init gtkb pb; dispatcher deliberately disabled
author_metadata_source: explicit_interactive_session_metadata

# Advisory Report - Bridge proposal helper pays multi-second eager-import and duplicate-compliance latency

bridge_kind: governance_review
Document: gtkb-advisory-bridge-propose-cold-import-duplicate-audit-latency
Version: 001
Date: 2026-07-30 UTC

target_paths: []
implementation_scope: none
requires_review: true
requires_verification: false
kb_mutation_in_scope: false
dispatcher_or_tafe_mutation_in_scope: false

## Summary

The bridge-proposal filing path has a repeatable latency defect before any
governed write occurs. On an existing 18,359-byte bridge proposal, importing
the helper required 16.881 to 31.934 seconds across four cold observations,
while its actual 30-pattern credential scan completed in approximately 16
milliseconds. After setup, the proposal helper runs a compliance audit and then
calls the canonical writer, which unconditionally runs the same audit again.
Each audit also starts separate applicability and ADR/DCL clause-preflight
Python processes.

The dominant measured costs are eager Python package initialization and
duplicate audit orchestration. Live SQLite/MemBase query time was approximately
10 milliseconds median and disabling applicability's MemBase enrichment saved
only about 0.13 seconds in the profiled run. This evidence therefore does not
support a generic database-cache fix. It supports a narrower correction that
preserves one authoritative final-bytes compliance decision while removing
eager unrelated imports and redundant evaluation.

## Advisory Classification

- Category: governed tool latency, import topology, duplicate validation.
- Affected operation: bridge proposal preparation and filing.
- User-visible symptom: credential/compliance preflight appears hung for tens
  of seconds even on a modest single document.
- Scale sensitivity: every fresh helper process repays the package import cost;
  every filing repays duplicate compliance and subprocess startup.
- Authority: review-only advisory. No corrective implementation, work-item
  approval, or project authorization is granted here.

## Claim

The bridge proposal hot path does substantially more setup and compliance work
than its requested operation requires. GT-KB should preserve fail-closed,
final-content validation and independent applicability/clause semantics while
making the canonical writer the sole compliance owner, or accepting only a
cryptographically bound equivalent result, and avoiding eager import of the
entire bridge package for one prior-deliberations dependency.

## Source And Measurement Context

The latency was encountered repeatedly while credential-scanning and
compliance-checking bridge drafts in this Prime Builder session. A read-only
profiling worker then isolated import, credential-scan, compliance-subprocess,
warm-core, applicability, and SQLite components against:

```text
bridge/gtkb-wi5759-ruff-gate-staged-blob-001.md
```

The tested document was 18,359 bytes. Profiling created no bridge file, packet,
claim, database row, source/test change, dispatcher/TAFE action, external
action, or process termination.

## Evidence

### E1 - Helper cold import dominates the credential operation

Cold import observations for
`.codex/skills/gtkb-bridge-propose/helpers/write_bridge.py` were:

```text
23.715 s
22.111 s
31.934 s
16.881 s
```

By contrast, the actual 30-pattern `scan_credential_hits()` operation had a
median of 16.179 milliseconds and returned zero hits. The credential regex
scan itself is not the latency source.

### E2 - Eager bridge package initialization is the primary setup path

The helper eagerly imports
`groundtruth_kb.bridge.prior_deliberations` at
`.codex/skills/gtkb-bridge-propose/helpers/write_bridge.py:56`. Python first
executes `groundtruth_kb.bridge.__init__`, whose lines 24-105 eagerly import a
large retained/retired audit, checkpoint, detector, handshake, notification,
registry, routing, runtime, and worker surface.

Independent measurements found:

- ordinary `prior_deliberations` package import: 17.409 seconds;
- direct source-module load that avoided package initialization: 0.326 seconds.

The comparison is diagnostic, not a proposal to bypass package contracts in
production. It demonstrates that unrelated package initialization, not the
needed module's own work, dominates setup.

### E3 - Compliance is evaluated twice per helper filing

The helper entry points run their own compliance audit at
`write_bridge.py:505` and `write_bridge.py:578`, then call
`_bridge_writer.write_bridge_file()` at lines 519 and 590. The canonical writer
unconditionally runs compliance again at
`scripts/gtkb_bridge_writer.py:1040`.

This duplicates an expensive gate. Removing the writer's final audit would be
unsafe because the writer owns the final bytes and write boundary. The safer
direction is to remove the helper's redundant audit, or pass a content-hash-
bound audit result that the writer revalidates without accepting stale bytes.

### E4 - Each compliance audit starts two additional preflight processes

`.claude/hooks/bridge-compliance-gate.py:1598-1695` invokes the applicability
and clause preflights as new Python processes. Observed medians were:

- applicability subprocess: 3.125 seconds;
- clause subprocess: 1.236 seconds;
- gate process/self-test baseline: 1.419 seconds.

Together, one duplicate audit adds roughly 5.8 seconds median before run noise.
The helper-plus-writer path can pay that orchestration twice.

### E5 - Warm validation and MemBase reads are not the dominant costs

- Warm compliance core: approximately 109 milliseconds median.
- Live membership SQLite query: approximately 10 milliseconds median.
- In-process applicability build: approximately 0.77-1.06 seconds median.
- Disabling MemBase enrichment reduced applicability median by only about
  0.13 seconds in the noisy profiling run.

These measurements matter because GT-KB favors append-only authoritative
history and already has real SoT-access latency elsewhere. This case should not
be misdiagnosed as append-only database growth or solved with an ungoverned
cache. The concrete bottleneck is import and duplicate orchestration.

## Risk And Impact

1. Every fresh proposal-helper process can spend tens of seconds before the
   requested content scan begins, making a safe gate look non-live.
2. Duplicate compliance multiplies subprocess startup, filesystem reads, and
   governance checks without adding an independent final-bytes boundary.
3. Operators may retry or terminate apparently stalled commands, multiplying
   load or confusing a slow read with a deadlock.
4. Broad caching could introduce competing authority or stale compliance
   decisions if the actual import/audit duplication is not corrected first.
5. Removing the wrong audit could create a time-of-check/time-of-use window;
   final-content ownership must remain with the canonical writer.
6. Making the package `__init__` lazy can break public import compatibility if
   done without an explicit exported-API inventory and parity tests.

## Related Work And Non-Duplication

- `bridge/gtkb-advisory-implementation-start-peer-scan-liveness-001.md`
  diagnoses an `O(packets x bridge_files)` append-only bridge-history scan in
  implementation authorization. The present path is independent: cold import
  topology and duplicate compliance in proposal filing.
- `bridge/gtkb-advisory-work-intent-release-db-lock-concurrency-001.md`
  diagnoses SQLite writer contention during claim release. The present
  measurements show SQLite is not the dominant cost here.
- Existing compliance, applicability, clause, and bridge-writer work remains
  semantically authoritative. This advisory recommends orchestration changes,
  not removal of those gates.

Corrective intake should search for an active item already owning this exact
helper-import/duplicate-audit path. If none exists, create a project-linked
candidate only after owner disposition; this report itself is not approval.

## Recommended Corrective Direction

1. Keep `scripts/gtkb_bridge_writer.py` as the single mandatory compliance
   owner for the exact final bytes at the write boundary.
2. Remove the helper's pre-write duplicate, or introduce an immutable
   content-hash/config-hash/rules-hash-bound audit envelope that the writer can
   verify without trusting a stale or differently composed result.
3. Make the prior-deliberations dependency lightweight: use a deliberately
   small import surface or make `groundtruth_kb.bridge.__init__` lazy while
   preserving every documented public import.
4. Add an import-time budget test and an exported-name compatibility test so a
   lazy-import correction cannot silently impair consumers.
5. Consider in-process or preloaded applicability/clause APIs only with
   explicit isolation, deterministic configuration, timeout, and error
   equivalence. Subprocess removal is not automatically safe.
6. Instrument named phases—helper import, credential scan, helper audit,
   writer audit, applicability, clause, and write—so future SoT-access latency
   can be distinguished from orchestration cost.
7. Do not introduce a durable mutable cache as a shortcut unless its
   authority, invalidation, rebuild, and final-content binding are separately
   governed.

## Acceptance Evidence For A Future Correction

- Cold helper import stays within a declared budget on a clean process and no
  longer imports unrelated bridge runtime/worker surfaces.
- `scan_credential_hits()` returns identical hits before and after the change.
- One filing produces exactly one authoritative compliance decision for the
  exact final content hash and current rules/config hashes.
- Content mutation between any preliminary check and writer entry cannot reuse
  a stale pass.
- Applicability and clause outcomes, exit behavior, timeout behavior, and
  diagnostics remain equivalent across pass, blocking-gap, malformed, missing-
  config, and subprocess-failure fixtures.
- Public `groundtruth_kb.bridge` imports remain compatible or are migrated by
  an explicitly reviewed API change.
- A representative end-to-end filing benchmark shows bounded latency without
  weakening credential, bridge, applicability, clause, or final-content gates.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`

## Specification-Derived Verification Plan

| Requirement | Future verification | Expected result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Independent Loyal Opposition review of this `NEW` report | Role-correct verdict; append-only bridge authority preserved. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | Route to an existing exact-scope item or owner-approved project-linked candidate | Finding remains durable without duplicate backlog work. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Compare applicability citations before/after orchestration correction | Same required specs and no missing blockers. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Run import-budget, API-compatibility, exact-content TOCTOU, and outcome-equivalence suites | Performance improves without gate weakening. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | Validate active project membership and inherited parent-project PAUTH before later code/test work | No orphan or per-WI implementation authority. |
| `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` | Exercise normal helper/writer filing path | One final authoritative audit; no bypass. |
| `GOV-WORK-TREE-HYGIENE-001` | Run with unrelated dirty/foreign work | No unrelated mutation or attribution. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Compare scan hits, audit decisions, errors, and final bytes over the same corpus | Semantics remain equivalent. |

## Decision Needed

No immediate owner decision is required to preserve or review this evidence.
If disposition creates a new unapproved backlog item, Prime Builder must present
that single item as an AUQ before implementation intake.

## Explicit Non-Approval And TAFE Exclusion

This Advisory Report is not a GO, project authorization, implementation-start
packet, or authorization to modify source, tests, configuration, metadata,
dispatcher/TAFE state, Git history, deployment, credentials, or external
systems. The TAFE dispatcher is deliberately disabled and was not activated or
mutated during profiling or report preparation.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
