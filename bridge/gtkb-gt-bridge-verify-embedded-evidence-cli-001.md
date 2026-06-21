NEW
author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: 96b4ab64-e440-47b7-8c81-cd55bc7a5c1e
author_model: claude-opus-4-8
author_model_version: 4.8
author_model_configuration: default

# Implementation Proposal - Deterministic-service CLI: gt bridge verify-embedded-evidence for inline-appendix byte-faithfulness + root-boundary regex checks

bridge_kind: prime_proposal
Document: gtkb-gt-bridge-verify-embedded-evidence-cli
Version: 001 (DRAFT; non-dispatchable)
Date: 2026-06-21 UTC

Project Authorization: PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21
Project: PROJECT-GTKB-RELIABILITY-FIXES
Work Item: WI-3415

target_paths: ["scripts/bridge_verify_embedded_evidence.py", "groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py", "platform_tests/scripts/test_bridge_verify_embedded_evidence.py"]

Implementation proposal for a bounded code or platform change.

## Claim

The verification labor for inline-embedded evidence in bridge implementation reports is repetitive, well-defined, and currently improvised per round as ad-hoc Python snippets — the exact "AI re-derives boilerplate procedure" anti-pattern that `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` declares a defect. The originating incident (`gtkb-git-repo-broken-blob-investigation` thread, NO-GO at `-008` and `-010`) required three rounds of hand-written hash/regex checks against the same report. This proposal converts that plumbing into a deterministic read-only service `scripts/bridge_verify_embedded_evidence.py`, exposed as `gt bridge verify-embedded-evidence --bridge-id <id>`, that (1) extracts each named appendix code-fenced block, (2) LF-normalizes it, (3) SHA256-compares it to the declared on-disk source path resolved from the proposal's `target_paths`, (4) scans the whole bridge file for the CLAUSE-IN-ROOT forbidden root-boundary patterns, and (5) emits JSON with per-appendix hash-match + per-pattern occurrence-count and a non-zero exit on any failure. Both Prime (pre-filing self-check) and Loyal Opposition (pre-verdict) run the single command instead of re-improvising the check.

## Requirement Sufficiency

Existing requirements sufficient. `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` already directs that repetitive, template-following AI plumbing be moved into deterministic services; this CLI is a direct first-class manifestation of that mandate (analogous to the existing `scripts/bridge_applicability_preflight.py` and `scripts/adr_dcl_clause_preflight.py` services). The forbidden-pattern set the service enforces is already specified in `config/governance/adr-dcl-clauses.toml` under `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` (`failure_pattern`). No new or revised requirement/specification is introduced; the service reads existing governance configuration and existing bridge-protocol structure rather than defining new policy.

## In-Root Placement Evidence

