REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019fb19b-7814-73c1-8707-204e432cbf00
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: Codex Desktop interactive Prime Builder task; user-directed newest-first bridge processing
author_metadata_source: x-codex-turn-metadata

bridge_kind: prime_proposal
Document: gtkb-wi5765-lo-atomicity-suites-and-carrier-gate
Version: 005
Responds to: bridge/gtkb-wi5765-lo-atomicity-suites-and-carrier-gate-004.md
Date: 2026-07-30 America/Los_Angeles

Project Authorization: PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM
Project: PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729
Work Item: WI-5765

target_paths: ["platform_tests/scripts/test_lo_verified_commit_atomicity.py", "platform_tests/skills/test_auto_retire_actuation_helper_parity.py", ".claude/hooks/bridge-compliance-gate.py", "config/hooks/gtkb-bridge-compliance-gate.py", "groundtruth-kb/templates/hooks/bridge-compliance-gate.py", "platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py"]

# WI-5765 REVISED — Restore LO Atomicity Suites and the Bridge-Only Carrier Gate

Scope confirmation: this proposal performs no MemBase mutation and no
`groundtruth.db` write. Its MemBase/project/PAUTH references are read-only
authority evidence only.

## Revision Disposition

This revision accepts v004's NO-GO on the executable authority of GO-002 and
cures that defect through the current whole-project authority model. It does
not use the WI-specific authorization named in v003/v004. Individual work-item
approval and per-WI PAUTH are historical/non-controlling under
`DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` and
`DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD`.

The controlling authorization is active whole-project
`PAUTH-PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729-PROGRAM` v5, current row
942, changed `2026-07-30T14:06:37+00:00`. Its list-free project envelope
allows `source`, `test`, `test_addition`, `configuration`, `metadata`,
`governance_evidence`, and `bridge`. WI-5765 is an active member of active
`PROJECT-GTKB-ADVISORY-CORRECTIONS-20260729`. The v004 blocker is therefore
removed at the project level: both hook targets now have their required
`configuration` class without a per-WI exception.

This is an append-only proposal correction only. GO-002 is not reused.
Implementation requires a fresh independent GO on this exact v005, an exact
claim, and a schema-v3 implementation-start packet before any protected
target changes. No dispatcher or TAFE activation/configuration/mutation,
external-system action, credential action, push, history rewrite, deployment,
release, or destructive cleanup is in scope.

## Preserved Problem and Scope

The substantive A1/A7 design accepted in v001/v002 is unchanged.

### A1 — red LO finalization-atomicity suites

`platform_tests/scripts/test_lo_verified_commit_atomicity.py` and
`platform_tests/skills/test_auto_retire_actuation_helper_parity.py` still use
retired `skills/verify/` helper paths. Their fixtures abort or compare dead
paths instead of enforcing the terminal commit-atomicity contract. The live
helper topology is the Claude and Codex
`skills/gtkb-verify/helpers/write_verdict.py` pair; Cursor has no helper copy
and exposes its governed fallback through
`.cursor/skills/gtkb-verify/SKILL.md`. Goose divergence remains outside this
WI in the WI-5763 lane.

Repair both suites to the live Claude/Codex `gtkb-verify` topology and remove
the phantom Cursor helper-copy entry. Expectations remain governed by
`DELIB-202667533` AT-01: assert commit-before-terminal-publication outcomes,
assert that commit failure leaves neither a verdict file nor published
terminal state, and do not pin the rejected publish-first or temporary
pending-then-promote mechanism as a durable requirement. Any genuine helper
ordering defect exposed by the repaired tests is reported to the WI-5742 /
WI-5666 finalizer lane rather than expanded into this implementation.

### A7 — bridge-only carrier VERIFIED evidence

The compliance gate currently requires a test-runner token for every VERIFIED
body, including bridge-only evidence carriers whose reviewed implementation
report changes only `bridge/**`. That class can honestly provide exact git
provenance and governed applicability/clause preflights but may have no
source-derived test to run.

Condition only the command-evidence limb of
`_has_spec_derived_verification` so non-test evidence is sufficient if and
only if all three conditions hold:

1. The thread's reviewed operative implementation report resolves
   deterministically.
2. Its `target_paths` parse cleanly, are non-empty, and every path is under
   `bridge/**`.
3. The VERIFIED body records executed governed preflight evidence plus exact
   git provenance (`git show` / `git diff-tree` class commands).

Absent, malformed, ambiguous, or mixed/non-bridge target paths fail closed and
retain the existing test-runner requirement. `COMMAND_EVIDENCE_RE` remains
textually unchanged; preflight/git tokens are not added globally. Per-thread
owner waivers are not introduced.

