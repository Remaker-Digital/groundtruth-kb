REVISED

---
Status: REVISED
Author: prime-builder (claude harness B)
Date: 2026-05-15
Session: S354
Source: GTKB-COMMIT-SCOPE-BUNDLING-DETECTION-001 (Pre-commit predicate to detect cross-scope bundling via mismatched approval-packet manifest)
Recommended commit type: feat
bridge_kind: implementation_proposal
target_paths: ["scripts/check_commit_scope_bundling.py", "platform_tests/scripts/test_check_commit_scope_bundling.py"]
Project Authorization: PAUTH-PROJECT-COMMIT-SCOPE-BUNDLING-DETECTION-COMMIT-SCOPE-BUNDLING-DETECTION-SLICE-1
Project: PROJECT-COMMIT-SCOPE-BUNDLING-DETECTION
Work Item: GTKB-COMMIT-SCOPE-BUNDLING-DETECTION-001
---

Document: gtkb-commit-scope-bundling-detection-slice-1

## Summary

Add a deterministic, read-only pre-commit predicate `scripts/check_commit_scope_bundling.py` that inspects the staged-file set, looks up matching formal-artifact-approval packets under `.groundtruth/formal-artifact-approvals/`, computes the per-file scope-identity union, and emits a structured diagnostic when the staged set spans more than one approval scope OR contains protected staged paths with no covering approval scope. Slice 1 is **WARN-only**: the predicate prints a finding to stderr and exits `0` so commits are not blocked. Block-mode escalation is deferred to Slice 2 (a separate bridge thread) after Slice 1 produces real-world false-positive/false-negative evidence.

Scope-identity per packet is the deterministic tuple `(deliberation_id?, spec_id?, bridge_thread_slug?, source_ref)` derived from the packet's `source_ref`, `change_reason`, and `artifact_id` fields. Two staged files share a scope when their matched packets yield equal scope-identity tuples; they bundle different scopes when the tuples differ. Files with no matching packet are counted in a separate `unscoped_paths` bucket and are only flagged when they intersect the protected-narrative-artifact pattern set (per `config/governance/narrative-artifact-approval.toml`) — bulk source/test/script edits without a narrative-artifact packet are out of scope for Slice 1.

The predicate has NO write side effects, makes NO MemBase mutations, and depends only on `git diff --cached --name-only` plus filesystem reads under `.groundtruth/formal-artifact-approvals/` and `config/governance/`.

**Scope boundary (REVISED — addresses F1):** Slice 1 lands exactly two files — the new predicate script and its new test file, as declared in `target_paths`. Slice 1 does NOT touch `.githooks/pre-commit` or any other hook/configuration surface. Wiring the predicate into `.githooks/pre-commit` is explicitly OUT of this slice's scope and is NOT authorized by this proposal. That wiring is a hook/configuration mutation under `.claude/rules/codex-review-gate.md` §"What Counts as Implementation" and requires its own separate NEW bridge proposal — filed, reviewed, and GO'd — with `.githooks/pre-commit` listed in that proposal's `target_paths`. This proposal makes no claim that the wiring is "small enough" to skip bridge review; it is not.

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
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001 — the predicate is designed to be invoked on the `git pre-commit` lifecycle trigger by a future wiring slice; no new lifecycle is invented.
- GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001 — work item GTKB-COMMIT-SCOPE-BUNDLING-DETECTION-001 is homed in PROJECT-COMMIT-SCOPE-BUNDLING-DETECTION and covered by the active project-scoped authorization cited in this proposal's metadata.
- `.claude/rules/file-bridge-protocol.md` — bridge filing conventions followed verbatim.
- `.claude/rules/codex-review-gate.md` — counterpart review gate; awaits Codex GO before implementation begins.
- `.claude/rules/project-root-boundary.md` — all paths inside `E:\GT-KB`.

## Prior Deliberations

