---
Status: NEW
Author: prime-builder (claude harness B)
Date: 2026-05-14
Session: S350
Source: GTKB-COMMIT-SCOPE-BUNDLING-DETECTION-001 (Pre-commit predicate to detect cross-scope bundling via mismatched approval-packet manifest)
Recommended commit type: feat
bridge_kind: prime_proposal
target_paths: ["scripts/check_commit_scope_bundling.py", "platform_tests/scripts/test_check_commit_scope_bundling.py"]
---

Document: gtkb-commit-scope-bundling-detection-slice-1

## Summary

Add a deterministic, read-only pre-commit predicate `scripts/check_commit_scope_bundling.py` that inspects the staged-file set, looks up matching formal-artifact-approval packets under `.groundtruth/formal-artifact-approvals/`, computes the per-file scope-identity union, and emits a structured diagnostic when the staged set spans more than one approval scope OR contains protected staged paths with no covering approval scope. Slice 1 is **WARN-only**: the predicate prints a finding to stderr and exits `0` so commits are not blocked. Block-mode escalation is deferred to Slice 2 (a separate bridge thread) after Slice 1 produces real-world false-positive/false-negative evidence.

Scope-identity per packet is the deterministic tuple `(deliberation_id?, spec_id?, bridge_thread_slug?, source_ref)` derived from the packet's `source_ref`, `change_reason`, and `artifact_id` fields. Two staged files share a scope when their matched packets yield equal scope-identity tuples; they bundle different scopes when the tuples differ. Files with no matching packet are counted in a separate `unscoped_paths` bucket and are only flagged when they intersect the protected-narrative-artifact pattern set (per `config/governance/narrative-artifact-approval.toml`) — bulk source/test/script edits without a narrative-artifact packet are out of scope for Slice 1.

The predicate has NO write side effects, makes NO MemBase mutations, and depends only on `git diff --cached --name-only` plus filesystem reads under `.groundtruth/formal-artifact-approvals/` and `config/governance/`. It will be wired into `.githooks/pre-commit` as a non-blocking warn step ordered AFTER the existing universal-floor `check_narrative_artifact_evidence.py` gate.