Apply the gate change to the canonical hook, its tracked byte-identical
`config/hooks/` activated copy, and the corresponding template region. This
WI does not claim full template byte parity; the broader parity correction
remains with WI-5764. Codex hook adapters already invoke the canonical hook
and require no edit.

## Cross-Harness Disposition

| Harness or surface | Disposition |
| --- | --- |
| Claude / canonical workspace hook | `.claude/hooks/bridge-compliance-gate.py` is the canonical behavioral implementation and is an exact target. |
| Codex | Existing `.codex/gtkb-hooks/bridge-compliance-gate*.py|.cmd` adapters invoke the canonical hook; behavior changes by reference and adapter bytes remain unchanged. |
| Cursor and Antigravity | No separate compliance-gate implementation is registered for this predicate; both consume governed bridge artifacts produced under the canonical workspace gate. No phantom projection is created. |
| Ollama, OpenRouter, Goose, and Alibaba Cloud Studio | Provider harnesses have no independent copy of this write-time hook. Their bridge outputs remain subject to the same canonical publication/compliance path; no provider-specific prompt, dispatcher route, or TAFE setting is changed. |
| Activated configuration copy | `config/hooks/gtkb-bridge-compliance-gate.py` receives the byte-identical canonical change and is an exact target. |
| Scaffold/template | `groundtruth-kb/templates/hooks/bridge-compliance-gate.py` receives the corresponding logical change so future installations preserve behavior; unrelated pre-existing template drift stays with WI-5764. |
| Regression suites | The three `platform_tests/**` targets exercise canonical behavior and live Claude/Codex helper topology; no harness-specific test bypass or waiver is used. |

No owner waiver is claimed. Any discovery of another registered implementation
of the predicate is target-scope drift and stops implementation for a fresh
append-only proposal.

## Exact Target and Concurrency Check

The exact six v001 targets are preserved with no addition or removal. A fresh
`git status --short -- <six paths>` check immediately before this revision
returned no entries. The prior WI-5765 claim is expired and no current holder
owns the slug. Any later target or claim drift invalidates this proposal's
start readiness and must be re-evaluated before implementation.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — bridge authority and terminal commit-finalization gate.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — truthful spec-to-test evidence and fail-closed VERIFIED behavior.
- `SPEC-1662` — meaningful assertion quality; fully red suites enforce nothing.
- `GOV-15` — the test repair occurs only through this reviewed correction.
- `GOV-10` — tests exercise exposed finalizer and compliance-gate behavior.
- `GOV-12` — WI-5765 drives the new gate regression cases.
- `GOV-17` — the hook change requires governed proposal/review evidence.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — preserve mechanical enforcement.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — canonical/config/template surface discipline.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — Codex adapters continue routing to the canonical hook.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — current project authorization is the controlling implementation envelope.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — PAUTH v5 does not replace this fresh bridge review.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — revalidate PAUTH, claim, targets, and proposal at every operation gate.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — the project/WI/PAUTH header is explicit.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — concrete governing links are carried here.
- `GOV-STANDING-BACKLOG-001` — WI-5765 remains the MemBase work authority.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — authority, membership, targets, and claim state were freshly checked.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — all targets remain in the GT-KB root.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory-to-WI-to-proposal lifecycle and durable carrier evidence.

## Prior Deliberations

- `DELIB-202667531` — routes fix-class advisories into the Advisory Corrections project while preserving item bridge gates.
- `DELIB-202667533` — AT-01 commit-first ordering and AT-04 whole-project program authorization.
- `DELIB-202667534` — routes A1 and A7 to WI-5765; A2-A6 remain in the WI-5763 lane.
- `DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD` — current owner decision that implementation approval is project-only and orphan WIs cannot implement.
- `DELIB-20260630-PROJECT-LEVEL-WI-APPROVAL-RETIREMENT` — individual WI approval state is not current implementation authority.
- `DELIB-202667104` — Cursor fallback topology has no helper copy.
- `DELIB-20265963` — lineage of the auto-retire helper-parity regression suite.
- `DELIB-202666065` — prior governed hunk-scoped VERIFIED finalization behavior.
- `bridge/gtkb-lo-verified-finalization-toolchain-drift-advisory-001.md` — source A1/A7 findings and sequencing.
- `bridge/gtkb-wi5661-hunk-provenance-bridge-evidence-carrier-010.md` — bridge-only carrier exemplar and adjacent-suite padding workaround.

## Owner Decisions / Input

