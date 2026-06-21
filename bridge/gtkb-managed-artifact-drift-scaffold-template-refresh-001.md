NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Implementation Proposal - Resolve perpetual managed-artifact drift=8 WARN: refresh scaffold templates FROM live platform hooks/rules (templates lag live)

bridge_kind: prime_proposal
Document: gtkb-managed-artifact-drift-scaffold-template-refresh
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-4630

target_paths: ["groundtruth-kb/templates/hooks/assertion-check.py", "groundtruth-kb/templates/hooks/spec-classifier.py", "groundtruth-kb/templates/hooks/destructive-gate.py", "groundtruth-kb/templates/hooks/credential-scan.py", "groundtruth-kb/templates/hooks/spec-event-surfacer.py", "groundtruth-kb/templates/rules/file-bridge-protocol.md", "groundtruth-kb/templates/rules/bridge-essential.md", "groundtruth-kb/templates/rules/deliberation-protocol.md", "groundtruth-kb/tests/test_doctor_registry_parity.py"]

Implementation proposal for a bounded code or platform change.

## Claim

`gt project doctor` perpetually reports `Managed artifact drift` as WARN with `current=6, drifted=8` for the GT-KB `dual-agent` checkout because eight `gt-kb-managed` scaffold templates have fallen far behind their live `.claude/` copies. The live platform hooks and rules have evolved through many bridge cycles while their `groundtruth-kb/templates/...` source templates were not kept in lockstep, so `_check_managed_artifact_drift` (which hashes each live `target_path` against its `template_path`) flags all eight. The defect is template staleness, not doctor logic: refreshing the eight template files FROM the current live files clears the WARN without regressing live behavior, and a byte-parity regression test prevents the drift from silently reaccumulating.

## Requirement Sufficiency

