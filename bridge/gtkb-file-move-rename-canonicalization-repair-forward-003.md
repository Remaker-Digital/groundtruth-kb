REVISED
::init gtkb pb
::open build
author_identity: prime-builder/codex
author_harness_id: A
author_session_context_id: 019f863a-acd3-7320-80c0-1831f0936cc0
author_model: gpt-5
author_model_version: gpt-5
author_model_configuration: reasoning_effort=high; thread_source=user
author_metadata_source: x-codex-turn-metadata

# WI-5640 Repair-Forward Stage A: Registry Admission and Exact-Plan Production

bridge_kind: prime_proposal
Document: gtkb-file-move-rename-canonicalization-repair-forward
Version: 003
Responds to: bridge/gtkb-file-move-rename-canonicalization-repair-forward-002.md
Author: Codex Prime Builder (harness A)
Date: 2026-07-24 UTC

Project Authorization: PAUTH-PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY-20260715-PROJECT-SCOPE
Project: PROJECT-GTKB-PLATFORM-MODERNIZATION-HARNESS-PARITY
Work Item: WI-5640

target_paths: [".claude/skills/gtkb-bridge/SKILL.md",".claude/skills/gtkb-bridge/helpers/impl_report_bridge.py",".claude/skills/gtkb-bridge/helpers/revise_bridge.py",".claude/skills/gtkb-bridge/helpers/scan_bridge.py",".claude/skills/gtkb-bridge/helpers/show_thread_bridge.py",".codex/skills/MANIFEST.json",".codex/skills/gtkb-bridge/SKILL.md",".codex/skills/gtkb-bridge/helpers/impl_report_bridge.py",".codex/skills/gtkb-bridge/helpers/revise_bridge.py",".codex/skills/gtkb-bridge/helpers/scan_bridge.py",".codex/skills/gtkb-bridge/helpers/show_thread_bridge.py",".codex/skills/gtkb-proposal-review/SKILL.md",".codex/skills/gtkb-send-review/SKILL.md",".codex/skills/gtkb-verify/SKILL.md","config/agent-control/gtkb-acting-prime-builder.md","config/agent-control/gtkb-active-workspace.md","config/agent-control/gtkb-activity-disposition-profiles.toml","config/agent-control/gtkb-activity-envelope-sharding.toml","config/agent-control/gtkb-auq-policy-gates.toml","config/agent-control/gtkb-auto-finalization-sweep.md","config/agent-control/gtkb-backlog-approval-state.md","config/agent-control/gtkb-bridge-essential.md","config/agent-control/gtkb-bridge-permanent-operations-runbook.md","config/agent-control/gtkb-bridge-poller-canonical.md","config/agent-control/gtkb-canonical-terminology.md","config/agent-control/gtkb-canonical-terminology.toml","config/agent-control/gtkb-capability-import-policy.md","config/agent-control/gtkb-command-surface.toml","config/agent-control/gtkb-control-map.md","config/agent-control/gtkb-dead-ends-and-false-positives.md","config/agent-control/gtkb-decision-ledger.md","config/agent-control/gtkb-declarative-agent-role-manifest.yaml","config/agent-control/gtkb-deliberation-protocol.md","config/agent-control/gtkb-dispatcher-daemon-substrate-rollback-runbook.md","config/agent-control/gtkb-file-bridge-protocol.md","config/agent-control/gtkb-governance-emergency-bootstrap-protocol.md","config/agent-control/gtkb-harness-capability-registry.toml","config/agent-control/gtkb-harness-model-pin-confirmations.toml","config/agent-control/gtkb-knowledge-base-index.md","config/agent-control/gtkb-lo-startup-overlay.md","config/agent-control/gtkb-loyal-opposition-runbook.md","config/agent-control/gtkb-loyal-opposition.md","config/agent-control/gtkb-operating-model.md","config/agent-control/gtkb-operating-role.md","config/agent-control/gtkb-pb-startup-overlay.md","config/agent-control/gtkb-peer-solution-advisory-loop.md","config/agent-control/gtkb-prime-bridge-collaboration-protocol.md","config/agent-control/gtkb-prime-builder-role.md","config/agent-control/gtkb-prime-builder.md","config/agent-control/gtkb-project-resource-aliases.toml","config/agent-control/gtkb-project-root-boundary.md","config/agent-control/gtkb-report-depth-prime-builder-context.md","config/agent-control/gtkb-report-depth.md","config/agent-control/gtkb-review-checklists.md","config/agent-control/gtkb-review-gate.md","config/agent-control/gtkb-review-mode-setup.md","config/agent-control/gtkb-review-operating-contract.md","config/agent-control/gtkb-role-capability-manifest.md","config/agent-control/gtkb-session-bootstrap.md","config/agent-control/gtkb-session-startup-control-map.md","config/agent-control/gtkb-session-startup-index.md","config/agent-control/gtkb-skill-rename-map.toml","config/agent-control/gtkb-skill-scenarios.toml","config/agent-control/gtkb-sot-read-discipline.md","config/agent-control/gtkb-standing-priorities.md","config/agent-control/gtkb-system-interface-map.toml","config/agent-control/gtkb-template-code-review.md","config/agent-control/gtkb-template-decision-memo.md","config/agent-control/gtkb-unified-policy-registry.toml","config/agent-control/gtkb-vision.md","config/agent-control/gtkb-way-of-working.md","config/file-reference-migration/wi5640.toml","config/hooks/gtkb-advisory-router-scan.py","config/hooks/gtkb-assertion-check.py","config/hooks/gtkb-bridge-axis-2-surface.py","config/hooks/gtkb-bridge-compliance-gate.py","config/hooks/gtkb-bridge-proposal-wi-id-collision-gate.py","config/hooks/gtkb-code-quality-baseline-proposal-check.py","config/hooks/gtkb-credential-scan.py","config/hooks/gtkb-delib-search-gate.py","config/hooks/gtkb-delib-search-tracker.py","config/hooks/gtkb-destructive-gate.py","config/hooks/gtkb-directive-enforcement-claude-adapter.py","config/hooks/gtkb-document_author_provenance_gate.py","config/hooks/gtkb-formal-artifact-approval-gate.py","config/hooks/gtkb-glossary-expansion.py","config/hooks/gtkb-gov-capture.py","config/hooks/gtkb-implementation-start-gate.py","config/hooks/gtkb-intake-classifier.py","config/hooks/gtkb-lo-file-safety-gate.py","config/hooks/gtkb-narrative-artifact-approval-gate.py","config/hooks/gtkb-not-markdown.py","config/hooks/gtkb-owner-decision-capture.py","config/hooks/gtkb-owner-decision-tracker.py","config/hooks/gtkb-project-completion-surface.py","config/hooks/gtkb-scanner-safe-writer.py","config/hooks/gtkb-session-start-governance.py","config/hooks/gtkb-session-topic-envelope-router.py","config/hooks/gtkb-session_start_dispatch.py","config/hooks/gtkb-sot-read-discipline.py","config/hooks/gtkb-spec-before-code.py","config/hooks/gtkb-spec-classifier.py","config/hooks/gtkb-spec-event-surfacer.py","config/hooks/gtkb-workstream-focus.py","config/hooks/gtkb_delib_common.py","config/registry/sot-artifacts.toml","groundtruth.db","platform_tests/scripts/test_generate_codex_skill_adapters.py","platform_tests/scripts/test_generate_cursor_skill_adapters.py","platform_tests/scripts/test_generate_rule_compatibility_projections.py","platform_tests/scripts/test_gtkb_file_reference_migration.py","platform_tests/scripts/test_implementation_start_gate.py","scripts/generate_codex_skill_adapters.py","scripts/generate_cursor_skill_adapters.py","scripts/generate_rule_compatibility_projections.py","scripts/gtkb_file_reference_migration.py"]
input_paths: ["gtkb-file-move-and-rename-list.csv"]