No new owner decision is required for this revision. The owner already chose
project-only implementation authority in
`DELIB-20260730-PROJECT-AUTHORITY-INHERITANCE-PULL-FORWARD`. The current active
whole-project PAUTH v5 is backed by `DELIB-202667533` and the corrected
class-scope owner AUQ recorded in its v5 change reason. This proposal does not
rely on `DELIB-202667695` or the historical WI-specific PAUTH named in v003 /
v004.

## Requirement Sufficiency

Existing requirements are sufficient. This revision changes authority
evidence, not the already-accepted A1/A7 requirement interpretation. A new
formal specification would duplicate the current atomicity, truthful VERIFIED
evidence, test quality, project authorization, and cross-harness enforcement
contracts.

## Complete Specification-Derived Test Plan

1. **Atomicity suite green under commit-first semantics.** Run
   `python -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py -q`.
   All 31 tests must collect with zero failures/errors; no retired
   `skills/verify/` literal remains. Ordering-sensitive assertions prove
   terminal publication follows the backing commit and commit failure leaves
   neither terminal publication nor verdict file.
2. **Live helper-copy parity.** Run
   `python -m pytest platform_tests/skills/test_auto_retire_actuation_helper_parity.py -q`.
   All seven tests must pass with Claude/Codex `gtkb-verify` helper copies and
   no phantom Cursor helper. Goose remains outside the parity set for this WI.
3. **Bridge-only carrier accepts governed non-test evidence.** Add a fixture
   whose resolved reviewed report declares only
   `target_paths: ["bridge/<slug>-NNN.md"]`. A VERIFIED body with concrete
   specification links, executed preflight evidence, and `git show` /
   `git diff-tree` provenance, but no test-runner token, must pass the
   spec-derived-verification predicate.
4. **Source-bearing and malformed reports remain denied.** The negative twin
   with any non-bridge target must retain the test-runner requirement. Missing,
   empty, malformed, ambiguous, or unresolvable `target_paths` must receive no
   exemption. Existing predicate tests remain green.
5. **No global regex weakening.** Assert `COMMAND_EVIDENCE_RE` receives no
   preflight or git tokens and remains textually unchanged by this WI.
6. **Activated-copy discipline.** The canonical and `config/hooks/` gate
   copies must be byte-identical after the edit; the same logical region must
   exist in the template without claiming unrelated full-template parity.
7. **Combined focused verification.** Run:
   `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_lo_verified_commit_atomicity.py platform_tests/skills/test_auto_retire_actuation_helper_parity.py platform_tests/hooks/test_bridge_compliance_gate_spec_test_heading.py -q`.
   Then run `ruff check` and `ruff format --check` on all six changed Python
   files and a scoped diff check proving only the approved targets changed.

## Acceptance Criteria

1. Both A1 suites fully collect and pass against the live `gtkb-verify`
   topology with zero retired helper-path literals.
2. Repaired ordering assertions require commit-before-terminal-publication and
   do not encode publish-first or pending-then-promote as a durable contract.
3. Only a deterministically resolved all-bridge carrier receives the governed
   non-test evidence path; mixed, source-bearing, absent, or malformed cases
   fail closed.
4. `COMMAND_EVIDENCE_RE` remains globally unchanged.
5. Canonical/config activated gate copies are byte-identical, the template
   region is updated, focused tests pass, and Ruff lint/format checks pass.
6. The implementation report maps every acceptance criterion to executed
   evidence and requests independent VERIFIED review; no terminal state is
   self-authored.

## Risks, Stop Rules, and Rollback

Risk is low-to-medium. A1 restores signal to red tests. A7 is a narrowly
conditioned exception with a fail-closed default. Stop immediately if target
preimages or ownership drift, PAUTH v5 changes/expires/is superseded, another
claim appears, helper re-greening exposes a production finalizer-ordering bug,
the gate cannot resolve the exact reviewed report without heuristic fallback,
or the change would require a seventh target. Route any such expansion through
a fresh append-only proposal.

Rollback is a scoped revert of only this implementation cohort after governed
review; no bridge history is overwritten or deleted. TAFE remains deliberately
disabled. No dispatcher mutation is permitted.

Recommended commit type: fix

## Verification Questions for Loyal Opposition

1. Does current whole-project PAUTH v5 cure the v004 configuration-class
   blocker while correctly superseding the historical per-WI PAUTH route?
2. Does v005 preserve the full A1/A7 design and test plan without broadening
   the exact six targets?
3. Are the bridge-only-carrier conditions sufficiently fail-closed to prevent
   source-bearing threads from using non-test evidence?

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