Existing requirements sufficient. The governing specs already require scaffold templates to be the authoritative source for `gt-kb-managed` artifacts and to remain consistent with the live framework surface (`GOV-FILE-BRIDGE-AUTHORITY-001`, `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`). The directly-analogous precedent `gtkb-wi4672-bridge-compliance-gate-template-parity` (GO at `-002`, VERIFIED) refreshed one managed hook template from its live copy and added a byte-parity test under the same specs with no new/revised requirement; this WI applies the identical pattern to the remaining eight drifted artifacts. No new or revised requirement/specification is introduced.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `groundtruth-kb/templates/hooks/assertion-check.py`, `groundtruth-kb/templates/hooks/spec-classifier.py`, `groundtruth-kb/templates/hooks/destructive-gate.py`, `groundtruth-kb/templates/hooks/credential-scan.py`, `groundtruth-kb/templates/hooks/spec-event-surfacer.py`, `groundtruth-kb/templates/rules/file-bridge-protocol.md`, `groundtruth-kb/templates/rules/bridge-essential.md`, `groundtruth-kb/templates/rules/deliberation-protocol.md`, `groundtruth-kb/tests/test_doctor_registry_parity.py`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - the eight artifacts include the bridge surface itself (`rules/file-bridge-protocol.md`, `rules/bridge-essential.md`); refreshing their templates keeps the canonical bridge-protocol scaffold consistent with the live bridge authority that adopters inherit.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the fix preserves the durable artifact (scaffold template) as the authoritative source by reconciling it with the live framework surface rather than letting two divergent copies persist.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all governing specs (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan derives a byte-parity regression test from the cited template-consistency specs (mandatory).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries Project Authorization / Project / Work Item linkage lines (mandatory).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the change is confined to the GT-KB platform package (`groundtruth-kb/templates/...`, `groundtruth-kb/tests/...`); no adopter/application subtree is touched and no placement boundary is crossed.
- `GOV-STANDING-BACKLOG-001` - WI-4630 is a standing-backlog work item under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - five of the eight artifacts are hooks delivered into the dual-harness boundary; refreshing the hook templates keeps the scaffolded hook surface consistent with the live hook contract that the Claude/Codex parity model depends on.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the template/live reconciliation keeps the managed-artifact state artifact-backed (template file == live file) rather than inferred or divergent.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the new byte-parity test wires the template-refresh lifecycle to a deterministic regression trigger so future divergence is caught instead of perpetually warning.

## Prior Deliberations

- `DELIB-20260602-GLOSSARY-CLI-SCAN-LIVE-PLUS-TEMPLATES` - established the "live plus templates" propagation discipline (changes that touch a live framework surface must also reach the scaffold templates); this WI applies that discipline retroactively to eight artifacts whose templates lagged.
- `DELIB-20260719` / `DELIB-20261296` - WI-4225 Scaffold Golden Fixture Regen VERIFIED-010: prior precedent for regenerating scaffold-source artifacts from authoritative state and locking them with a regression guard.
- `DELIB-20264976` - GT-KB Upgrade Pre-Flight Checks Scope Review: context that `gt project upgrade --apply --force` would push stale templates DOWN onto live files (regression); the WI direction explicitly forbids that path and refreshes templates UP from live instead.
- The directly-analogous WI-4672 thread (`bridge/gtkb-wi4672-bridge-compliance-gate-template-parity-002.md`, GO/VERIFIED) refreshed one managed hook template from live and added a CRLF-normalized byte-parity test; this proposal reuses that exact pattern and assertion idiom for the remaining eight artifacts.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` - project-scoped authorization envelope covering the PROJECT-GTKB-RELIABILITY-FIXES non-fast-lane proposal batch; WI-4630 is an in-scope reliability defect/improvement under this PAUTH, so bounded implementation is authorized once Loyal Opposition records GO.
- `DELIB-20265457` - owner AUQ (2026-06-21) authorizing this PROJECT-GTKB-RELIABILITY-FIXES batch and directing authoring of NEW proposals for the open reliability work items; WI-4630 is one of the batch items.

## Proposed Scope

1. Overwrite each of the eight stale scaffold templates with the exact current content of its live `.claude/` counterpart so `template_path` content == `target_path` content for each `gt-kb-managed` doctor-required artifact:
   - `groundtruth-kb/templates/hooks/assertion-check.py` <- `.claude/hooks/assertion-check.py`
   - `groundtruth-kb/templates/hooks/spec-classifier.py` <- `.claude/hooks/spec-classifier.py`
   - `groundtruth-kb/templates/hooks/destructive-gate.py` <- `.claude/hooks/destructive-gate.py`
   - `groundtruth-kb/templates/hooks/credential-scan.py` <- `.claude/hooks/credential-scan.py`
   - `groundtruth-kb/templates/hooks/spec-event-surfacer.py` <- `.claude/hooks/spec-event-surfacer.py`
   - `groundtruth-kb/templates/rules/file-bridge-protocol.md` <- `.claude/rules/file-bridge-protocol.md`
   - `groundtruth-kb/templates/rules/bridge-essential.md` <- `.claude/rules/bridge-essential.md`
   - `groundtruth-kb/templates/rules/deliberation-protocol.md` <- `.claude/rules/deliberation-protocol.md`
   The copy is content-only (live -> template); no live file is modified. Direction is strictly UP (live is authoritative); `gt project upgrade --apply --force` (which would push stale templates down onto live) MUST NOT be run.
2. Apply line-ending normalization so the refreshed templates use the repository's canonical newline style (LF) and pass `ruff format --check` for the two `.py` template files. (Templates are byte-compared CRLF-normalized in the new test, matching the WI-4672 `_file_sha256` idiom, but the committed templates should be LF-normalized to match repo convention.)
3. Add a byte-parity regression test to `groundtruth-kb/tests/test_doctor_registry_parity.py` (see verification plan) that asserts, for each of the eight `gt-kb-managed` doctor-required artifacts, that the template file content matches the live `.claude/` file content (CRLF-normalized), so future divergence fails a deterministic test rather than re-accumulating as a perpetual WARN.

This is the WI's primary direction (refresh templates FROM live). The WI's rejected alternative (running `gt project upgrade --apply --force` to converge the files) is explicitly out of scope because it regresses live behavior to the stale templates.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` / `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` (scaffold template is authoritative and consistent with the live surface) | `test_managed_artifact_templates_match_live[<artifact-id>]` (parametrized over the 8 artifacts) | For each of the eight `gt-kb-managed` doctor-required artifacts, the CRLF-normalized sha256 of `groundtruth-kb/templates/<template_path>` equals that of `.claude/<target_path>`. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` (drift trigger is deterministic, not perpetual WARN) | `test_managed_artifact_drift_clears_for_refreshed_artifacts` | `doctor._check_managed_artifact_drift(REPO_ROOT, "dual-agent")` reports no `drifted` entry for any of the eight refreshed artifact IDs (message no longer contains `drifted=8`). |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` / `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (no regression to live hook/rule behavior) | `test_managed_artifact_refresh_leaves_live_files_unchanged` | The eight live `.claude/` files are byte-identical to their pre-change `git HEAD` blobs (refresh is template-only; live surface, including the hook parity contract, is untouched). |

Execution commands:
- `python -m pytest groundtruth-kb/tests/test_doctor_registry_parity.py -q --tb=short`
- `python -m ruff check groundtruth-kb/templates/hooks/assertion-check.py groundtruth-kb/templates/hooks/spec-classifier.py groundtruth-kb/templates/hooks/destructive-gate.py groundtruth-kb/templates/hooks/credential-scan.py groundtruth-kb/templates/hooks/spec-event-surfacer.py groundtruth-kb/tests/test_doctor_registry_parity.py`
- `python -m ruff format --check groundtruth-kb/templates/hooks/assertion-check.py groundtruth-kb/templates/hooks/spec-classifier.py groundtruth-kb/templates/hooks/destructive-gate.py groundtruth-kb/templates/hooks/credential-scan.py groundtruth-kb/templates/hooks/spec-event-surfacer.py groundtruth-kb/tests/test_doctor_registry_parity.py`

(`ruff` is run only on the five `.py` templates and the test; the three `.md` rule templates are not Python and are verified by the byte-parity test.)

## Acceptance Criteria

1. `gt project doctor` for the GT-KB `dual-agent` checkout no longer reports `drifted` for the eight artifacts; `Managed artifact drift` reports `current=14` (the previous 6 current + 8 refreshed) and status is no longer WARN on account of these artifacts.
2. Each of the eight refreshed templates matches its live `.claude/` counterpart (CRLF-normalized byte parity).
3. No live `.claude/` file is modified (template-only change; live hook/rule behavior unchanged).
4. The new parametrized parity test and the two companion tests pass; `ruff check` and `ruff format --check` are clean on the five changed `.py` templates and the test file.

## Risks / Rollback

- Risk: a live file is itself non-canonical (e.g., contains a transient local edit) and the refresh propagates it into the template. Mitigation: the eight live files are tracked, committed framework surfaces under `.claude/` (negated from the blanket ignore per `bridge-essential.md` S294 lesson); the refresh copies the committed live content, and Loyal Opposition verification inspects the diff for any non-canonical content before VERIFIED.
- Risk: line-ending churn (CRLF vs LF) inflates the diff or breaks `ruff format --check`. Mitigation: normalize the refreshed templates to LF; the parity test compares CRLF-normalized content so it is newline-insensitive, matching the WI-4672 idiom.
- Risk: over-broad refresh accidentally touches templates not in the drift set. Mitigation: scope is fixed to the exact eight `target_paths`; the parity test enumerates exactly those eight artifact IDs.
- Rollback: revert the eight template files and the test addition. The change is content-only with no schema, registry, or live-surface change and is fully reversible with no migration.

## Files Expected To Change

- `groundtruth-kb/templates/hooks/assertion-check.py`
- `groundtruth-kb/templates/hooks/spec-classifier.py`
- `groundtruth-kb/templates/hooks/destructive-gate.py`
- `groundtruth-kb/templates/hooks/credential-scan.py`
- `groundtruth-kb/templates/hooks/spec-event-surfacer.py`
- `groundtruth-kb/templates/rules/file-bridge-protocol.md`
- `groundtruth-kb/templates/rules/bridge-essential.md`
- `groundtruth-kb/templates/rules/deliberation-protocol.md`
- `groundtruth-kb/tests/test_doctor_registry_parity.py`

## Recommended Commit Type

`fix`
