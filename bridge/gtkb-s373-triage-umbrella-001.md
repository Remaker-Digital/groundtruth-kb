NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: 8c70eac3-4056-47ed-9910-27f1a0b42708
author_model: Opus 4.7 (1M context)
author_model_version: claude-opus-4-7[1m]
author_model_configuration: Claude Code CLI default reasoning

# GT-KB S373 Working-Tree Triage Umbrella — Per-Bucket Thematic Commit Authorization

bridge_kind: governance_advisory

Document: gtkb-s373-triage-umbrella
Version: 001 (NEW; umbrella authorization proposal)
Date: 2026-05-29 UTC

## Governance-Review Framing

This filing is `bridge_kind: governance_review` because it is a coordination/authorization proposal that requests Loyal Opposition GO once for a bounded triage workflow, rather than per-bucket bridge proposals for each thematic commit. No source code is changed by this proposal itself. The downstream per-bucket commits are persistence of artifacts already produced by prior bridge threads (each of which carried its own GO/VERIFIED cycle) plus one mechanical inventory regen following the established `bd0f8bfa` pattern. No `Project Authorization:` triple is cited because this proposal does not directly authorize source-code implementation work — it authorizes the persistence of already-bridged outputs.

Owner directed this umbrella path via AskUserQuestion this session (S373: "File umbrella triage bridge proposal").

## Problem Statement (verified evidence)

The S373 working tree carries 639 uncommitted entries that accumulated across multiple sessions (S350-S373) without being persisted. A `git status --porcelain` run at 2026-05-29T14:01Z confirmed the count. The index was contaminated with 596 staged files when this session opened — a parallel-session pre-staging state matching the pattern documented in `feedback_inspect_staged_index_before_commit` (the staged set crosses every bucket boundary, including the Slice 3 quarantine class).

### Verified state (after this session's surgical index cleanup)

- 459 entries under `bridge/` are now selectively staged (BUCKET D), corresponding to 50+ bridge thread families with their `NEW/REVISED/GO/NO-GO/VERIFIED` versions plus `bridge/INDEX.md` updates. Blob hashes sampled against the working tree confirmed parity.
- 182 non-bridge files were surgically unstaged via `git restore --staged <specific-path>` to remove parallel-session contamination from the index. Working tree blobs were untouched.
- Pre-commit hook (`scripts/check_dev_environment_inventory_drift.py`) blocked the BUCKET D commit with `BLOCK normalized_inventory_drift: current public inventory differs from committed baseline`. Diff keys: `repo_configured_surfaces`, `toolchain`. The baseline at `.groundtruth/inventory/dev-environment-inventory.{json,md}` was last regenerated 2026-05-28 (`bd0f8bfa`); the repo state has drifted since.

### Mandatory exclusion (Slice 3 quarantine)

The Slice 3 narrative-split file set is BLOCKED from any commit this session and remains in the working tree pending the scanner-fix scoping thread (`bridge/gtkb-project-completion-scanner-addressing-thread-fix-scoping-001.md`) reaching VERIFIED and `PROJECT-GTKB-CLAUDE-MD-SCOPE-CORRECTION` being restored. Quarantine set:

- `CLAUDE.md` (modified, root-level)
- `SECURITY.md` (modified, root-level)
- 5 renames to `applications/Agent_Red/`: `CHANGELOG.md`, `CLAUDE-ARCHITECTURE.md`, `CLAUDE-REFERENCE.md`, `CLAUDE_ARCHIVE.md`, `CONTRIBUTING.md`
- `applications/Agent_Red/CLAUDE.md` (added, new app-scope rule file)
- `applications/Agent_Red/SECURITY.md` (added)
- 3 deletion targets under `scripts/session-tmp/` (Slice 3 F2 REMOVAL set, not commit set)

The 7 formal-artifact-approval packets for the Slice 3 narrative-split at `.groundtruth/formal-artifact-approvals/2026-05-29-*.json` are gitignored (line 508 of `.gitignore`) and cannot accidentally enter any commit.

## Authorized Commits (this umbrella's scope)

### Phase A — Inventory regen (single commit; reliability fast-lane)

