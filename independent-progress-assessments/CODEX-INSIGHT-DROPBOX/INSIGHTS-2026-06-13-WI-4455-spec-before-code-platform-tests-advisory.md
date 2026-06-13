WIs: WI-4455, WI-4449, WI-3183, WI-3184
Specs: GOV-FILE-BRIDGE-AUTHORITY-001, DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, GOV-STANDING-BACKLOG-001

# WI-4455 Loyal Opposition Advisory: spec-before-code Platform Tests Coverage

Date: 2026-06-13
Author: loyal-opposition/codex/A
Scope: Read-only review of live hook state, managed hook template behavior, FAB-20 bridge evidence, and MemBase linkage for `platform_tests/` source-path coverage.

## Claim

`WI-4455` is correctly captured as a real governance-design gap, but the live checkout has changed since the backlog item was filed. The active root hook at `.claude/hooks/spec-before-code.py` is now a recovery stub that emits no advisory. The false-positive behavior still exists in the managed scaffold/template hook at `groundtruth-kb/templates/hooks/spec-before-code.py`, and the hook's current tests preserve that source_paths-only model.

Prime Builder should not re-enable or restore the managed template into `.claude/hooks/spec-before-code.py` unchanged. Doing so would recreate the same advisory miss for `platform_tests/` files whose authoritative spec linkage is carried by bridge proposal/report evidence rather than by `specifications.source_paths`.

## Evidence

- Live root hook is disabled: `.claude/hooks/spec-before-code.py:1-13` is a recovery stub from commit `e90b2f0301` and exits 0 without output. A local payload for `platform_tests/scripts/test_gtkb_hygiene_investigation.py` produced empty stdout and exit 0.
- Managed template still implements source_paths-only matching: `groundtruth-kb/templates/hooks/spec-before-code.py:49-81` queries only `specifications.source_paths`, and `:145-150` emits "No specification found covering <path>" when no source_paths row matches.
- The template reproduces the WI-4455 symptom today. Running the template hook with an `Edit` payload for `platform_tests/scripts/test_gtkb_hygiene_investigation.py` emitted: `[Governance] No specification found covering platform_tests/scripts/test_gtkb_hygiene_investigation.py. Create or update a spec with source_paths before writing source code.`
- The test suite targets the template, not the live stub: `groundtruth-kb/tests/test_governance_hooks.py:14` points `HOOKS_DIR` at `groundtruth-kb/templates/hooks`, and `:480-509` asserts the no-match advisory behavior.
- FAB-20 bridge evidence links the platform test through bridge-governed verification instead of per-file source_paths: `bridge/gtkb-fab-20-hygiene-investigation-skill-007.md:21` includes `platform_tests/**` in target_paths, `:196-203` maps bridge/spec requirements to the report, and `:210-216` records executed pytest/ruff checks for `platform_tests/scripts/test_gtkb_hygiene_investigation.py`.
- Live MemBase source_paths coverage for platform tests is sparse. A direct `current_specifications` query found one current spec with `platform_tests` source_paths, and it does not include `platform_tests/scripts/test_gtkb_hygiene_investigation.py`.
- The template is still a managed artifact source: `groundtruth-kb/templates/managed-artifacts.toml:213-223` maps `hooks/spec-before-code.py` to `.claude/hooks/spec-before-code.py`, and `:704-716` registers `spec-before-code.py` on `PreToolUse`.

## Risk / Impact

Severity: P1 governance drift, preserving the backlog P0 urgency as implementation priority.

The immediate user-facing warning is suppressed in this checkout by the WI-4449 recovery stub, so this is not an active live-hook noise incident at the moment. The risk is revival drift: any Stage 3 governance-hook restoration, scaffold upgrade, or managed-artifact overwrite that copies the current template back into the active hook will reintroduce a noisy advisory for bridge-linked `platform_tests/` edits.

That false signal matters because `platform_tests/` are often the spec-derived verification layer for bridge work. If the hook treats those tests as unspecced solely because no canonical spec row carries the exact file in `source_paths`, it pushes agents toward either ignoring governance warnings or doing a broad source_paths backfill without first deciding the correct authority model.

## Recommended Action

1. Do not restore the current managed template unchanged into `.claude/hooks/spec-before-code.py`.
2. Decide the intended coverage model for `platform_tests/` before re-enabling the hook:
   - Option A: teach the hook to recognize bridge-thread evidence for test files, using a bounded lookup from file path to bridge target_paths/spec-to-test mapping.
   - Option B: perform an reviewed source_paths backfill for platform test files, with a generated inventory and bridge-reviewed mapping.
   - Option C: keep `platform_tests/` advisory-only or explicitly exempt until Option A or B is implemented.
3. Add regression coverage against the selected model. At minimum, include a fixture for `platform_tests/scripts/test_gtkb_hygiene_investigation.py` or an equivalent bridge-linked platform test so source_paths-only behavior cannot be restored silently.
4. Link this work to WI-4449 before implementation, because the root hook is currently a recovery stub and Stage 3 hook restoration is the likely collision point.

## Prime Builder Context

Objective: Restore useful spec-before-code signal without noisy false positives for bridge-linked platform tests.

Preconditions: Live bridge queue should not have pending LO work; Prime should have an approved proposal before changing hook/template/test behavior. Check whether WI-4449 Stage 3 is already being implemented before filing a separate proposal.

Evidence paths:
- `.claude/hooks/spec-before-code.py`
- `groundtruth-kb/templates/hooks/spec-before-code.py`
- `groundtruth-kb/tests/test_governance_hooks.py`
- `groundtruth-kb/templates/managed-artifacts.toml`
- `bridge/gtkb-fab-20-hygiene-investigation-skill-007.md`
- `groundtruth.db` views `current_specifications` and `current_work_items`

Likely file touchpoints:
- `groundtruth-kb/templates/hooks/spec-before-code.py`
- `groundtruth-kb/tests/test_governance_hooks.py`
- Possibly `.claude/hooks/spec-before-code.py` only as part of the approved hook-restoration thread.

Verification steps:
- Reproduce no advisory for bridge-linked platform tests under the chosen coverage model.
- Preserve warning behavior for genuinely uncovered source files.
- Run `groundtruth-kb\.venv\Scripts\python.exe -m pytest groundtruth-kb\tests\test_governance_hooks.py -q --tb=short`.
- Run targeted ruff check/format on changed hook/test files.

Rollback notes: Leave the root hook as the WI-4449 recovery stub if the replacement model is not ready; do not partially restore the source_paths-only template.

Open decisions: None for this LO advisory. Prime may need an owner-visible choice later if selecting between bridge-derived coverage and source_paths backfill changes governance semantics.

## Verification Performed

- Read live `bridge/INDEX.md` directly; LO actionable scan returned zero `NEW`/`REVISED` items at selection time.
- Confirmed Codex harness A is assigned `loyal-opposition` in the root durable registry and root-scoped `python -m groundtruth_kb.cli harness roles`.
- Queried `current_work_items` for P0/P1 open work and selected WI-4455 after checking duplicate-effort risk against recent reports.
- Ran live and template hook reproduction with the same `platform_tests/scripts/test_gtkb_hygiene_investigation.py` payload.
- Queried `current_specifications` for `platform_tests` source_paths coverage.
- No product/source implementation files were modified.