- DELIB-0835 — owner formal-artifact approval-and-audit principle; the predicate complements (does not replace) the formal-artifact-approval discipline whose packet inventory it reads.
- DELIB-COMMIT-SCOPE-BUNDLING-DETECTION-001-PROJECT-HOMING — owner AskUserQuestion decision (S354) homing GTKB-COMMIT-SCOPE-BUNDLING-DETECTION-001 in the new dedicated project PROJECT-COMMIT-SCOPE-BUNDLING-DETECTION and authorizing the project-scoped implementation authorization that this proposal cites.
- DELIB-S344-SPEC-EXPRESSIONS-TRIANGULATION-001 — the concrete commit cycle whose `5611dc44` cross-scope bundle directly motivated work-item GTKB-COMMIT-SCOPE-BUNDLING-DETECTION-001. Empirical anchor for Slice 1.
- S333 audit FINDING-P0-001 captured in `bridge/gtkb-governance-hygiene-bundle-001.md` — sibling commit-discipline finding (commit `721f7c69` labeled `chore` despite ~13K LOC of net infrastructure). Establishes the family of commit-discipline gaps the predicate addresses.
- `bridge/gtkb-governance-hygiene-bundle-001.md` — established the Conventional Commits Type Discipline rule in `.claude/rules/file-bridge-protocol.md`. That rule is the human-discipline counterpart; this predicate is the mechanical counterpart.
- `bridge/gtkb-narrative-artifact-approval-extension-001-004.md` (Slice C universal floor) — established the per-path approval-packet evidence gate that this predicate complements. The current Slice 1 predicate reads the same packet directory but answers a different question (single-scope union vs. per-path coverage).
- DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE — repetitive plumbing for commit-scope coherence belongs in a deterministic service, not in author discipline. The predicate is that service.
- `bridge/gtkb-backlog-add-cli-slice-1-001.md` (sibling NEW, S350) — peer slice in the same batch authorization cycle; informs section conventions.

## Owner Decisions / Input

Project-homing decision: the owner decided, via AskUserQuestion (recorded as `DELIB-COMMIT-SCOPE-BUNDLING-DETECTION-001-PROJECT-HOMING`, `source_type=owner_conversation`, `outcome=owner_decision`, session S354), to home work item GTKB-COMMIT-SCOPE-BUNDLING-DETECTION-001 under a NEW dedicated project `PROJECT-COMMIT-SCOPE-BUNDLING-DETECTION` (1:1 with the work item) and to create the project-scoped implementation authorization `PAUTH-PROJECT-COMMIT-SCOPE-BUNDLING-DETECTION-COMMIT-SCOPE-BUNDLING-DETECTION-SLICE-1`. The owner was presented three options — (A) a new dedicated project, (B) home under existing PROJECT-GTKB-COMMIT-TRIAGE-001, (C) home under existing PROJECT-GTKB-SECRETS-PURGE-AND-COMMIT-ENFORCEMENT — and chose (A). This proposal's three project-linkage metadata lines (`Project Authorization:`, `Project:`, `Work Item:`) reflect that decision.

Underlying scope authority for GTKB-COMMIT-SCOPE-BUNDLING-DETECTION-001 itself: S344 owner directive "Both please" recorded in `source_owner_directive` on the work-item row (rowid 4473), authorizing strategic-self-improvement filing of two observations from the DELIB-S344 commit cycle.

No owner-AUQ-required decision is open inside this slice's implementation. Implementation stays within `scripts/` and a new test file; no protected narrative artifact is touched; no MemBase mutation; no formal-artifact insert; no hook/configuration mutation. The Slice 1 WARN-only stance is itself the conservative choice that minimizes owner-decision surface area until empirical evidence justifies escalation to BLOCK in Slice 2.

## Revision Notes

This `-003` REVISED proposal addresses both findings in the `-002` Codex NO-GO.