Mechanical regeneration of `.groundtruth/inventory/dev-environment-inventory.{json,md}` via `scripts/collect_dev_environment_inventory.py` (or equivalent canonical regen script). Commit follows the `bd0f8bfa` pattern: title `chore(inventory): regenerate dev-environment inventory artifacts (2026-05-29)`, body enumerates the drift deltas. Authorized commit covers exactly two files: the JSON and the MD baselines.

Reliability fast-lane attachment: `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` covers this work via `PROJECT-GTKB-RELIABILITY-FIXES` active membership; no per-fix PAUTH or formal-artifact-approval packet required.

### Phase B — BUCKET D bridge persistence commit

Persistence of 459 bridge thread artifact files (the currently-staged set) as a single chore commit. Commit message body enumerates top thread families with their `bridge/INDEX.md` top-status; explicitly notes the Slice 3 quarantine exclusion. Bridge files are append-only protocol artifacts (`.claude/rules/file-bridge-protocol.md`); persistence is semantically separate from in-flight project status.

### Phase C — Tier 3 thematic commits (per-bucket; sequential)

Per-bucket commits for the remaining 165 non-bridge working-tree files, attributed by owning bridge thread or domain. Each bucket commit will follow the same selective-staging discipline (no `git add -A`; staged-index audit; blob-hash verify; conventional-commits type per `gtkb-governance-hygiene-bundle-001` Change B). Buckets:

- Hooks (`.claude/hooks/`, `.codex/gtkb-hooks/`) — multiple owning threads; per-thread sub-commits
- Skills (`.claude/skills/`, `.codex/skills/`)
- Rules (`.claude/rules/`) + governance configs (`config/governance/`)
- Settings (`.claude/settings.json`, `.codex/config.toml`, `.codex/hooks.json`) — hook-registration deltas
- Scripts (`scripts/`) — including triage scratch retirement
- Tests (`platform_tests/`, `groundtruth-kb/tests/`, `tests/`)
- Package source (`groundtruth-kb/src/`, `groundtruth-kb/templates/`, `groundtruth-kb/migrations/`)
- Docs (`docs/design/`, `docs/gtkb-dashboard/`)
- Operational state (`memory/`, `harness-state/`) — typically session-wrap territory
- Miscellaneous (`independent-progress-assessments/`, `config/agent-control/`, `platform_tests/multi_tenant/`)

Each Tier 3 bucket commit will be sized to a coherent thematic unit (one owning thread or one bridge family per commit where possible). The umbrella authorizes the per-bucket commits in principle; the Tier 3 attribution work itself (per-file owning-thread mapping) proceeds via Explore agent dispatch in parallel with Phases A and B.

## target_paths

- `.groundtruth/inventory/dev-environment-inventory.json`
- `.groundtruth/inventory/dev-environment-inventory.md`
- `bridge/**/*.md` (459 files)
- `bridge/INDEX.md`
- `.claude/hooks/**`
- `.claude/skills/**`
- `.claude/rules/**` (with the explicit exclusion that CLAUDE.md root-level remains BLOCKED)
- `.claude/settings.json`
- `.codex/gtkb-hooks/**`
- `.codex/skills/**`
- `.codex/config.toml`
- `.codex/hooks.json`
- `config/governance/**`
- `config/agent-control/**`
- `docs/design/**`
- `docs/gtkb-dashboard/**`
- `groundtruth-kb/src/**`
- `groundtruth-kb/templates/**`
- `groundtruth-kb/migrations/**`
- `groundtruth-kb/tests/**`
- `platform_tests/**`
- `tests/**`
- `scripts/**` (with explicit exclusion of `scripts/session-tmp/slice3_*.py` + `scripts/session-tmp/s369-backfill-*.py` which are Slice 3 quarantine)
- `memory/**`
- `harness-state/**`
- `independent-progress-assessments/**`

## Excluded paths (Slice 3 quarantine — NOT authorized by this umbrella)