implementation_scope: source | test | configuration | governance_evidence | kb_projection
requires_review: true
requires_verification: true
kb_mutation_in_scope: true

---

## Revision Response

This revision addresses every v002 NO-GO condition:

1. It binds the authoritative input as
   `gtkb-file-move-and-rename-list.csv`, byte length 10029, SHA-256
   `sha256:02dc582d27a31418c870bd86b39f160dde985400631b0bd692de84e58a9aa136`.
2. It embeds the exact 90-source/90-destination compatibility inventory and
   binds its canonical JSON to
   `sha256:f83dcc76aa32df6e019ac749ffa46b5e1531682c2c1650a48232411b73c854c3`.
3. It replaces every target wildcard with an exact Stage A path. Consumer
   writes are not authorized here; they require a child proposal whose inline
   target paths exactly equal the hash-bound Stage A plan write set.
4. It specifies the canonical registry transaction and projection evidence.
5. The post-implementation report is a strict Prime Builder `NEW` verification
   request, never `NO-ACTION`.
6. Terminal `VERIFIED` is permitted only through the governed commit-finalizer
   after the owner authorizes the two bounded local finalization commits.

## Summary

Repair forward from preserved incident commit
`db07f9dcfe7e7de8addc850729209278472cb0fe`. Stage A repairs the migration
planner and known candidate defects, admits the exact retained-source and
destination compatibility set to the canonical registry, synchronizes its
MemBase projection through the governed registry service, and produces a
blocked-by-default exact consumer plan. Stage A never applies consumer edits.