All target paths are inside `E:\GT-KB`: `scripts/bridge_verify_embedded_evidence.py`, `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`, `platform_tests/scripts/test_bridge_verify_embedded_evidence.py`. The service reads only in-root bridge files (`E:\GT-KB\bridge\`), in-root declared source paths under `target_paths`, and the in-root governance config `config/governance/adr-dcl-clauses.toml`. No out-of-root path is read, written, or required.

## Specification Links

- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` - governing directive: repetitive AI plumbing (the per-round inline-evidence hash/regex checks) is a defect and must be moved into a deterministic service; this CLI is that service.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - the service operates on bridge-protocol artifacts (versioned bridge files, `target_paths`, appendix evidence) and strengthens the GO/VERIFIED evidence discipline without weakening the bridge audit trail.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the CLI makes a recurring review formality artifact-backed and machine-checkable rather than conversation-mediated, consistent with artifact-oriented governance.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites every governing spec for the work (mandatory linkage).
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the verification plan below derives each test from a cited spec clause (mandatory spec-derived testing).
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the proposal carries Project Authorization / Project / Work Item linkage lines (mandatory project linkage).
- `SPEC-AUQ-POLICY-ENGINE-001` - no AUQ owner-decision surface is added or altered; the service is read-only and emits evidence, leaving owner-decision routing unchanged (cited to confirm non-impact on the AUQ policy surface).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the forbidden root-boundary patterns the service scans for are this ADR's `CLAUSE-IN-ROOT` `failure_pattern`; the service reuses that canonical pattern source rather than hard-coding a divergent copy, and the change is confined to the GT-KB platform (scripts + platform tests + the CLI module), crossing no application-placement boundary.
- `GOV-STANDING-BACKLOG-001` - WI-3415 is a standing-backlog work item under PROJECT-GTKB-RELIABILITY-FIXES.
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` - the service is a harness-neutral CLI runnable identically by Claude (Prime) and Codex (LO), preserving cross-harness parity for the pre-filing / pre-verdict check.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the evidence check becomes a durable, reusable artifact (a versioned script + test) rather than per-instance improvised snippets.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - adding this service is the lifecycle response (tooling creation) triggered by a repeated review-friction pattern surfaced across multiple bridge rounds.

## Prior Deliberations

- `DELIB-20264070` - Loyal Opposition Verification: Git Repo Broken-Blob Investigation REVISED-9 - the originating thread whose inline-evidence-embedding pattern (appendix code fences SHA256-compared to source) this service automates; the Opportunity Radar note proposing this CLI lives in that thread's `-010` file.
- `DELIB-20261600` - Loyal Opposition Review - gt generate-approval-packet CLI - precedent for converting repetitive Prime/LO plumbing into a deterministic `gt`-surfaced CLI; informs the same shape (read-only, JSON output, non-zero exit on failure).
- `DELIB-2407` - Loyal Opposition Review - gt generate-approval-packet CLI - earlier review of the same deterministic-service CLI pattern; reinforces the design conventions reused here.
- `DELIB-2488` - Loyal Opposition Verification - LO File-Safety PreToolUse Enforcement Slice 1 - precedent that root-boundary / path-safety checks belong in mechanical tooling, not agent self-discipline.
- `DELIB-20263281` - Loyal Opposition NO-GO Verdict: WI-4464 Commit Pathspec-Safety Detector - sibling deterministic safety-detector design (read-only scanner with structured findings + fail-fast exit) whose conventions this service mirrors.

## Owner Decisions / Input

- `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-NONFASTLANE-BATCH-2026-06-21` - active project authorization covering the PROJECT-GTKB-RELIABILITY-FIXES non-fast-lane batch; WI-3415 is in scope through active project membership, authorizing this bounded implementation (new script + thin CLI wiring + test) under the bridge protocol.
- `DELIB-20265457` - owner AUQ (2026-06-21) authorizing authoring of NEW proposals for the open PROJECT-GTKB-RELIABILITY-FIXES work-item batch; WI-3415 (P3, origin=new) is an item in that authorized batch.

## Proposed Scope

1. Add `scripts/bridge_verify_embedded_evidence.py`, a read-only deterministic service modeled on `scripts/bridge_applicability_preflight.py` (same argparse / resolver / JSON-output conventions). It:
   - Accepts `--bridge-id <id>` (resolved to the operative versioned file via `parse_versioned_files_for_document`, reused from the applicability-preflight resolver) OR `--content-file <path>` for pre-filing self-check of a draft, plus `--bridge-dir` (default `bridge/`) and `--json`.
   - **Appendix extraction:** parses appendix blocks by the header pattern `Appendix A<n> - <filename>` (case-insensitive, tolerant of `—`/`-` dashes) followed by the adjacent fenced code block (``` ... ```), capturing `<filename>` and the fenced body.
   - **Source resolution:** resolves each captured `<filename>` against the proposal's declared `target_paths` (reusing `extract_target_paths` from `bridge_applicability_preflight`) by basename match; an appendix whose filename matches no declared in-root source path is reported as `unresolved` (failure).
   - **Byte-faithfulness:** LF-normalizes the fenced body (strip trailing CR, normalize CRLF->LF, ensure single trailing newline policy matching on-disk read) and SHA256-compares to the resolved on-disk source file; emits per-appendix `{appendix, filename, source_path, embedded_sha256, source_sha256, match: bool}`.
   - **Root-boundary scan:** loads the `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` `failure_pattern` from `config/governance/adr-dcl-clauses.toml` (honoring `failure_pattern_disclosure_exempt` HTML-comment spans the same way the clause preflight does) and counts occurrences across the whole bridge file, reporting `{pattern, occurrences, lines: [..]}` with file-and-line precision.
   - **Result + exit:** emits a JSON object `{bridge_id, operative_path, appendices: [...], root_boundary: {...}, summary: {appendix_failures, root_boundary_failures}, passed: bool}` and exits `0` on full pass, non-zero on any hash mismatch, unresolved appendix, or root-boundary occurrence.
2. Wire a thin `@bridge_group.command("verify-embedded-evidence")` Click command in `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py` (where `bridge_group` is defined and which `cli.py` imports) that forwards `--bridge-id` / `--content-file` / `--json` to the script's public entry function and propagates its exit code, mirroring how the existing `bridge_group` subcommands delegate.
3. Add regression tests in `platform_tests/scripts/test_bridge_verify_embedded_evidence.py` (see verification plan) using the `importlib.util.spec_from_file_location` load pattern of `test_bridge_applicability_preflight.py`, with `tmp_path` fixtures that synthesize a bridge file + matching/mismatching source files.

Out of scope: changing the appendix-embedding format itself, any MemBase write, any change to bridge dispatch/routing, and any new owner-decision/AUQ surface. The service is purely read-only and additive.

## Specification-Derived Verification Plan

| Spec clause | Derived test | Assertion |
|---|---|---|
| `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` (plumbing becomes a deterministic service) | `test_pass_when_appendix_matches_source` | A bridge file whose appendix block byte-matches its declared on-disk source and contains no forbidden patterns yields `passed: true` and exit code 0. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` (hash mismatch must be caught) | `test_fail_on_appendix_hash_mismatch` | When the appendix body differs from the resolved source file, the result reports `match: false` for that appendix and exit code is non-zero. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (appendix must resolve to a declared target_path) | `test_fail_on_unresolved_appendix_filename` | An appendix whose filename matches no `target_paths` source is reported `unresolved` and exit code is non-zero. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (CLAUSE-IN-ROOT forbidden patterns) | `test_fail_on_root_boundary_pattern` | A bridge file containing a non-exempt out-of-root path literal <!-- in-root-disclosure -->(the canonical `CLAUSE-IN-ROOT` `failure_pattern` triad: `C:\Users\`, `/tmp/`, `C:\temp\`)<!-- /in-root-disclosure --> reports `root_boundary_failures > 0` with the offending line number and exit code is non-zero. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` (`failure_pattern_disclosure_exempt`) | `test_disclosure_exempt_span_not_flagged` | A forbidden pattern inside a paired `<!-- in-root-disclosure -->`/`<!-- /in-root-disclosure -->` span is NOT counted, matching clause-preflight semantics. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` (LF normalization) | `test_crlf_embedded_body_normalized_before_hash` | An appendix body with CRLF line endings that LF-normalizes to the LF source file still reports `match: true` (normalization is applied before hashing). |
| `ADR-CODEX-HOOK-PARITY-FALLBACK-001` (`--content-file` parity path) | `test_content_file_mode_resolves_without_bridge_dir` | Passing `--content-file <draft>` (no live bridge thread) performs the same extraction/scan against the draft content, enabling identical Prime/LO pre-filing use. |

Execution commands:
- `python -m pytest platform_tests/scripts/test_bridge_verify_embedded_evidence.py -q --tb=short`
- `python -m ruff check scripts/bridge_verify_embedded_evidence.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py platform_tests/scripts/test_bridge_verify_embedded_evidence.py`
- `python -m ruff format --check scripts/bridge_verify_embedded_evidence.py groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py platform_tests/scripts/test_bridge_verify_embedded_evidence.py`

## Acceptance Criteria

1. `gt bridge verify-embedded-evidence --bridge-id <id>` (and `--content-file <draft>`) extracts `Appendix A<n> - <filename>` fenced blocks, resolves each filename against the proposal's `target_paths`, LF-normalizes, and SHA256-compares to the on-disk source, emitting per-appendix match results.
2. The command scans the whole bridge file for the canonical `CLAUSE-IN-ROOT` `failure_pattern` (loaded from `config/governance/adr-dcl-clauses.toml`, honoring disclosure-exempt spans) and reports per-pattern occurrence counts with line numbers.
3. The command emits structured JSON and exits non-zero on any hash mismatch, unresolved appendix, or root-boundary occurrence; exits 0 when all checks pass.
4. The seven derived tests pass; `ruff check` and `ruff format --check` are clean on all three changed files.

## Risks / Rollback

- Risk: appendix-header parsing is too strict and misses real appendices (false pass). Mitigation: header regex tolerates `-`/`—` dash variants and is case-insensitive; `test_fail_on_unresolved_appendix_filename` and the match tests pin the recognized shape; an unrecognized appendix surfaces as `unresolved` rather than silently passing.
- Risk: LF-normalization diverges from how the on-disk file is read, causing spurious mismatches. Mitigation: both the embedded body and the source file are read and normalized through the same helper; `test_crlf_embedded_body_normalized_before_hash` pins the contract.
- Risk: drift between the service's forbidden-pattern set and the canonical clause config. Mitigation: the service loads `failure_pattern` from `config/governance/adr-dcl-clauses.toml` at runtime rather than hard-coding it, so it tracks the canonical source.
- Rollback: delete `scripts/bridge_verify_embedded_evidence.py` and its test, and remove the thin `@bridge_group.command("verify-embedded-evidence")` registration in `cli_bridge_propose.py`. The change is purely additive (a new read-only script + one CLI command + tests) with no migration, no MemBase mutation, and no change to existing behavior; fully reversible.

## Files Expected To Change

- `scripts/bridge_verify_embedded_evidence.py`
- `groundtruth-kb/src/groundtruth_kb/cli_bridge_propose.py`
- `platform_tests/scripts/test_bridge_verify_embedded_evidence.py`

## Recommended Commit Type

`feat`