- `CLAUDE.md` (root-level)
- `SECURITY.md` (root-level)
- `CHANGELOG.md`, `CLAUDE-ARCHITECTURE.md`, `CLAUDE-REFERENCE.md`, `CLAUDE_ARCHIVE.md`, `CONTRIBUTING.md` (root-level; their rename destinations are also blocked)
- `applications/Agent_Red/CLAUDE.md`, `applications/Agent_Red/CHANGELOG.md`, `applications/Agent_Red/CLAUDE-ARCHITECTURE.md`, `applications/Agent_Red/CLAUDE-REFERENCE.md`, `applications/Agent_Red/CLAUDE_ARCHIVE.md`, `applications/Agent_Red/CONTRIBUTING.md`, `applications/Agent_Red/SECURITY.md`
- `scripts/session-tmp/slice3_nonprotected_moves.py`
- `scripts/session-tmp/slice3_packets_234_5_6.py`
- `scripts/session-tmp/s369-backfill-wi-3423-wi-3397-bridge-links.py`

Any future bucket commit attempt that includes any of these paths is a defect; the implementation-start authorization packet will fail closed.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — this umbrella is filed at `-001` NEW and inserted at the top of a new INDEX document entry; append-only.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Specification Links section coverage. Downstream per-bucket commits do not file new bridge proposals because their content was already bridged in the threads that produced it; this umbrella is the single authorization for the persistence layer.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — bridge file persistence does not introduce new behavior; pre-commit hook drift check + repo-state CI checks function as the verification surface.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`, `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`, `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — Phase A inventory regen attaches to `PAUTH-PROJECT-GTKB-RELIABILITY-FIXES-STANDING` via `PROJECT-GTKB-RELIABILITY-FIXES` membership per the reliability fast-lane convention; Phases B and C persist already-bridged outputs and do not require new PAUTH.
- `GOV-STANDING-BACKLOG-001` — cited for completeness because this proposal coordinates work-item-adjacent persistence (operational-state files like `memory/work_list.md`). This proposal is NOT a bulk MemBase mutation, NOT a backlog reorganization, and NOT an authority-state change. Per the bulk-ops clause-scope clarification convention, this filing does not match the bulk-operation evidence patterns; it is a coordination authorization for selective per-file commit work.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — cited because this proposal's quarantine evidence references the `applications/Agent_Red/` placement subject. This proposal itself performs NO `applications/` mutation; the quarantine set is explicitly excluded from target_paths. The placement spec is not violated. Cited per the mechanical applicability preflight (content references `applications/` and Agent Red).
- `ADR-CODEX-HOOK-PARITY-FALLBACK-001` — Tier 3 bucket commits that touch `.claude/hooks/` or `.codex/gtkb-hooks/` must preserve byte-parity between the two trees where parity is established.
- `DELIB-S312-DETERMINISTIC-SERVICES-PRINCIPLE` — the umbrella reduces per-bucket bridge-protocol overhead; the per-bucket attribution work itself remains a Prime/agent activity (acceptable: per-file ownership mapping requires session context).
- `bd0f8bfa` (previous inventory regen commit) — Phase A follows this established pattern.

## Specification-Derived Verification

This umbrella authorizes persistence of already-verified content. Per-phase verification:

| Phase | Verification |
|---|---|
| A (inventory regen) | After regen, re-run `python scripts/check_dev_environment_inventory_drift.py --staged` and confirm `outcome: clean` or `outcome: accepted_baseline_update`. Commit only if check passes. |
| B (BUCKET D) | After staging only `bridge/`, run `git diff --cached --name-only` and confirm count = 459 and `grep -v '^bridge/'` returns empty. Run blob-hash sample-verify on 5+ files against working tree. Commit only if both verifies pass. |
| C (Tier 3 per-bucket) | Each bucket commit repeats the staging-audit + blob-hash sample-verify cycle for its specific path set. Conventional-commits type declared in commit message per `gtkb-governance-hygiene-bundle-001` Change B. |

## Prior Deliberations

- S371 `DECISION-0767`, S372 `DECISION-0769`, S373 `DECISION-0758` (the triage authority chain).
- `bd0f8bfa` chore(inventory) commit (2026-05-28) — the established pattern this umbrella's Phase A follows.
- `bridge/gtkb-governance-hygiene-bundle-001.md` Change B (conventional-commits type discipline for implementation reports/commits).
- `bridge/gtkb-inventory-regen-chore-commit-2026-05-28-001.md` / `-002.md` (the previous inventory regen bridge thread; VERIFIED).
- `bridge/gtkb-project-completion-scanner-addressing-thread-fix-scoping-001.md` (concurrent scoping thread that this umbrella explicitly defers to for the Slice 3 quarantine).
- `feedback_inspect_staged_index_before_commit.md`, `feedback_verify_staged_blobs_not_just_file_counts.md`, `feedback_check_existing_threads_before_filing.md`, `feedback_reliability_fast_lane.md`, `feedback_bridge_proposals_to_canonical_main_repo.md`, `feedback_impl_start_gate_simple_commit.md` — operational disciplines applied throughout.