The existing preflight evidence is intentionally negative and establishes the
repair baseline: 13,866 inventory entries, 407 reference hits, 100 proposed
writes, 136 unresolved residuals, and 368 blockers. Eighty-four proposed writes
are Cursor outputs produced without a membership-closed split: they mix
declared harness surfaces with clearly unregistered helper/draft material. The
repair must retain only outputs resolved as registered after WI-5441 and reduce
the unregistered subset to zero.

## Exact Compatibility Inventory

The following JSON is generated mechanically from the CSV. Its arrays preserve
CSV order; all paths are normalized relative to `E:\\GT-KB`.

```json
{
  "schema_version": 1,
  "manifest_path": "gtkb-file-move-and-rename-list.csv",
  "manifest_sha256": "sha256:02dc582d27a31418c870bd86b39f160dde985400631b0bd692de84e58a9aa136",
  "row_count": 90,
  "source_count": 90,
  "destination_count": 90,
  "source_paths": [
    ".claude/hooks/_delib_common.py",
    ".claude/hooks/advisory-router-scan.py",
    ".claude/hooks/assertion-check.py",
    ".claude/hooks/bridge-axis-2-surface.py",
    ".claude/hooks/bridge-compliance-gate.py",
    ".claude/hooks/bridge-proposal-wi-id-collision-gate.py",
    ".claude/hooks/code-quality-baseline-proposal-check.py",
    ".claude/hooks/credential-scan.py",
    ".claude/hooks/delib-search-gate.py",
    ".claude/hooks/delib-search-tracker.py",
    ".claude/hooks/destructive-gate.py",
    ".claude/hooks/directive-enforcement-claude-adapter.py",
    ".claude/hooks/document_author_provenance_gate.py",
    ".claude/hooks/formal-artifact-approval-gate.py",
    ".claude/hooks/glossary-expansion.py",
    ".claude/hooks/gov09-capture.py",
    ".claude/hooks/implementation-start-gate.py",
    ".claude/hooks/intake-classifier.py",
    ".claude/hooks/kb-not-markdown.py",
    ".claude/hooks/lo-file-safety-gate.py",
    ".claude/hooks/narrative-artifact-approval-gate.py",
    ".claude/hooks/owner-decision-capture.py",
    ".claude/hooks/owner-decision-tracker.py",
    ".claude/hooks/spec-before-code.py",
    ".claude/hooks/project-completion-surface.py",
    ".claude/hooks/scanner-safe-writer.py",
    ".claude/hooks/session_start_dispatch.py",
    ".claude/hooks/session-start-governance.py",
    ".claude/hooks/session-topic-envelope-router.py",
    ".claude/hooks/sot-read-discipline.py",
    ".claude/hooks/spec-classifier.py",
    ".claude/hooks/spec-event-surfacer.py",
    ".claude/hooks/workstream-focus.py",
    ".claude/rules/acting-prime-builder.md",
    ".claude/rules/active-workspace.md",
    ".claude/rules/auto-finalization-sweep.md",
    ".claude/rules/backlog-approval-state.md",
    ".claude/rules/bridge-essential.md",
    ".claude/rules/bridge-permanent-operations-runbook.md",
    ".claude/rules/bridge-poller-canonical.md",
    ".claude/rules/canonical-terminology.md",
    ".claude/rules/canonical-terminology.toml",
    ".claude/rules/codex-dead-ends-and-false-positives.md",
    ".claude/rules/codex-decision-ledger.md",
    ".claude/rules/codex-knowledge-base-index.md",
    ".claude/rules/codex-loyal-opposition-runbook.md",
    ".claude/rules/codex-review-checklists.md",
    ".claude/rules/codex-review-gate.md",
    ".claude/rules/codex-review-operating-contract.md",
    ".claude/rules/codex-session-bootstrap.md",
    ".claude/rules/codex-standing-priorities.md",
    ".claude/rules/codex-way-of-working.md",
    ".claude/rules/deliberation-protocol.md",
    ".claude/rules/dispatcher-daemon-substrate-rollback-runbook.md",
    ".claude/rules/file-bridge-protocol.md",
    ".claude/rules/governance-emergency-bootstrap-protocol.md",
    ".claude/rules/groundtruth-kb-vision.md",
    ".claude/rules/gtkb-capability-import-policy.md",
    ".claude/rules/loyal-opposition.md",
    ".claude/rules/operating-model.md",
    ".claude/rules/operating-role.md",
    ".claude/rules/peer-solution-advisory-loop.md",
    ".claude/rules/prime-bridge-collaboration-protocol.md",
    ".claude/rules/prime-builder.md",
    ".claude/rules/prime-builder-role.md",
    ".claude/rules/project-root-boundary.md",
    ".claude/rules/report-depth.md",
    ".claude/rules/report-depth-prime-builder-context.md",
    ".claude/rules/sot-read-discipline.md",
    ".claude/rules/template-code-review.md",
    ".claude/rules/template-decision-memo.md",
    "config/agent-control/activity-disposition-profiles.toml",
    "config/agent-control/activity-envelope-sharding.toml",
    "config/agent-control/auq-policy-gates.toml",
    "config/agent-control/command-surface.toml",
    "config/agent-control/CONTROL-MAP.md",
    "config/agent-control/declarative-agent-role-manifest.yaml",
    "config/agent-control/harness-capability-registry.toml",
    "config/agent-control/harness-model-pin-confirmations.toml",
    "config/agent-control/skill-scenarios.toml",
    "config/agent-control/LOYAL-OPPOSITION-STARTUP-OVERLAY.md",
    "config/agent-control/PRIME-BUILDER-STARTUP-OVERLAY.md",
    "config/agent-control/project-resource-aliases.toml",
    "config/agent-control/REVIEW-MODE-SETUP.md",
    "config/agent-control/ROLE-CAPABILITY-MANIFEST.md",
    "config/agent-control/SESSION-STARTUP-CONTROL-MAP.md",
    "config/agent-control/SESSION-STARTUP-INDEX.md",
    "config/agent-control/skill-rename-map.toml",
    "config/agent-control/system-interface-map.toml",
    "config/agent-control/unified-policy-registry.toml"
  ],
  "destination_paths": [
    "config/hooks/gtkb_delib_common.py",
    "config/hooks/gtkb-advisory-router-scan.py",
    "config/hooks/gtkb-assertion-check.py",
    "config/hooks/gtkb-bridge-axis-2-surface.py",
    "config/hooks/gtkb-bridge-compliance-gate.py",
    "config/hooks/gtkb-bridge-proposal-wi-id-collision-gate.py",
    "config/hooks/gtkb-code-quality-baseline-proposal-check.py",
    "config/hooks/gtkb-credential-scan.py",
    "config/hooks/gtkb-delib-search-gate.py",
    "config/hooks/gtkb-delib-search-tracker.py",
    "config/hooks/gtkb-destructive-gate.py",
    "config/hooks/gtkb-directive-enforcement-claude-adapter.py",
    "config/hooks/gtkb-document_author_provenance_gate.py",
    "config/hooks/gtkb-formal-artifact-approval-gate.py",
    "config/hooks/gtkb-glossary-expansion.py",
    "config/hooks/gtkb-gov-capture.py",
    "config/hooks/gtkb-implementation-start-gate.py",
    "config/hooks/gtkb-intake-classifier.py",
    "config/hooks/gtkb-not-markdown.py",
    "config/hooks/gtkb-lo-file-safety-gate.py",
    "config/hooks/gtkb-narrative-artifact-approval-gate.py",
    "config/hooks/gtkb-owner-decision-capture.py",
    "config/hooks/gtkb-owner-decision-tracker.py",
    "config/hooks/gtkb-spec-before-code.py",
    "config/hooks/gtkb-project-completion-surface.py",
    "config/hooks/gtkb-scanner-safe-writer.py",
    "config/hooks/gtkb-session_start_dispatch.py",
    "config/hooks/gtkb-session-start-governance.py",
    "config/hooks/gtkb-session-topic-envelope-router.py",
    "config/hooks/gtkb-sot-read-discipline.py",
    "config/hooks/gtkb-spec-classifier.py",
    "config/hooks/gtkb-spec-event-surfacer.py",
    "config/hooks/gtkb-workstream-focus.py",
    "config/agent-control/gtkb-acting-prime-builder.md",
    "config/agent-control/gtkb-active-workspace.md",
    "config/agent-control/gtkb-auto-finalization-sweep.md",
    "config/agent-control/gtkb-backlog-approval-state.md",
    "config/agent-control/gtkb-bridge-essential.md",
    "config/agent-control/gtkb-bridge-permanent-operations-runbook.md",
    "config/agent-control/gtkb-bridge-poller-canonical.md",
    "config/agent-control/gtkb-canonical-terminology.md",
    "config/agent-control/gtkb-canonical-terminology.toml",
    "config/agent-control/gtkb-dead-ends-and-false-positives.md",
    "config/agent-control/gtkb-decision-ledger.md",
    "config/agent-control/gtkb-knowledge-base-index.md",
    "config/agent-control/gtkb-loyal-opposition-runbook.md",
    "config/agent-control/gtkb-review-checklists.md",
    "config/agent-control/gtkb-review-gate.md",
    "config/agent-control/gtkb-review-operating-contract.md",
    "config/agent-control/gtkb-session-bootstrap.md",
    "config/agent-control/gtkb-standing-priorities.md",
    "config/agent-control/gtkb-way-of-working.md",
    "config/agent-control/gtkb-deliberation-protocol.md",
    "config/agent-control/gtkb-dispatcher-daemon-substrate-rollback-runbook.md",
    "config/agent-control/gtkb-file-bridge-protocol.md",
    "config/agent-control/gtkb-governance-emergency-bootstrap-protocol.md",
    "config/agent-control/gtkb-vision.md",
    "config/agent-control/gtkb-capability-import-policy.md",
    "config/agent-control/gtkb-loyal-opposition.md",
    "config/agent-control/gtkb-operating-model.md",
    "config/agent-control/gtkb-operating-role.md",
    "config/agent-control/gtkb-peer-solution-advisory-loop.md",
    "config/agent-control/gtkb-prime-bridge-collaboration-protocol.md",
    "config/agent-control/gtkb-prime-builder.md",
    "config/agent-control/gtkb-prime-builder-role.md",
    "config/agent-control/gtkb-project-root-boundary.md",
    "config/agent-control/gtkb-report-depth.md",
    "config/agent-control/gtkb-report-depth-prime-builder-context.md",
    "config/agent-control/gtkb-sot-read-discipline.md",
    "config/agent-control/gtkb-template-code-review.md",
    "config/agent-control/gtkb-template-decision-memo.md",
    "config/agent-control/gtkb-activity-disposition-profiles.toml",
    "config/agent-control/gtkb-activity-envelope-sharding.toml",
    "config/agent-control/gtkb-auq-policy-gates.toml",
    "config/agent-control/gtkb-command-surface.toml",
    "config/agent-control/gtkb-control-map.md",
    "config/agent-control/gtkb-declarative-agent-role-manifest.yaml",
    "config/agent-control/gtkb-harness-capability-registry.toml",
    "config/agent-control/gtkb-harness-model-pin-confirmations.toml",
    "config/agent-control/gtkb-skill-scenarios.toml",
    "config/agent-control/gtkb-lo-startup-overlay.md",
    "config/agent-control/gtkb-pb-startup-overlay.md",
    "config/agent-control/gtkb-project-resource-aliases.toml",
    "config/agent-control/gtkb-review-mode-setup.md",
    "config/agent-control/gtkb-role-capability-manifest.md",
    "config/agent-control/gtkb-session-startup-control-map.md",
    "config/agent-control/gtkb-session-startup-index.md",
    "config/agent-control/gtkb-skill-rename-map.toml",
    "config/agent-control/gtkb-system-interface-map.toml",
    "config/agent-control/gtkb-unified-policy-registry.toml"
  ]
}
```