Empirical motivation: commit `5611dc44` (S344) bundled DELIB-S344 scope (`scripts/archive/record_delib_s344_spec_expressions_triangulation.py`) with S343 scope (`memory/work_list.md` row added via the S343 bridge-protocol-guide entry); the existing `check_narrative_artifact_evidence.py` predicate passed because each staged path had its own packet, but no predicate observed that the *union* spanned two unrelated `source_ref` scopes. S333 audit FINDING-P0-001 (`bridge/gtkb-governance-hygiene-bundle-001.md`) describes the older sibling pattern (commit `721f7c69`'s ~13K LOC mis-labeled `chore`); commit-scope bundling and commit-type understatement are kin failure modes whose long-term remedy is mechanical detection.

## Specification Links

- GOV-FILE-BRIDGE-AUTHORITY-001 — live bridge/INDEX.md is authoritative; this proposal is filed through the file bridge.
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 — proposal cites every relevant governing specification (this section).
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — every acceptance criterion is covered by a spec-derived test (see § Test Mapping).
- GOV-STANDING-BACKLOG-001 — work item GTKB-COMMIT-SCOPE-BUNDLING-DETECTION-001 lives in the canonical MemBase backlog; this proposal does not bulk-mutate that backlog (see § Clause Scope Clarification).
- GOV-ARTIFACT-APPROVAL-001 — the new predicate is one of the supporting mechanisms that lets the approval-packet gate scale; the proposal does NOT bypass the existing approval-packet gate for any artifact class.
- DCL-ARTIFACT-APPROVAL-HOOK-001 — the approval-hook surface is preserved unchanged. The new predicate is a sibling read-only diagnostic, not a replacement for the existing hook gate.
- ADR-ISOLATION-APPLICATION-PLACEMENT-001 — all touched paths live within `E:\GT-KB` (`scripts/` and `platform_tests/scripts/`); no application-directory writes.
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 — the predicate preserves traceability across staged paths, approval packets, deliberations, and bridge threads.
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 — the predicate surfaces a quality observation as governed data (structured stderr finding) rather than burying it in commit-message convention.
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — the predicate fires on the `git pre-commit` lifecycle trigger; no new lifecycle is invented.
- `.claude/rules/file-bridge-protocol.md` — bridge filing conventions followed verbatim.
- `.claude/rules/codex-review-gate.md` — counterpart review gate; awaits Codex GO before implementation begins.
- `.claude/rules/project-root-boundary.md` — all paths inside `E:\GT-KB`.

## Prior Deliberations

- DELIB-S344-SPEC-EXPRESSIONS-TRIANGULATION-001 — the concrete commit cycle whose `5611dc44` cross-scope bundle directly motivated work-item GTKB-COMMIT-SCOPE-BUNDLING-DETECTION-001. Empirical anchor for Slice 1.
- S333 audit FINDING-P0-001 captured in `bridge/gtkb-governance-hygiene-bundle-001.md` — sibling commit-discipline finding (commit `721f7c69` labeled `chore` despite ~13K LOC of net infrastructure). Establishes the family of commit-discipline gaps the predicate addresses.
- `bridge/gtkb-governance-hygiene-bundle-001.md` — established the Conventional Commits Type Discipline rule in `.claude/rules/file-bridge-protocol.md`. That rule is the human-discipline counterpart; this predicate is the mechanical counterpart.
- `bridge/gtkb-narrative-artifact-approval-extension-001-004.md` (Slice C universal floor) — established the per-path approval-packet evidence gate that this predicate complements. The current Slice 1 predicate reads the same packet directory but answers a different question (single-scope union vs. per-path coverage).
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE — repetitive plumbing for commit-scope coherence belongs in a deterministic service, not in author discipline. The predicate is that service.
- `bridge/gtkb-backlog-add-cli-slice-1-001.md` (sibling NEW, S350) — peer slice in the same batch authorization cycle; informs section conventions.

## Owner Decisions / Input

Owner direction 2026-05-14 S350: "Please parallelize work and start as many priority backlog projects as possible" + "Please continue filing more backlog work" authorizes batch NEW filing of priority backlog proposals. Per-proposal Codex GO required before implementation. Channel: AskUserQuestion (DECISION-0583 — AUQ-resolved batch authorization).

Underlying scope authority for GTKB-COMMIT-SCOPE-BUNDLING-DETECTION-001 itself: S344 owner directive "Both please" recorded in `source_owner_directive` on the work-item row (rowid 4473), authorizing strategic-self-improvement filing of two observations from the DELIB-S344 commit cycle.

No owner-AUQ-required decision is open inside this slice. Implementation stays within `scripts/` and a new test file; no protected narrative artifact is touched; no MemBase mutation; no formal-artifact insert. The Slice 1 WARN-only stance is itself the conservative choice that minimizes owner-decision surface area until empirical evidence justifies escalation to BLOCK in Slice 2.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal adds a single new predicate script and its test file. It is NOT a bulk operation under `GOV-STANDING-BACKLOG-001`'s bulk-ops clause:

- No bulk mutation of MemBase `work_items` rows (the predicate is read-only against MemBase via no path; it does not even open `groundtruth.db`).
- No bulk insertion of formal-artifact-approval packets (the predicate only READS the packet inventory at `.groundtruth/formal-artifact-approvals/`).
- No bulk edit of standing-backlog rows, deliberations, or specifications.
- No bulk modification of bridge files (the predicate does not touch `bridge/INDEX.md` or any `bridge/*.md`).

Evidence-pattern tokens: `inventory` of approval packets is read for scope-identity lookup; the predicate complements the existing `formal-artifact-approval` packet gate at `.groundtruth/formal-artifact-approvals/` without modifying it. The proposal touches exactly two files (one new script, one new test) and adds one non-blocking line to `.githooks/pre-commit` plumbing (deferred to a follow-on wiring slice to keep this scope minimal — Slice 1 lands the script + tests only).

## Requirement Sufficiency

Existing requirements sufficient. The governing specifications cited above (GOV-FILE-BRIDGE-AUTHORITY-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-STANDING-BACKLOG-001, GOV-ARTIFACT-APPROVAL-001, DCL-ARTIFACT-APPROVAL-HOOK-001, ADR-ISOLATION-APPLICATION-PLACEMENT-001, ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001) plus the cited rule files (`.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/project-root-boundary.md`) constrain the predicate's interface, packet-shape contract, evidence requirements, and scope. No new or revised requirement is required before Slice 1 implementation. Slice 2 (BLOCK escalation) will be a separate proposal and may motivate a new DCL at that time; that is deliberately deferred.

## Implementation Plan

Slice 1 implements only the read-only WARN-mode predicate and its test suite. No `.githooks/pre-commit` wiring; that is a single follow-on commit after Codex VERIFIED.

### A. Predicate script: `scripts/check_commit_scope_bundling.py`

Public CLI shape (matches `scripts/check_narrative_artifact_evidence.py` conventions):

```
python scripts/check_commit_scope_bundling.py --staged [--json] [--project-root PATH]
python scripts/check_commit_scope_bundling.py --paths PATH [PATH ...] [--json]
```

Module functions (pure, testable):

1. `_staged_paths(root: Path) -> list[str]` — invokes `git diff --cached --name-only --diff-filter=ACM`, normalizes backslashes to forward slashes, returns sorted list. Mirrors existing `check_narrative_artifact_evidence._staged_paths`.
2. `_load_packets(packets_dir: Path) -> list[dict]` — enumerates `*.json` under `.groundtruth/formal-artifact-approvals/`, parses each, returns only valid dicts. Deterministic glob-sorted order.
3. `_packet_scope_identity(packet: dict) -> tuple` — extracts `(source_ref, deliberation_id, spec_id, bridge_slug)`:
   - `source_ref`: packet's `source_ref` field (canonical scope label).
   - `deliberation_id`: parsed from `source_ref` or `change_reason` via `\bDELIB-[A-Z0-9_-]+\b` regex; `None` if absent.
   - `spec_id`: parsed via `\b(?:SPEC|GOV|ADR|DCL|PB|REQ)-[A-Z0-9][A-Z0-9_-]*\b`; `None` if absent.
   - `bridge_slug`: parsed via `\bgtkb-[a-z0-9-]+(?:-\d{3})?\b` (slug minus version suffix) when `source_ref` cites a bridge thread; `None` otherwise.
   - Two scope-identity tuples are EQUAL when all three resolvable components match (string equality, `None == None`). The frozen tuple is suitable as a dict key.
4. `_match_packets_to_path(rel_path: str, packets: list[dict]) -> list[dict]` — returns packets whose `target_path` equals `rel_path` (matching the existing `check_narrative_artifact_evidence` resolution).
5. `evaluate(root: Path, *, paths: list[str] | None = None) -> dict` — pure entry point returning `{"status": "pass"|"warn", "scopes": {scope_id: [paths]}, "unscoped_protected": [paths], "skipped_unprotected": [paths], "findings": [...]}`.
6. `_format_human(result: dict) -> str` — human-readable stderr message when WARN.
7. `main() -> int` — CLI; exits `0` always in Slice 1 (WARN exit reserved for Slice 2 BLOCK promotion). Emits `--json` when requested.

### B. Scope-coherence logic

For each staged path:
- If protected (per `config/governance/narrative-artifact-approval.toml`) AND has a matching packet → add to `scopes[scope_identity]`.
- If protected AND has no matching packet → add to `unscoped_protected`.
- If unprotected → add to `skipped_unprotected` (Slice 1 does not flag bulk source/test edits).

After classification:
- If `len(scopes) > 1` → emit finding `multi_scope_bundle` listing each scope_identity and its paths.
- If `unscoped_protected` is non-empty → emit finding `unscoped_protected_paths` (this overlaps with the existing universal-floor gate's hard-block; Slice 1's WARN is informational redundancy and a sanity check).
- Otherwise → status `pass`.

### C. Output format

WARN stderr (when `len(scopes) > 1`):

```
WARN commit-scope bundling detected
  Staged set spans 2 approval scopes:
    scope[1]: source_ref=<...>, deliberation=DELIB-..., spec=..., bridge_slug=...
      paths:
        - path/one.md
    scope[2]: source_ref=<...>, deliberation=DELIB-..., spec=..., bridge_slug=...
      paths:
        - path/two.md
  Slice 1 is WARN-only; commit proceeds. Slice 2 will promote to BLOCK after empirical tuning.
```

JSON output (when `--json`):

```json
{
  "status": "warn" | "pass",
  "scopes": {
    "<canonical-scope-key>": {"source_ref": "...", "deliberation_id": "...", "spec_id": "...", "bridge_slug": "...", "paths": ["..."]},
    "...": {"...": "..."}
  },
  "unscoped_protected": ["..."],
  "skipped_unprotected": ["..."],
  "findings": [
    {"kind": "multi_scope_bundle", "scope_count": 2, "scope_keys": ["..."]},
    {"kind": "unscoped_protected_paths", "paths": ["..."]}
  ]
}
```

### D. Exit code semantics (Slice 1)

- `0` — always (WARN-only mode); structured stderr or JSON conveys the diagnostic.
- `2` — configuration error (missing/unreadable `config/governance/narrative-artifact-approval.toml`) — mirrors the existing universal-floor gate.

Slice 2 will introduce exit `1` for BLOCK; that is explicitly out of scope here.

### E. Plumbing (deferred)

`.githooks/pre-commit` wiring is NOT part of Slice 1. After Codex VERIFIED, a one-line follow-on commit adds the predicate invocation between the existing `check_narrative_artifact_evidence.py` call and the PowerShell PS1 parse step, with `|| true` to honor the WARN-only stance. The follow-on commit is small enough to land under standard scoped-commit discipline without a new bridge thread; if Codex disagrees in review, that wiring can be folded into Slice 2 instead.

## Test Mapping

Test file: `platform_tests/scripts/test_check_commit_scope_bundling.py` (new).

| # | Test name | Spec coverage | Behavior verified |
|---|-----------|---------------|-------------------|
| 1 | `test_single_packet_single_scope_passes` | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001; GOV-ARTIFACT-APPROVAL-001 | Staged set of one packet-matched protected path returns `status=pass`, scope count 1. |
| 2 | `test_two_packets_same_scope_passes` | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | Two staged paths whose packets share identical `source_ref`/`deliberation_id`/`spec_id` collapse to a single scope; `status=pass`. |
| 3 | `test_two_packets_different_source_ref_warns` | GOV-FILE-BRIDGE-AUTHORITY-001; DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | Two packets with distinct `source_ref` produce `status=warn` and a `multi_scope_bundle` finding. Reproduces commit `5611dc44` empirically. |
| 4 | `test_two_packets_different_deliberation_id_warns` | GOV-ARTIFACT-ORIENTED-GOVERNANCE-001 | Same `source_ref` form but distinct DELIB ids in `change_reason` are flagged as distinct scopes. |
| 5 | `test_two_packets_different_bridge_slug_warns` | GOV-FILE-BRIDGE-AUTHORITY-001 | Two packets citing different bridge thread slugs are flagged as distinct scopes. |
| 6 | `test_protected_path_no_packet_warns_unscoped` | DCL-ARTIFACT-APPROVAL-HOOK-001 | A protected narrative path without a matching packet appears in `unscoped_protected` and surfaces an `unscoped_protected_paths` finding. |
| 7 | `test_unprotected_path_skipped_silently` | ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | A staged source/test/script path with no narrative-artifact protection is in `skipped_unprotected` and does not generate a finding in Slice 1. |
| 8 | `test_packet_enumeration_deterministic` | DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 | Two invocations against the same fixture return byte-identical JSON (glob-sorted iteration, no clock dependency). |
| 9 | `test_exit_code_zero_in_slice_1_warn_mode` | (Slice 1 boundary) | Even with `status=warn`, `main()` returns exit `0`. Slice 2 is the explicit place to change this. |
| 10 | `test_exit_code_two_on_missing_config` | (Operational safety) | When `config/governance/narrative-artifact-approval.toml` is missing, `main()` returns exit `2` and stderr mentions config path. |
| 11 | `test_staged_paths_plumbing_filters_diff_filter` | ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001 | Verifies the `git diff --cached --name-only --diff-filter=ACM` invocation skips deleted paths; uses a mocked subprocess. |
| 12 | `test_scope_identity_extraction_handles_none_components` | DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 | A packet with `source_ref` but no extractable DELIB/SPEC/bridge slug yields scope identity `(source_ref, None, None, None)` and groups correctly. |
| 13 | `test_paths_mode_bypasses_git` | ADR-ISOLATION-APPLICATION-PLACEMENT-001 | `--paths a b c` mode runs without git invocation; suitable for offline testing. |
| 14 | `test_json_output_shape_matches_contract` | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | JSON output contains the documented top-level keys (`status`, `scopes`, `unscoped_protected`, `skipped_unprotected`, `findings`). |
| 15 | `test_root_boundary_packet_dir_within_root` | ADR-ISOLATION-APPLICATION-PLACEMENT-001; `.claude/rules/project-root-boundary.md` | The predicate refuses to follow a `--project-root` outside `E:\GT-KB`; fails closed with a clear stderr. |

All tests use temporary directories and fixture packets; no live MemBase or live `.git` interaction.

## Risk and Rollback

**Risks:**

- *False positive on legitimate same-scope multi-packet edits.* Mitigation: Slice 1 WARN-only; false positives produce noise but never block. Slice 2 will use Slice 1 evidence to tighten the scope-identity tuple before promoting to BLOCK.
- *Scope-identity heuristic mis-extracts on novel packet shapes.* Mitigation: packet schema is stable (the `narrative_artifact_type` shape has not changed since the universal-floor landing). Test 12 exercises the `None`-component path explicitly.
- *Performance regression on the pre-commit path.* Mitigation: the predicate reads at most O(packets) JSON files (< 100 in the current inventory) and is bounded by the staged set size. Slice 1 also defers the `.githooks/pre-commit` wiring; performance impact only lands when Codex VERIFIES this slice plus the follow-on wiring.
- *Misleading WARN noise hides real findings.* Mitigation: structured stderr with explicit "Slice 1 is WARN-only" framing; `--json` mode keeps machine-readability for downstream tooling.

**Rollback:** the predicate is a standalone script with no MemBase or runtime dependency. Rollback is `git revert` of the implementation commit; no migration, no schema change, no state to clean up. The companion `.githooks/pre-commit` wiring (deferred) is similarly a one-line revert.

## Acceptance Criteria

1. `scripts/check_commit_scope_bundling.py` exists, is executable, and passes `python scripts/check_commit_scope_bundling.py --paths <fixture-path>` smoke-test.
2. All 15 tests in `platform_tests/scripts/test_check_commit_scope_bundling.py` pass under `python -m pytest platform_tests/scripts/test_check_commit_scope_bundling.py`.
3. The predicate returns exit `0` in WARN mode (Slice 1 boundary).
4. The predicate returns exit `2` when `config/governance/narrative-artifact-approval.toml` is missing.
5. JSON output schema matches the documented top-level keys.
6. The predicate produces deterministic output across two consecutive invocations against the same fixture.
7. No file outside `target_paths` is modified by the implementation.
8. The existing `check_narrative_artifact_evidence.py` predicate continues to pass for all staged paths under `.githooks/pre-commit` invocation (no regression of the universal-floor gate).
9. No MemBase mutations, no `bridge/INDEX.md` mutations, no formal-artifact-approval-packet writes.
10. Implementation report cites this proposal's Specification Links forward and adds a `## Recommended Commit Type` (`feat:`) line per the Conventional Commits Type Discipline rule.

## Verification Plan

1. Loyal Opposition runs `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-commit-scope-bundling-detection-slice-1` on the live INDEX entry and confirms `preflight_passed: true`.
2. Loyal Opposition runs `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-commit-scope-bundling-detection-slice-1` and confirms exit `0` with no blocking gaps.
3. Loyal Opposition runs the new test file: `python -m pytest platform_tests/scripts/test_check_commit_scope_bundling.py -v` and confirms 15 PASS, 0 FAIL.
4. Loyal Opposition smoke-tests the CLI: `python scripts/check_commit_scope_bundling.py --paths .claude/rules/file-bridge-protocol.md --json` and confirms a well-formed JSON envelope.
5. Loyal Opposition confirms `target_paths` boundary: `git status --porcelain` after implementation shows only `scripts/check_commit_scope_bundling.py` and `platform_tests/scripts/test_check_commit_scope_bundling.py` (plus the bridge proposal/report files themselves).
6. Loyal Opposition confirms exit-code parity by deliberately removing `config/governance/narrative-artifact-approval.toml` in a temp checkout (NOT in the live tree) and observing exit `2`.
7. Loyal Opposition records VERIFIED only when items 1–6 pass; otherwise NO-GO with the specific failing item enumerated.

## Applicability Preflight

The preflight will be run mechanically after this file is saved; the result is recorded here (filled in post-Write):

```
python scripts/bridge_applicability_preflight.py \
  --bridge-id gtkb-commit-scope-bundling-detection-slice-1 \
  --content-file E:\GT-KB\bridge\gtkb-commit-scope-bundling-detection-slice-1-001.md
```

Expected: `preflight_passed: true`, `missing_required_specs: []`. If the live INDEX entry does not yet exist, the `--content-file` mode evaluates the pending proposal text directly per the bridge-protocol catch-22 procedure.

End of proposal.