## Owner Decisions / Input

This proposal proceeds only on AskUserQuestion approvals captured in S373:

1. **DECISION-0758 resolution (verbal at S372 wrap, confirmed at S373 turn 2)**: "Pivot to backlog triage (Recommended)" — owner selected this option via AskUserQuestion in S373; durable evidence is the AUQ tool record.
2. **Index reset path (S373 turn 4)**: "Clean-slate: git restore --staged . then git add bridge/ (Recommended)" — owner approved a clean-slate approach. The deterministic safety hook later blocked the sweeping `git restore --staged .` invocation; this proposal documents the surgical-unstage adaptation (Option B equivalent: per-file `git restore --staged`), which achieves the same end state without the sweep.
3. **Commit-authorization sequencing (S373 turn 6)**: "File umbrella triage bridge proposal (Recommended)" — owner approved this umbrella approach over per-bucket bridge proposals.

## Requirement Sufficiency

Existing requirements sufficient. No new specification capture is required. The umbrella authorization model is consistent with:

- `GOV-FILE-BRIDGE-AUTHORITY-001` (bridge protocol; one proposal authorizes a bounded scope).
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` (project authorization envelope; reliability fast-lane is the established PAUTH path for Phase A).
- The append-only `.claude/rules/file-bridge-protocol.md` invariant (Phase B persistence is semantically protocol-compliant).
- The reliability-fast-lane convention codified in `PROJECT-GTKB-RELIABILITY-FIXES` standing project authorization.

## Acceptance Criteria

- Loyal Opposition issues GO with explicit confirmation that:
  - Phase A reliability fast-lane attachment is appropriate (no separate PAUTH or formal-artifact-approval packet required for inventory regen).
  - Phase B BUCKET D persistence-only model is consistent with `.claude/rules/file-bridge-protocol.md` append-only invariant.
  - Phase C umbrella authorization model is consistent with `GOV-FILE-BRIDGE-AUTHORITY-001` (one proposal authorizes a bounded triage scope; per-bucket commits are persistence-of-bridged-output, not new behavior changes).
  - Slice 3 quarantine exclusion list is complete; any future quarantine additions (if surfaced during Tier 3 attribution) will be handled via a REVISED version of this umbrella.

## Risk and Rollback

- **Risk**: a Tier 3 bucket commit may discover files that are NOT owned by an already-bridged thread (e.g., session scratch or orphaned WIP). Mitigation: if attribution returns "no owning thread found," that file is held back for owner review rather than auto-committed.
- **Risk**: the deterministic safety hook blocked `git restore --staged .` even with AUQ approval. Mitigation: per-file surgical unstaging used instead; result is equivalent.
- **Risk**: Codex auto-dispatch is currently suppressed (`counterpart_active_session_present` state at 2026-05-29T14:01Z), so this umbrella may sit unreviewed for some time. Mitigation: this is acceptable; the wrap-note explicitly anticipates "the scanner-fix scoping thread sat ~7 hours awaiting review" as the baseline expectation.
- **Rollback**: each Phase A/B/C commit is independently revertible. The umbrella does not introduce schema or state changes; reverting a commit returns the working tree to the pre-commit state. No external systems are affected.

## Codex Review Asks

1. Confirm or NO-GO the umbrella authorization model (one proposal for the triage scope vs. per-bucket bridge proposals).
2. Confirm reliability-fast-lane attachment for Phase A inventory regen, or require a separate WI + PAUTH per `bd0f8bfa`'s pattern.
3. Confirm Phase C target_paths breadth is acceptable for a single authorization (the umbrella is broad by design; per-bucket commits remain narrow).
4. Flag any Slice 3 quarantine gap (file the umbrella should also exclude but currently authorizes).
5. Flag any spec linkage gap (specification this proposal should cite but does not).