## Stage A Exact Write Boundary

- Canonical JSON of the exact Stage A target array plus one LF is bound to
  `sha256:480d71e3624303acebeba82e1d598c33555ea88ebf1b7584fafcd6eed7687af8`.
- The inline `target_paths` is the complete Stage A write authority. It
  contains the 90 exact destinations plus the exact migration, registry,
  generator, canonical skill, generated Codex adapter, and test paths that may
  require repair. The 90 source paths are read/retention inputs, not Stage A
  write authority.
- Runtime preflight payloads under
  `.gtkb-state/file-reference-migration/wi5640/` are disposable derived state,
  not canonical evidence and not consumer-write authority.
- A required repository write outside inline `target_paths` fails closed.
- Stage A output includes an exact child `target_paths` JSON array and SHA-256.
  The child thread is
  `gtkb-file-move-rename-canonicalization-repair-forward-exact-plan`.
- The child proposal must cite the Stage A plan hash, inventory fingerprint,
  closure fingerprint, preimage-set hash, and exact target array. It receives
  independent GO before `apply`; no wildcard is permitted.

## Implementation Procedure

### Gate 0 - Current authority and registry readiness

1. Require strict lifecycle `NEW -> NO-GO -> REVISED -> GO`, current-session
   work-intent claim, active PAUTH, and exact implementation-start packet.
