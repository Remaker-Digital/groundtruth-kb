NO-GO

bridge_kind: lo_verdict
Document: gtkb-ollama-tool-numeric-argument-coercion
Version: 002
Author: Loyal Opposition (Codex, harness A)
Date: 2026-06-07 UTC
Reviewer: Loyal Opposition
Responds to: bridge/gtkb-ollama-tool-numeric-argument-coercion-001.md
Verdict: NO-GO

# Loyal Opposition Review - Ollama Tool Numeric Argument Coercion

## Verdict

NO-GO.

The proposed fix is technically well scoped and addresses a live P1 bridge-dispatch defect, but the implementation proposal is missing the required machine-readable target-path metadata for source/test mutation. Prime Builder must revise the proposal before this can receive GO, because a GO on the current text would not reliably mint an implementation-start packet for `scripts/ollama_harness.py` and the focused Ollama harness test path.

## Review Scope

- Read live `bridge/INDEX.md`; latest status for this thread was `NEW: bridge/gtkb-ollama-tool-numeric-argument-coercion-001.md`.
- Read the full thread chain, currently version `001`.
- Inspected current `scripts/ollama_harness.py`; `Read.max_chars`, `Grep.max_results`, and `Glob.max_results` still use direct `int(...)` casts.
- Confirmed existing Ollama harness tests live in `platform_tests/scripts/test_ollama_harness.py` and related `platform_tests/scripts/test_ollama_*.py` modules.
- Checked MemBase project/work state: `WI-4393` is an open P1 reliability defect in `PROJECT-GTKB-RELIABILITY-FIXES`, and the standing reliability fast-lane authorization is active for source/test reliability work.
- Ran mandatory bridge applicability and ADR/DCL clause preflights.
- Ran Deliberation Archive search before review.

## Applicability Preflight

Command:

```text
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-ollama-tool-numeric-argument-coercion
```

Observed result:

```text
## Applicability Preflight

- packet_hash: `sha256:8061508294b7ac9f3c9a6104f251b63ac18fdff64bb1b84aa3f66f6a5c4e719a`
- bridge_document_name: `gtkb-ollama-tool-numeric-argument-coercion`
- content_source: `indexed_operative`
- content_file: `bridge/gtkb-ollama-tool-numeric-argument-coercion-001.md`
- operative_file: `bridge/gtkb-ollama-tool-numeric-argument-coercion-001.md`
- preflight_passed: `true`
- warnings.missing_parent_dirs: []
- missing_required_specs: []
- missing_advisory_specs: ["ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001", "DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001", "GOV-ARTIFACT-ORIENTED-GOVERNANCE-001"]
```

The missing specs are advisory, not blocking. Prime should add them in the revision if the revised text continues to discuss artifact lifecycle, deliberation, or work-item evidence.

## Clause Applicability

Command:

```text
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-tool-numeric-argument-coercion
```

Observed result:

```text
## Clause Applicability (Slice 2; mandatory gate)

- Bridge id: `gtkb-ollama-tool-numeric-argument-coercion`
- Operative file: `bridge\gtkb-ollama-tool-numeric-argument-coercion-001.md`
- Clauses evaluated: 5
- must_apply: 4, may_apply: 1, not_applicable: 0
- Evidence gaps in must_apply clauses: 0
- Blocking gaps (gate-failing): 0
- Mode: **mandatory** (default invocation). Exit 5 = blocking gap; exit 0 = pass.
```

## Prior Deliberations

Deliberation Archive search was run before this verdict:

```text
uv run --project groundtruth-kb gt deliberations search "WI-4393 Ollama harness numeric argument coercion tool dispatcher float string" --limit 10 --json
```

Relevant results:

- `DELIB-20260897` - prior VERIFIED Ollama Phase 2 dispatch wiring baseline.
- `DELIB-20260901` - prior VERIFIED Ollama full LO dispatch test update baseline.
- `DELIB-20260909` - prior VERIFIED Ollama dispatch failure-hardening baseline; relevant predecessor but does not cover integral float-string coercion.
- `DELIB-2088`, `DELIB-2137`, and `DELIB-2162` - broader cross-harness / single-harness dispatcher history.

No searched deliberation blocks the proposed fix.

## Backlog And Dependency Check

