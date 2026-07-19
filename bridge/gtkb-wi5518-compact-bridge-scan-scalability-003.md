NEW
::init gtkb lo
::open build

# GT-KB Bridge Implementation Report - gtkb-wi5518-compact-bridge-scan-scalability - 003

bridge_kind: implementation_report
Document: gtkb-wi5518-compact-bridge-scan-scalability
Version: 003 (NEW; post-implementation report)
Responds to GO: bridge/gtkb-wi5518-compact-bridge-scan-scalability-002.md
Approved proposal: bridge/gtkb-wi5518-compact-bridge-scan-scalability-001.md
Project Authorization: PAUTH-DISPATCHER-BLACK-BOX-WI5518-COMPACT-SCAN-SCALABILITY-20260718
Project: PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-DISPATCHER-BLACK-BOX-HARDENING
Work Item: WI-5518
Recommended commit type: perf:

author_identity: prime-builder/codex/A
author_harness_id: A
author_session_context_id: 019f5f66-9582-7f03-a3f1-3c75e6bd9d0a
author_model: gpt-5.6-sol
author_model_version: gpt-5.6-sol
author_model_configuration: Codex desktop interactive; reasoning_effort=xhigh; transcript-defined Prime Builder role

target_paths: [".claude/skills/bridge/helpers/scan_bridge.py", ".codex/skills/bridge/helpers/scan_bridge.py", ".cursor/skills/bridge/helpers/scan_bridge.py", "groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py", "platform_tests/scripts/test_scan_bridge.py"]

## Implementation Claim

WI-5518 replaces the live and managed-template compact scanner's
read-every-version path with a filename-first current-thread inventory. Compact
mode now reads one physical-latest status per current thread, reads older files
only for invalid-latest fallback or a Prime Builder GO's operative
NEW/REVISED ancestry, preserves acknowledged-archive classification, and keeps
the existing full scan archival-complete.

The `.claude`, `.codex`, and `.cursor` live helpers remain byte-identical. The
adopter template has equivalent compact read bounds and output projection while
retaining its distinct terminal-work-item blocking behavior.

Implementation started only after live GO v002, the matching PB work-intent
claim, and schema-v3 packet
`sha256:ddda2f067afc046e308977f962c7894a0c63c7448e9a51be08442157713d9287`
authorized all five exact targets.

## Specification Links

- `SPEC-DISPATCH-REPORT-WORKFLOW-COMPACT-001`
- `SPEC-CENTRALIZED-DISPATCH-SERVICE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001`
- `GOV-WORK-TREE-HYGIENE-001`
- `ADR-CROSS-HARNESS-PARITY-001`
- `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001`
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Owner Decisions / Input

No new owner decision is required.
`DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` remains the
owner-decision basis for the active WI-5518 PAUTH. The owner's dispatcher
configuration hold was preserved: this implementation changed no dispatcher or
TAFE configuration, runtime, claim, lease, eligibility, routing, daemon,
worker, credential, external system, deployment, release, or Git history.

## Prior Deliberations

- `DELIB-20260715-FLEET-HARNESS-DEFECT-REPAIR-AUTHORIZATION` - authorizes bounded governed defect repair while preserving every downstream gate.
- `DELIB-202666121` - establishes the bounded, read-only compact-workflow precedent whose role semantics remain unchanged.
- `DELIB-202665650` - establishes compactness without a competing source of truth.

No cited deliberation rejects the filename-first current-thread inventory.

## Specification-Derived Verification Plan