- **F1 (P1) — Follow-on pre-commit wiring proposed outside bridge-reviewed target scope.** Addressed by choosing the pure-Slice-1 option (Codex's revision option 1). All wording stating that `.githooks/pre-commit` wiring would happen "without a new bridge thread" is removed. The `-001` § E ("Plumbing (deferred)"), the § Summary closing sentence, the § Clause Scope Clarification plumbing line, and the § Implementation Plan preamble are all rewritten to state explicitly that `.githooks/pre-commit` wiring is OUT of this slice's scope, is NOT authorized by this proposal, and requires a separate NEW bridge proposal with `.githooks/pre-commit` in that proposal's `target_paths`. `target_paths` is unchanged — exactly `["scripts/check_commit_scope_bundling.py", "platform_tests/scripts/test_check_commit_scope_bundling.py"]`.
- **F2 (P3) — Fixture strategy vs. absolute project-root refusal contract.** Addressed by stating the intended contract precisely. The live default entry point `main()` refuses a `--project-root` outside the repository root (fails closed with a clear stderr message and a non-`0` config-error exit). The pure entry point `evaluate(root, *, paths=None)` accepts ANY explicit root, including a unit-test temporary directory, and never reads or writes live GT-KB artifacts. Unit tests exercise `evaluate()` directly with temporary fixture roots; the root-boundary refusal is tested against `main()` (the CLI surface), not `evaluate()`. See § B (root-boundary contract), § Test Mapping rows 13 and 15, and § Verification Plan item 6.

## Clause Scope Clarification (Not a Bulk Operation)

This proposal adds a single new predicate script and its test file. It is NOT a bulk operation under `GOV-STANDING-BACKLOG-001`'s bulk-ops clause:

- No bulk mutation of MemBase `work_items` rows (the predicate is read-only against MemBase via no path; it does not even open `groundtruth.db`).
- No bulk insertion of formal-artifact-approval packets (the predicate only READS the packet inventory at `.groundtruth/formal-artifact-approvals/`).
- No bulk edit of standing-backlog rows, deliberations, or specifications.
- No bulk modification of bridge files (the predicate does not touch `bridge/INDEX.md` or any `bridge/*.md`).

Evidence-pattern tokens: `inventory` of approval packets is read for scope-identity lookup; the predicate complements the existing `formal-artifact-approval` packet gate at `.groundtruth/formal-artifact-approvals/` without modifying it. The proposal touches exactly two files (one new script, one new test) — it adds NO line to `.githooks/pre-commit` or any other hook/configuration file. Hook wiring is deferred to a separate NEW bridge proposal (see § Revision Notes F1 and § E).

## Requirement Sufficiency

Existing requirements sufficient. The governing specifications cited above (GOV-FILE-BRIDGE-AUTHORITY-001, DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-STANDING-BACKLOG-001, GOV-ARTIFACT-APPROVAL-001, DCL-ARTIFACT-APPROVAL-HOOK-001, ADR-ISOLATION-APPLICATION-PLACEMENT-001, ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001, GOV-ARTIFACT-ORIENTED-GOVERNANCE-001, DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001, GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001) plus the cited rule files (`.claude/rules/file-bridge-protocol.md`, `.claude/rules/codex-review-gate.md`, `.claude/rules/project-root-boundary.md`) constrain the predicate's interface, packet-shape contract, evidence requirements, and scope. No new or revised requirement is required before Slice 1 implementation. Slice 2 (BLOCK escalation) will be a separate proposal and may motivate a new DCL at that time; that is deliberately deferred. The `.githooks/pre-commit` wiring slice is likewise a separate future proposal; it is not implied or authorized here.

## Implementation Plan

Slice 1 implements only the read-only WARN-mode predicate and its test suite — exactly the two files in `target_paths`. There is NO `.githooks/pre-commit` wiring in this slice. The wiring is a separate hook/configuration mutation that requires its own NEW bridge proposal (see § E and § Revision Notes F1).

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
5. `evaluate(root: Path, *, paths: list[str] | None = None) -> dict` — pure entry point returning `{"status": "pass"|"warn", "scopes": {scope_id: [paths]}, "unscoped_protected": [paths], "skipped_unprotected": [paths], "findings": [...]}`. `evaluate()` accepts ANY explicit `root` (including a unit-test temporary directory) and reads only the packet/config directories beneath that `root`; it performs no repository-root boundary check and never touches live GT-KB artifacts when called with a temporary root.
6. `_format_human(result: dict) -> str` — human-readable stderr message when WARN.
7. `main() -> int` — CLI; resolves the effective project root, enforces the root-boundary contract (see § B), then delegates to `evaluate()`. Exits `0` always in Slice 1 WARN/pass mode (WARN exit reserved for Slice 2 BLOCK promotion); exits `2` on configuration error including a root-boundary violation. Emits `--json` when requested.

### B. Scope-coherence logic and root-boundary contract

**Root-boundary contract (REVISED — addresses F2):**

- `main()` (the live default entry point): resolves the effective project root from `--project-root` (default: the current repository root, discovered as the directory containing `.git`). If the resolved root is OUTSIDE the repository root, `main()` refuses: it prints a clear stderr message naming the offending path and the expected repository root, and returns exit `2` (configuration error). This is the live, fail-closed default.
- `evaluate(root, *, paths=None)` (the pure entry point): accepts ANY explicit `root`, including a unit-test temporary directory. `evaluate()` performs NO root-boundary check; it only reads the packet directory and `config/governance/` beneath the supplied `root`. Unit tests call `evaluate()` directly with temporary fixture roots and therefore never touch live GT-KB artifacts and never trip the `main()` refusal.

This split means the public CLI is fail-closed against accidental out-of-root execution, while the pure function remains fully unit-testable with temporary directories — resolving the `-002` F2 ambiguity.

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

- `0` — always for `pass` and `warn` results (WARN-only mode); structured stderr or JSON conveys the diagnostic.
- `2` — configuration error: missing/unreadable `config/governance/narrative-artifact-approval.toml`, OR a `--project-root` resolved outside the repository root (the root-boundary refusal). Mirrors the existing universal-floor gate's config-error code.

Slice 2 will introduce exit `1` for BLOCK; that is explicitly out of scope here.

### E. Pre-commit wiring is OUT of scope (separate future proposal)

`.githooks/pre-commit` wiring is NOT part of Slice 1 and is NOT authorized by this proposal. The predicate ships in Slice 1 as a standalone, independently-runnable script (`python scripts/check_commit_scope_bundling.py ...`) and its test suite. Wiring it into `.githooks/pre-commit` — adding an invocation line to that hook file — is a hook/configuration mutation per `.claude/rules/codex-review-gate.md` §"What Counts as Implementation" item 4 and §"Mechanical Implementation-Start Gate". It therefore requires its OWN separate NEW bridge proposal: a distinct bridge thread whose `target_paths` lists `.githooks/pre-commit`, whose implementation plan states the exact hook-line change, and whose verification plan proves the WARN-only behavior in the hook path. This proposal makes no claim that the wiring is "too small to review" — it explicitly does not. The wiring proposal will be filed after this slice reaches VERIFIED (or, at the owner's/Codex's discretion, folded into the Slice 2 BLOCK-escalation thread).

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
| 13 | `test_evaluate_accepts_temporary_root` | ADR-ISOLATION-APPLICATION-PLACEMENT-001 | `evaluate(tmp_root, paths=[...])` runs against a temporary fixture root with no git invocation and no live GT-KB artifact access; suitable for offline unit testing. |
| 14 | `test_json_output_shape_matches_contract` | DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001 | JSON output contains the documented top-level keys (`status`, `scopes`, `unscoped_protected`, `skipped_unprotected`, `findings`). |
| 15 | `test_main_refuses_project_root_outside_repo` | ADR-ISOLATION-APPLICATION-PLACEMENT-001; `.claude/rules/project-root-boundary.md` | `main()` invoked with a `--project-root` outside the repository root refuses: returns exit `2` and prints a stderr message naming the offending path. The pure `evaluate()` entry point is NOT subject to this refusal (verified by row 13). |

All tests use temporary directories and fixture packets and exercise the pure `evaluate()` entry point; the single root-boundary refusal test (row 15) exercises `main()` (the CLI). No test performs live MemBase or live `.git` interaction.

## Risk and Rollback

**Risks:**

- *False positive on legitimate same-scope multi-packet edits.* Mitigation: Slice 1 WARN-only; false positives produce noise but never block. Slice 2 will use Slice 1 evidence to tighten the scope-identity tuple before promoting to BLOCK.
- *Scope-identity heuristic mis-extracts on novel packet shapes.* Mitigation: packet schema is stable (the `narrative_artifact_type` shape has not changed since the universal-floor landing). Test 12 exercises the `None`-component path explicitly.
- *Performance regression on the pre-commit path.* Mitigation: the predicate reads at most O(packets) JSON files (< 100 in the current inventory) and is bounded by the staged set size. Slice 1 also does NOT wire the predicate into `.githooks/pre-commit`; no pre-commit-path performance impact lands until a separate wiring proposal is reviewed and GO'd.
- *Misleading WARN noise hides real findings.* Mitigation: structured stderr with explicit "Slice 1 is WARN-only" framing; `--json` mode keeps machine-readability for downstream tooling.

**Rollback:** the predicate is a standalone script with no MemBase or runtime dependency. Rollback is `git revert` of the implementation commit; no migration, no schema change, no state to clean up. Since this slice does not touch `.githooks/pre-commit`, no hook-wiring rollback is in scope.

## Acceptance Criteria

1. `scripts/check_commit_scope_bundling.py` exists, is executable, and passes `python scripts/check_commit_scope_bundling.py --paths <fixture-path>` smoke-test.
2. All 15 tests in `platform_tests/scripts/test_check_commit_scope_bundling.py` pass under `python -m pytest platform_tests/scripts/test_check_commit_scope_bundling.py`.
3. The predicate returns exit `0` in WARN mode (Slice 1 boundary).
4. The predicate returns exit `2` when `config/governance/narrative-artifact-approval.toml` is missing.
5. `main()` returns exit `2` and a clear stderr message when invoked with a `--project-root` outside the repository root; `evaluate()` accepts a temporary root without refusal.
6. JSON output schema matches the documented top-level keys.
7. The predicate produces deterministic output across two consecutive invocations against the same fixture.
8. No file outside `target_paths` is modified by the implementation — in particular, `.githooks/pre-commit` is NOT modified by this slice.
9. The existing `check_narrative_artifact_evidence.py` predicate continues to pass for all staged paths under `.githooks/pre-commit` invocation (no regression of the universal-floor gate).
10. No MemBase mutations, no `bridge/INDEX.md` mutations, no formal-artifact-approval-packet writes, no hook/configuration-file writes.
11. Implementation report cites this proposal's Specification Links forward and adds a `## Recommended Commit Type` (`feat:`) line per the Conventional Commits Type Discipline rule.

## Verification Plan

1. Loyal Opposition runs `python scripts/bridge_applicability_preflight.py --bridge-id gtkb-commit-scope-bundling-detection-slice-1` on the live INDEX entry and confirms `preflight_passed: true`.
2. Loyal Opposition runs `python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-commit-scope-bundling-detection-slice-1` and confirms exit `0` with no blocking gaps.
3. Loyal Opposition runs the new test file: `python -m pytest platform_tests/scripts/test_check_commit_scope_bundling.py -v` and confirms 15 PASS, 0 FAIL.
4. Loyal Opposition smoke-tests the CLI: `python scripts/check_commit_scope_bundling.py --paths .claude/rules/file-bridge-protocol.md --json` and confirms a well-formed JSON envelope.
5. Loyal Opposition confirms `target_paths` boundary: `git status --porcelain` after implementation shows only `scripts/check_commit_scope_bundling.py` and `platform_tests/scripts/test_check_commit_scope_bundling.py` (plus the bridge proposal/report files themselves); `.githooks/pre-commit` is unchanged.
6. Loyal Opposition confirms the root-boundary contract: `main()` invoked with `--project-root` set to a path outside the repository root (e.g., a temp directory) exits `2` with a clear stderr message; a unit test calling `evaluate()` with a temporary fixture root succeeds. The `evaluate()` temporary-root path is also exercised by test row 13, and the `main()` refusal by test row 15 — both run in the same temp checkout, never against the live tree.
7. Loyal Opposition records VERIFIED only when items 1–6 pass; otherwise NO-GO with the specific failing item enumerated.

## Applicability Preflight

Command:

```
python scripts/bridge_applicability_preflight.py --bridge-id gtkb-commit-scope-bundling-detection-slice-1
```

Observed (run against the live INDEX `-003` operative file after this file was saved and the INDEX `REVISED` entry added):

```
- packet_hash: sha256:c5763adc872f4e404e3371854426335605d04d96e4360f7f5a14fa6182bfafa7
- bridge_document_name: gtkb-commit-scope-bundling-detection-slice-1
- content_source: indexed_operative
- content_file: bridge/gtkb-commit-scope-bundling-detection-slice-1-003.md
- operative_file: bridge/gtkb-commit-scope-bundling-detection-slice-1-003.md
- preflight_passed: true
- missing_required_specs: []
- missing_advisory_specs: []
```

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `yes` | content:artifact, content:traceability, content:deliberation, content:MemBase |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | `blocking` | `yes` | path:.claude/rules/project-root-boundary.md, path:.claude/rules/file-bridge-protocol.md |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `yes` | content:deferred, content:blocked, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links, content:bridge proposal |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `yes` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/**, path:.claude/rules/file-bridge-protocol.md, path:.claude/rules/codex-review-gate.md |

Exit code: `0`. All required cross-cutting specs are cited; `missing_required_specs` is empty.

## Clause Applicability

Command:

```
python scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-commit-scope-bundling-detection-slice-1
```

Observed (run against the live INDEX `-003` operative file after this file was saved and the INDEX `REVISED` entry added):

```
- Bridge id: gtkb-commit-scope-bundling-detection-slice-1
- Operative file: bridge\gtkb-commit-scope-bundling-detection-slice-1-003.md
- Clauses evaluated: 5
- must_apply: 5, may_apply: 0, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: mandatory (default invocation). Exit 5 = blocking gap; exit 0 = pass.
```

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | must_apply | yes | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-INDEX-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | must_apply | yes | blocking | blocking |

Exit code: `0`. All 5 `must_apply` clauses have satisfying evidence; 0 blocking gaps; no owner waiver required.

End of proposal.