`WI-4393` is open, P1, and attached to `PROJECT-GTKB-RELIABILITY-FIXES`. The proposal is a dependency-unblocking reliability fix for Ollama Loyal Opposition dispatch, not duplicate work. It is also related to `WI-4388`, but the current failure mode is distinct: the worker crashes after dispatch because local tool numeric parsing rejects model-emitted integral float strings.

## Findings

### F1 - Missing machine-readable target-path metadata blocks implementation-start authorization

Severity: P1 governance drift / implementation blocker.

Observation: The proposal requests source and test mutation, and its prose `## Proposed Change Scope` lists target files, but the artifact does not include a required `target_paths: [...]` metadata line or a recognized `## target_paths` / `## Files Expected To Change` section.

Evidence:

- `bridge/gtkb-ollama-tool-numeric-argument-coercion-001.md` lists:
  - `scripts/ollama_harness.py`
  - `platform_tests/scripts/test_ollama_harness_numeric_args.py` or an existing Ollama harness test module
- `.claude/rules/file-bridge-protocol.md` requires implementation proposals that request source, test, script, hook, configuration, deployment, repository-state, or KB-mutation work to include `target_paths` metadata.
- `scripts/implementation_authorization.py:535` extracts only inline `target_paths: [...]`, `## Files Expected To Change`, or `## target_paths`; the current `Target files:` prose heading is not one of those recognized forms.

Impact: Prime Builder could receive GO but then fail to mint the required implementation-start authorization packet, or the packet could omit the intended source/test files. That would recreate the same stranded-work condition currently visible on other bridge-dispatch work.

Recommended action: File a REVISED proposal that adds exact machine-readable target-path metadata, for example:

```text
target_paths: ["scripts/ollama_harness.py", "platform_tests/scripts/test_ollama_harness.py", "platform_tests/scripts/test_ollama_harness_numeric_args.py"]
```

If Prime chooses to extend only the existing test module, omit the new test-file path. If Prime chooses a new focused module, keep both the new file and the existing module only if both are expected to change.

## Positive Confirmations

- The defect is live in current source: `scripts/ollama_harness.py` still directly casts optional numeric tool arguments with `int(...)`.
- The work item is real and high priority: `WI-4393` is open, P1, and describes the same integral float-string crash class.
- The proposed behavior is appropriately narrow: accept positive integral numeric forms for bounded tool arguments, reject malformed/nonintegral/nonpositive/boolean values, and preserve guard behavior.
- The hard preflights report no missing required specs and no blocking clause gaps.

## Required Revision

Prime Builder should file `REVISED` with:

1. A recognized target-path surface: inline `target_paths: [...]`, `## target_paths`, or `## Files Expected To Change`.
2. Exact target paths aligned to the implementation choice:
   - `scripts/ollama_harness.py`
   - either `platform_tests/scripts/test_ollama_harness.py`, a new `platform_tests/scripts/test_ollama_harness_numeric_args.py`, or both if both will be touched.
3. The advisory specs if the revised text continues to trigger them: `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`, `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`, and `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`.
4. The same focused spec-derived verification plan, including accepted and rejected numeric forms plus existing guard behavior preservation.

## Commands Executed

```text
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-ollama-tool-numeric-argument-coercion --format json --preview-lines 260
python scripts\bridge_applicability_preflight.py --bridge-id gtkb-ollama-tool-numeric-argument-coercion
python scripts\adr_dcl_clause_preflight.py --bridge-id gtkb-ollama-tool-numeric-argument-coercion
rg -n "int\(|max_chars|max_results|_dispatch_read|OllamaHarnessError|Read|max_" scripts\ollama_harness.py platform_tests\scripts\test_ollama_harness*.py
uv run --project groundtruth-kb gt backlog list --id WI-4393 --json
uv run --project groundtruth-kb gt projects show PROJECT-GTKB-RELIABILITY-FIXES --json
uv run --project groundtruth-kb gt deliberations search "WI-4393 Ollama harness numeric argument coercion tool dispatcher float string" --limit 10 --json
rg --files platform_tests\scripts | rg "ollama_harness|ollama|harness"
```

## Owner Decisions / Input

No owner decision is requested by this verdict.

File bridge scan contribution: 1 entry processed.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
