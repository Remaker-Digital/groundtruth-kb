GO
author_identity: cursor
author_harness_id: E
author_session_context_id: cursor-e-20260626-wi4818-review
author_model: composer
author_model_version: composer-2.5
author_model_configuration: Cursor interactive; session role loyal-opposition

# Bridge Review — gtkb-wi4818-storm-watchdog-cursor-coverage-001

bridge_kind: proposal_review
Document: gtkb-wi4818-storm-watchdog-cursor-coverage
Version: 002 (GO)
Date: 2026-06-26 UTC
Responds-To: bridge/gtkb-wi4818-storm-watchdog-cursor-coverage-001.md (NEW)
Project: PROJECT-GTKB-DISPATCHER-RELIABILITY
Work Item: WI-4818

---

## Applicability Preflight

- packet_hash: `sha256:eb913bc56d51e78d4da1d05802b14b8529899fb939543dd2f757c2e437317d65`
- bridge_document_name: `gtkb-wi4818-storm-watchdog-cursor-coverage`
- content_source: `bridge_file_operative`
- content_file: `bridge/gtkb-wi4818-storm-watchdog-cursor-coverage-001.md`
- operative_file: `bridge/gtkb-wi4818-storm-watchdog-cursor-coverage-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- warnings.spec_links_section: {"status": "harvested", "candidate_heading": null}
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]

| Spec | Severity | Cited | Matched By |
|------|----------|-------|------------|
| `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` | `advisory` | `no` | content:deliberation |
| `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | `advisory` | `no` | content:candidate, content:verified |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `blocking` | `yes` | doc:*, content:Specification Links |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `blocking` | `yes` | doc:*, content:VERIFIED, content:verification, content:spec-to-test |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` | `advisory` | `no` | content:owner decision, content:requirement, content:specification, content:ADR, content:DCL, content:work item, content:backlog |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `blocking` | `yes` | doc:*, path:bridge/** |

## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-wi4818-storm-watchdog-cursor-coverage`
- Operative file: `bridge/gtkb-wi4818-storm-watchdog-cursor-coverage-001.md`
- Clauses evaluated: 5
- must_apply: 3, may_apply: 2, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.

| Clause | Spec | Applicability | Evidence found | Severity | Enforcement |
|---|---|---|---|---|---|
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001/CLAUSE-IN-ROOT` | `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | may_apply | — | blocking | blocking |
| `GOV-FILE-BRIDGE-AUTHORITY-001/CLAUSE-NUMBERED-FILE-CHAIN-IS-CANONICAL` | `GOV-FILE-BRIDGE-AUTHORITY-001` | must_apply | yes | blocking | blocking |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001/CLAUSE-CONCRETE-LINKS` | `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001/CLAUSE-SPEC-TO-TEST-MAPPING` | `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | must_apply | yes | blocking | blocking |
| `GOV-STANDING-BACKLOG-001/CLAUSE-VISIBILITY-BULK-OPS` | `GOV-STANDING-BACKLOG-001` | may_apply | — | blocking | blocking |

## Review Summary

The proposal correctly identifies a real unattended-safety gap: dispatched Cursor workers run `scripts/cursor_harness.py`, but `harness_storm_watchdog.ps1` only watches `ollama_harness.py` and `openrouter_harness.py`, so Cursor dispatch roots are never gathered or reaped. The one-line watched-set fix is proportionate; the pure decider needs no change. Preflights pass; governance metadata and spec-to-test mapping are adequate.

## Claim-by-Claim Verification

### 1. Watched-script set omits Cursor

**Verified.** `$NONCODEX_HARNESS_SCRIPTS = @('ollama_harness.py', 'openrouter_harness.py')` at `harness_storm_watchdog.ps1:56`; `cursor_harness.py` is absent.

### 2. Gather predicate excludes Cursor dispatch processes

**Verified.** Non-codex candidates require `$invokesWatchedHarness` matching `$NONCODEX_HARNESS_SCRIPT_PATTERN` plus project python path checks (`harness_storm_watchdog.ps1:75-86`). A `cursor_harness.py` process fails the first predicate and never enters `$candidates`.

### 3. Registry declares Cursor headless dispatch via python script

**Verified.** Harness `E` carries headless argv `groundtruth-kb/.venv/Scripts/python.exe` + `scripts/cursor_harness.py` (`harness-registry.json` lines 163-172). `scripts/cursor_harness.py` exists and is the headless dispatch shim.

### 4. Pure decider is harness-agnostic

**Verified.** `storm_watchdog_reap.decide_reap()` consumes only `Process.dispatched` and lease metadata; existing unit tests already treat generic `python` dispatched roots (`test_storm_watchdog_reap.py`). No decider change required.

### 5. Interactive Cursor IDE is out of reap scope

**Verified.** Watchdog marks only processes matching watched harness scripts (or `codex exec`) as candidates; the interactive IDE surface is `kind: ide`, not a `cursor_harness.py` python invocation. Risk claim is sound.

### 6. Governance metadata

**Verified.** Project Authorization, Project, Work Item, spec links, owner decision (`DELIB-20266135`), and verification plan present; preflights pass.

## Prior Deliberations

- `DELIB-20266135` — owner decision to draft/file WI-4818 under bounded PAUTH envelope.
- `DELIB-20266104` — surgical liveness-aware storm-watchdog reaper this fix extends.
- `DELIB-20265899` — dispatcher architecture authorization.
- `DELIB-20266132` / `DELIB-20266133` — dispatcher reliability re-scope context.

## Residual Risks / Implementation Notes (non-blocking)

1. **Parity test belongs in `test_harness_storm_watchdog.py`, not `test_storm_watchdog_reap.py`.** The repo already has `test_watchdog_covers_registry_lowcost_backends()` in `platform_tests/scripts/test_harness_storm_watchdog.py`, which reads the `.ps1` and registry but filters only `low-cost`-tagged harnesses — that is why Cursor was never caught. Extend or replace that test rather than adding coverage logic to the pure-decider test module.
2. **Registry expected-set filter must not use `can_receive_dispatch` alone.** Current projection shows `can_receive_dispatch: false` for all python-script harnesses (D/E/F); eligibility is overlay-controlled. Derive expected scripts from **active** harnesses whose headless argv includes `scripts/*_harness.py` (python-dispatch backends), excluding codex/claude/gemini invocations. Pre-fix expected set is `{ollama_harness.py, openrouter_harness.py, cursor_harness.py}`; post-fix watchdog set must be a superset.
3. **Retire or supersede the low-cost-only assertion** in `test_watchdog_covers_registry_lowcost_backends` so two conflicting coverage definitions do not coexist.
4. **Claude headless (`claude -p`) remains uncovered** — correctly out of scope here; if the broadened parity test flags it, capture as an advisory finding rather than blocking this WI.

## Verdict

**GO.** Add `cursor_harness.py` to `$NONCODEX_HARNESS_SCRIPTS` and land a registry-derived parity guard in the watchdog test module (updating the existing low-cost-only test). No change to `storm_watchdog_reap.py` or dispatch trigger behavior.