| Spec / governing surface | Executed verification evidence |
| --- | --- |
| `SPEC-DISPATCH-REPORT-WORKFLOW-COMPACT-001` | Focused pytest adds deterministic many-version read instrumentation for both roles and compares normalized compact versus full classifications; 32 tests passed. |
| `SPEC-CENTRALIZED-DISPATCH-SERVICE-001` | Source inspection and tests confirm the helper remains a read-only projection over numbered bridge files; no cache, alternate queue, or runtime artifact was added. |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Live applicability preflight passed with `missing_required_specs: []`, `missing_advisory_specs: []`, and no blocking errors; numbered files remain authority. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` | GO v002, active PAUTH, matching PB claim, schema-v3 implementation-start packet, and five successful operation-time target validations preceded edits. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | This report carries forward the exact PAUTH, project, and WI-5518 linkage. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Applicability preflight packet `sha256:8820c9997a527707611a1e9d796b38abbddc2b894e4b489ae48dbb260150cefe` passed with all required and advisory links present. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | The complete focused module executed: 32 passed with one pre-existing unknown-`asyncio_mode` warning. |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Deterministic normalized compact/full equivalence tests passed for both live and template helpers; full mode and existing fixtures remained green. |
| `GOV-WORK-TREE-HYGIENE-001` | Report planning found exactly five changed implementation files and excluded 1,815 unrelated dirty paths; exact diff-check passed. |
| `ADR-CROSS-HARNESS-PARITY-001` | SHA-256 for the three live helpers is identical: `19C809BD2E47003577451121E9BC6830C2DD14C8043D16A26D1A77C52D143F47`. |
| `DCL-CROSS-HARNESS-PARITY-ENFORCEMENT-001` | A/B/E live helper projections are byte-identical; C/D/F/H have no repo-local helper target; the adopter template's equivalent compact behavior is tested separately. |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Every changed implementation and test path is within `E:/GT-KB`; no external dependency or evidence path is used. |
| `GOV-STANDING-BACKLOG-001` | WI-5518 and TEST-11589 remain the canonical defect and regression carriers; no duplicate was created. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | The defect remains reconstructable through WI-5518, TEST-11589, PAUTH, proposal, GO, implementation report, tests, and pending independent verdict. |
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | The implementation preserves the full numbered chain and full-mode archive detail while compact mode projects only current evidence. |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Proposal, GO, claim/start, implementation, this NEW report, pending verdict, and focused commit remain distinct lifecycle transitions. |

## Commands Run

```text
groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_scan_bridge.py -q --tb=short
groundtruth-kb/.venv/Scripts/ruff.exe check .claude/skills/bridge/helpers/scan_bridge.py .codex/skills/bridge/helpers/scan_bridge.py .cursor/skills/bridge/helpers/scan_bridge.py groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py platform_tests/scripts/test_scan_bridge.py
groundtruth-kb/.venv/Scripts/ruff.exe format --check .claude/skills/bridge/helpers/scan_bridge.py .codex/skills/bridge/helpers/scan_bridge.py .cursor/skills/bridge/helpers/scan_bridge.py groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py platform_tests/scripts/test_scan_bridge.py
groundtruth-kb/.venv/Scripts/python.exe -m py_compile .claude/skills/bridge/helpers/scan_bridge.py .codex/skills/bridge/helpers/scan_bridge.py .cursor/skills/bridge/helpers/scan_bridge.py groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py platform_tests/scripts/test_scan_bridge.py
git diff --check -- .claude/skills/bridge/helpers/scan_bridge.py .codex/skills/bridge/helpers/scan_bridge.py .cursor/skills/bridge/helpers/scan_bridge.py groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py platform_tests/scripts/test_scan_bridge.py
groundtruth-kb/.venv/Scripts/python.exe scripts/bridge_applicability_preflight.py --bridge-id gtkb-wi5518-compact-bridge-scan-scalability
groundtruth-kb/.venv/Scripts/python.exe scripts/adr_dcl_clause_preflight.py --bridge-id gtkb-wi5518-compact-bridge-scan-scalability
groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/scan_bridge.py --role loyal-opposition --compact --format json
groundtruth-kb/.venv/Scripts/python.exe .codex/skills/bridge/helpers/scan_bridge.py --role prime-builder --compact --format json
```

## Observed Results

- Focused pytest: `32 passed, 1 warning in 0.57s`. The warning is the existing unknown `asyncio_mode` configuration warning.
- Ruff check: `All checks passed!`
- Ruff format check: `5 files already formatted`.
- Python compilation: exit 0 for all five files.
- Exact diff check: exit 0; only non-blocking Windows LF-to-CRLF notices were emitted.
- Live helper parity: all three SHA-256 values are `19C809BD2E47003577451121E9BC6830C2DD14C8043D16A26D1A77C52D143F47`.
- Applicability preflight: PASS; no missing required/advisory specs and no blocking errors. The known partial-suffix `bridge/helpers/scan_bridge.py` parent-directory warning remains non-blocking.
- Clause preflight: PASS; five clauses evaluated, four `must_apply`, one `may_apply`, zero evidence gaps, zero blocking gaps.
- Deterministic live fixture: compact/full normalized results match for both roles; compact status reads are bounded to four current threads plus one PB GO ancestry read, while full mode reads all historical versions.
- Deterministic template fixture: compact/full normalized results match for both roles; compact reads exactly four current files while full mode reads 32 historical versions.
- Live compact inventory probe: 2,103 included current threads, zero excluded archived threads, 2,248 status reads, 4.303 seconds. The 145 reads above current-thread count are required invalid-latest fallback or PB GO proposal ancestry.
- Live LO compact CLI: 3.94 seconds.
- Live PB compact CLI: 360.38 seconds. The filename-first inventory is only 4.303 seconds; the residual wall time is the preserved per-GO `_go_activatable` authorization-diagnostic path. Duplicate backlog searches for `activatability` and `authorization diagnostics` found no separate carrier. This residual is outside WI-5518's five-path scope and is not hidden or treated as a WI-5518 read-bound failure.

## Files Changed

- `.claude/skills/bridge/helpers/scan_bridge.py`
- `.codex/skills/bridge/helpers/scan_bridge.py`
- `.cursor/skills/bridge/helpers/scan_bridge.py`
- `groundtruth-kb/templates/skills/bridge/helpers/scan_bridge.py`
- `platform_tests/scripts/test_scan_bridge.py`

Excluded out-of-scope dirty paths: 1,815. No out-of-scope path was edited,
staged, committed, restored, cleaned, stashed, or reverted by this
implementation.

## Cross-Harness Disposition

- A (Codex), B (Claude Code), and E (Cursor): applicable live helper copies; byte-identical and covered by the focused module.
- C (Antigravity), D (Ollama), F (OpenRouter), and H (Alibaba): not applicable; no repo-local `scan_bridge.py` helper target exists for these harnesses.
- Managed adopter template: applicable; equivalent compact semantics are tested while its terminal-work-item profile remains intact.

## Recommended Commit Type

`perf(bridge)` - the change bounds compact read work without changing bridge
authority or adding a new user-facing capability.

Diff summary: five files, 579 insertions, 40 deletions.

## Acceptance Criteria Status

- [x] Compact scans read one physical-latest status per current thread plus only invalid-latest fallback and PB GO ancestry required for classification.
- [x] Many-version fixtures prove compact bridge-content reads do not grow with unrelated terminal history.
- [x] Normalized Prime Builder and Loyal Opposition compact results match full-mode summary, actionable, blocked, terminal, and archive classifications.
- [x] Full mode retains complete version chains, terminal payloads, excluded archive details, and GO activatability diagnostics.
- [x] Existing inline, NO-ACTION, terminal-kind, archive, unreadable-file, and template terminal-work-item behavior remains green.
- [x] The three live helper copies are byte-identical; the template has equivalent bounded behavior without losing its profile.
- [x] No cache, index, alternate queue, dispatcher/TAFE state, MemBase mutation, harness contact, or runtime mutation was introduced.
- [x] Focused pytest, Ruff, compilation, exact diff, applicability, clause, and hash-parity gates pass; independent VERIFIED and focused commit remain pending.

## Risk And Rollback

Residual risk is concentrated in two areas. First, PB GO activatability remains
operationally slow even after compact bridge-content reads are bounded; the
360.38-second measurement above makes that limitation explicit and requires a
separate governed defect because its implementation surface is outside this
PAUTH. Second, future archive-token changes could drift from the compact mirror;
the focused parity test fails closed against the canonical versioned-file
classifier.

Rollback requires separate authority and reverts only the five exact WI-5518
implementation/test hunks, then reruns the complete focused evidence set.
Numbered bridge files, WI-5518, TEST-11589, PAUTH, and independent verdict
history remain append-only.

## Loyal Opposition Asks

1. Independently rerun the focused pytest, Ruff, format, compilation, exact-diff, applicability, clause, and live-helper hash checks.
2. Verify compact/full normalized classification equivalence and the current-thread read bound for both live and template helpers.
3. Confirm the 360.38-second PB residual is accurately disclosed as preserved GO-activatability work outside WI-5518's target scope.
4. Return VERIFIED only if every linked specification and acceptance criterion is satisfied; otherwise return NO-GO with concrete findings.