2. Require the WI-5441 control plane to be implemented and independently
   VERIFIED, including `gt registry register`, lock/journal recovery,
   declaration/projection atomicity, observed revisions, and reverse-coverage
   validation. A `resolved` backlog label or 50/50 declaration parity is not
   readiness evidence: the live command surface currently has no mutation API,
   and 0/90 destinations are registered.
3. Require a fresh `gt registry validate --json` result that includes reverse
   coverage and reports zero unknown paths, zero unregistered load-bearing
   paths, zero stale observed revisions, and no incomplete transaction. The
   current parity-only validator does not satisfy this gate.
4. Recompute the CSV and compatibility-inventory hashes. Any mismatch stops.

### Gate 1 - Planner and candidate repair

1. Change the policy's main bridge ID to this repair-forward thread and its
   child bridge ID to the exact-plan child. The old v4 chain remains history.
2. Make every generator action registry-constrained. No unregistered Cursor,
   Codex, Claude, API, Goose, or other generated output may enter the plan.
3. Remove generated/draft helper detritus from generator inputs. It is
   disposable and must not be copied merely because it exists.
4. Repair the malformed activity-envelope TOML, stale canonical `gtkb-bridge`
   skill references, the byte-divergent `impl_report_bridge.py` and
   `revise_bridge.py` Codex mirrors, the independently observed
   `gtkb-proposal-review`, `gtkb-send-review`, and `gtkb-verify` Codex drift,
   and the missing-Version test fixtures. Production gate semantics are not
   weakened.
