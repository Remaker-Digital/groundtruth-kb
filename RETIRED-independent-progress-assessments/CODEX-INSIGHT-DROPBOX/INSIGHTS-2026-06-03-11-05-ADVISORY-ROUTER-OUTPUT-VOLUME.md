# Advisory Router Output Volume Advisory

Specs: SPEC-LO-OPPORTUNITY-RADAR-001, GOV-STANDING-BACKLOG-001
WIs: WI-4179

Session type: Loyal Opposition opportunity radar
Reviewer: Codex / Loyal Opposition
Generated: 2026-06-03T11:05:00Z

## Claim

The advisory-router dry-run path is idempotent and clean, but its default operator output is too large for recurring automation sessions. A dry run with no new advisory work scanned 745 sources, would create 0 rows, and still emitted the complete `skipped_existing` list. This is a token-cost smell, not a correctness defect.

## Evidence

- Command: `$env:PYTHONPATH='E:\GT-KB\groundtruth-kb\src'; python scripts\advisory_backlog_router.py --dry-run --source both`
- Observed result: `created: []`, `errors: []`, `scanned: 745`, and a full `skipped_existing` array for every already-routed advisory source.
- `scripts/advisory_backlog_router.py:88-95` includes the complete `skipped_existing` list in `RouterResult.as_json()`.
- `scripts/advisory_backlog_router.py:394-402` appends one object per existing advisory match.
- `scripts/advisory_backlog_router.py:365-368` already writes compact state counts, proving the deterministic summary fields exist.
- `scripts/advisory_backlog_router.py:457-458` prints the full JSON payload unconditionally from the CLI entry point.

## Risk / Impact

Recurring Loyal Opposition automation uses the router as a quick "is there anything new?" check. When the common result is "nothing new," printing hundreds of already-routed rows adds no decision value and can crowd out more relevant bridge/backlog evidence. The underlying router behavior appears healthy; the output shape is the problem.

## Opportunity Radar

- Defect pass: no router correctness defect found; dry-run remained non-mutating and reported zero errors.
- Token-savings pass: the default CLI emits hundreds of low-value skipped rows when counts would answer the operator question.
- Deterministic-service pass: a compact summary is deterministic because the router already computes `scanned`, `created_count`, `skipped_existing_count`, and `errors_count`.
- Surface-eligibility pass: this belongs in the router CLI/API, likely as `--summary`, `--counts-only`, or a default human summary with full JSON behind an explicit flag.
- Routing pass: preserve as a Loyal Opposition advisory so Prime can convert it into a small implementation proposal when appropriate.

## Recommended Action

Prime Builder should add a compact output mode for `scripts/advisory_backlog_router.py` and keep full per-row output available only when explicitly requested. The acceptance shape should include a test proving dry-run summary output reports counts without serializing every skipped advisory.

## Decision Needed From Owner

None. This is a low-risk future-work advisory and does not request source, config, or MemBase mutation in this session.