5. Add regression tests proving unregistered generator outputs cannot become
   writes and broad globs cannot enter child authority.

### Gate 2 - Canonical registry transaction

1. Invoke the implemented canonical `gt registry register` transaction surface;
   direct TOML edits, `gt registry sync` after a direct edit, and raw SQLite are
   forbidden implementation routes. If the command, lock, journal, observation,
   or recovery contract is unavailable, Stage A halts without a fallback.
2. In one registry transaction, preserve existing IDs and register only missing
   records among the exact manifest input, 90 retained sources, and 90
   destinations. Duplicate storage paths or concurrent registry revision drift
   abort the transaction.
3. The service writes the TOML declaration and root `groundtruth.db` projection,
   records transaction/observation evidence and a deterministic receipt, and
   validates declaration/projection parity and revision freshness before
   success.
4. Require each of the 181 governed input/compatibility paths to resolve exactly
   once through the canonical reader. No source record is retired while the
   source remains retained.

### Gate 3 - Deterministic exact-plan production

1. Run preflight and plan from fresh processes over canonical registered
   inventory only. Expand only registry-declared exact, directory, glob,
   opaque, virtual, and MemBase locators according to their canonical schema.
2. Detect direct and normalized paths, decoded structured values, Python
   literals, PowerShell segments, and registered MemBase text. Audit trails are
   counted but immutable; unregistered artifacts are ignored as disposable.
3. Require zero blockers and zero unresolved live residuals before plan
   publication. Emit exact child target array, write-set hash, plan hash,
   inventory and closure fingerprints, preimage hash, exclusions, and reasons.
4. Do not call `apply`, `rollback`, or bind an implementation packet in Stage A.

### Gate 4 - Strict implementation report and finalization

1. File the next Prime Builder version with first-line status `NEW` as the
   Stage A implementation report and verification request. Carry forward the
   specification-to-test mapping, exact commands/results, hashes, changed
   paths, and negative assertions.
2. Independent LO either files `NO-GO` or uses the governed
   `--finalize-verified` helper. A file-only `VERIFIED` is invalid.
3. Finalization stages only the reviewed Stage A implementation paths, the
   strict post-implementation report, the new VERIFIED verdict, and any then-
   uncommitted chain versions required as governance evidence. Versions 001 and
   002 already preserved in packaging commit `6d6bc663c` are not fabricated as
   new changes. The finalizer creates one local commit and performs no push.
4. The exact-plan child repeats this lifecycle for consumer apply and its second
   bounded local finalization commit.

## Finalization Authorization

Pending explicit owner decision. Proposed authority: two local commits, one for independently VERIFIED Stage A and one for the independently VERIFIED exact-plan child, each created only by the governed finalizer with its reviewed exact include list.

No implementation may begin while that authority is pending. No push, release,
deployment, deletion, history rewrite, or credential operation is requested.

## Cross-Harness Disposition

- Claude canonical skill sources are repaired directly.
- Codex copies are regenerated from canonical sources and checked byte-for-byte
  where the adapter contract requires it.
- Cursor generation is tested but produces no write unless the exact output is
  resolved as a registered artifact. The unregistered subset of the current 84
  mixed Cursor outputs must disappear; registered outputs require exact scope.
- Other harnesses receive no write under Stage A. No waiver is requested.

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-5640; DELIB-20260724-WI5640-REPAIR-FORWARD; DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION; bridge/gtkb-file-move-rename-canonicalization-repair-forward-002.md",
  "canonical_authority": "GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001, GOV-PLATFORM-SOT-REGISTRY-001, DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001, DCL-SOT-REGISTRY-PROJECTION-PARITY-001, and GOV-FILE-BRIDGE-AUTHORITY-001",
  "primary_route": "REVISED proposal, independent GO, exact Stage A implementation, strict NEW report, governed VERIFIED finalization commit, then an independently reviewed exact-plan child.",
  "before_behavior": "The candidate commit is preserved but unauthorized; the registry has 50 records and no destinations; current preflight has 368 blockers and proposes 84 Cursor writes without a membership-closed registered/unregistered split.",
  "after_behavior": "Stage A has an exact reviewed diff, 181 governed manifest and compatibility paths resolve once, unregistered generator writes are zero, and a hash-bound exact consumer plan awaits child review.",
  "self_descriptive_naming": "The repair-forward main and exact-plan child slugs, WI-5640 policy, registry records, and evidence hashes state their role.",
  "obsolete_guidance_disposition": "Old v4 bridge/config authority is replaced prospectively in the policy; audit history remains immutable; unregistered generated debris is ignored.",
  "history_preservation": "Commit db07f9dc, all numbered bridge versions, owner decisions, MemBase versions, and all 90 old source files remain preserved.",
  "baseline": {
    "current_head": "6d6bc663cc20d4d5777688c7845b0810cd387c69 (bridge packaging only)",
    "incident_commit": "db07f9dcfe7e7de8addc850729209278472cb0fe",
    "manifest_sha256": "sha256:02dc582d27a31418c870bd86b39f160dde985400631b0bd692de84e58a9aa136",
    "compatibility_inventory_sha256": "sha256:f83dcc76aa32df6e019ac749ffa46b5e1531682c2c1650a48232411b73c854c3",
    "preflight": "inventory=13866; hits=407; writes=100; unresolved=136; blockers=368",
    "registry": "TOML=50; projection=50; destinations=0"
  },
  "expected_result": {
    "stage_a": "zero blockers, zero unresolved live residuals, zero unregistered generator writes",
    "registry": "manifest plus 180 compatibility paths resolve once with projection parity",
    "plan": "exact child target array and all required deterministic hashes",
    "lifecycle": "strict NEW implementation report followed by governed commit-finalized review"
  },
  "rollback": {
    "instructions": "Abort the registry transaction before publication on any mismatch; before terminal verification restore reviewed Stage A preimages without rewriting existing history.",
    "verification": "Rerun registry parity, exact 181-path resolution, all focused tests, Ruff gates, TOML parse, and two fresh-process plans."
  },
  "hard_invariants": [
    "No consumer apply in Stage A and no wildcard target authority.",
    "No unregistered artifact may enter generator or consumer write sets.",
    "No direct raw SQLite or ad hoc registry-file mutation.",
    "All 90 old sources remain present and registered during compatibility retention.",
    "No file-only VERIFIED, deletion, history rewrite, push, release, or deployment."
  ],
  "fail_closed_conditions": [
    "Any lifecycle, claim, PAUTH, implementation-start, owner-finalization, registry-readiness, or project-root evidence is absent.",
    "CSV, compatibility inventory, registry revision, plan, write-set, preimage, inventory, or closure hash differs.",
    "A generator proposes an unregistered output or a required write is outside exact target paths.",
    "Any blocker or unresolved live residual remains when the exact plan is published.",
    "Any old source is absent or any audit-history record is selected for rewrite."
  ],
  "essential_context_preservation": "Preserve the owner repair-forward decision, registry-only membership rule, prior NO-GO evidence, exact input hashes, old-source retention, child-plan review boundary, and commit-finalized terminal semantics."
}
```

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - strict lifecycle, role authority, exact
  implementation gate, and append-only bridge evidence.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` - prohibits using `NO-ACTION` as an
  implementation report.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - project, PAUTH, and WI.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - concrete links.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - exact test mapping.
- `GOV-PLATFORM-SOT-REGISTRY-001` - exclusive artifact membership authority.
- `DCL-SOT-REGISTRY-PROJECTION-PARITY-001` - TOML/projection transaction parity.
- `DCL-ARTIFACT-REGISTRY-MUTATION-AUTHORIZATION-001` - registration and
  retained compatibility mutation authority.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` - source retention and rollback.
- `ADR-CROSS-HARNESS-PARITY-001` and
  `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` - canonical/generated parity.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`,
  `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, and
  `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - durable plan/report lifecycle.

## Prior Deliberations

- `DELIB-20260724-WI5640-REPAIR-FORWARD` - preserve the incident commit and
  recover through a fresh bounded chain.
- `DELIB-20260722-WI5640-OBSOLETE-FILE-RETENTION` - retain all old sources;
  deletion is a separate operation.
- `DELIB-202666274`, `DELIB-202667191`, and `DELIB-202667182` - active project
  authorization evidence and exclusions.
- `bridge/gtkb-file-move-rename-canonicalization-repair-forward-002.md` - the
  controlling NO-GO corrected by this revision.

## Owner Decisions / Input

Repair-forward and source retention are authorized by the cited deliberations.
The two local VERIFIED finalization commits require the explicit owner decision
record named in `Finalization Authorization`; no implementation starts before
that record exists.

## Requirement Sufficiency

The specified governance requirements are sufficient for Stage A, but their
required registry control plane is not yet implemented in the current tree.
Execution readiness additionally requires the owner finalization decision and
independently VERIFIED WI-5441 CLI/reconciliation implementation; neither a
backlog status nor parity-only validation is accepted as a waiver.

## Spec-Derived Verification Plan

1. Lifecycle and scope: strict resolver, applicability preflight, clause
   preflight, PAUTH check, claim check, and implementation-start check for every
   exact target. Expected: all pass; no wildcard or unmatched path.
2. Input inventory: independently recompute CSV byte hash, cardinality,
   uniqueness, exact 180-path inventory hash, and path presence. Expected:
   stated hashes, 90/90 unique paths, all 180 present.
3. Registry transaction: exercised `gt registry register`, lock/journal fault
   recovery, observed-revision validation, and canonical
   `load_toml`/`load_projection` comparison. Expected: all exact 181 paths
   resolve once; zero duplicates, unknowns, unregistered load-bearing paths,
   stale revisions, incomplete transactions, or field divergence.
4. Planner tests: focused migration, rule/Cursor/Codex generator, and
   implementation-start suites. Expected: all pass, including registry-only
   generator filtering and missing-Version fixtures.
5. Planner execution: two fresh-process preflight/plan runs. Expected: zero
   blockers, zero unresolved live residuals, identical fingerprints and exact
   write set, zero unregistered writes, and no apply transaction.
6. Syntax/quality: parse all exact TOML targets; Ruff check and format-check all
   exact changed Python paths. Expected: all pass.
7. Finalization: independent LO invokes only the governed VERIFIED finalizer
   with the exact reviewed include list. Expected: one local commit containing
   implementation, complete bridge chain/report/verdict, and no unrelated path.

## Risk / Rollback

The main risks are treating resolved WI-5441 metadata as registry completeness,
copying unregistered generated debris, widening target authority, colliding
with a concurrent registry transaction, and filing a non-committed VERIFIED.
Every risk is a named fail-closed condition. Stage A is reversible from exact
preimages and registry transaction evidence; existing history is never reset.

## Recommended Commit Type

`fix(gtkb): repair WI-5640 migration planning and registry admission`

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
