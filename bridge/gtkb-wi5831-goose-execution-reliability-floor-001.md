NEW
::init gtkb pb
::open build

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: bba2e933-5d36-4c5b-ad04-08a653c8700f
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code proposal-author worker dispatched under the DELIB-202667735 delegated-authoring mandate; ambient native session bba2e933 with a transcript-resolved prime-builder envelope; authoring-only scope - no implementation, commit, or review in this session

bridge_kind: prime_proposal
Document: gtkb-wi5831-goose-execution-reliability-floor
Version: 001
Date: 2026-07-31 UTC

Project Authorization: PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730
Project: PROJECT-GTKB-HARNESS-TEST-CORRECTIONS
Work Item: WI-5831

target_paths: ["scripts/goose_harness.py", "scripts/goose_execution_guard.py", "config/agent-control/goose-execution-floor.toml", "platform_tests/scripts/test_goose_execution_guard.py", "platform_tests/scripts/test_goose_harness_reliability_floor.py"]
implementation_scope: harness_execution_reliability_detection_floor
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

# WI-5831 Implementation Proposal — Goose Execution Reliability Floor: Write Verification, Tool-Call Leak Detection, and Post-Compaction Provenance Guard

## Summary

Give the Goose harness (identity `G`) a mechanical floor that converts three silent failure classes observed across the 2026-07-30 nine-run evaluation into loud, detectable errors at the harness boundary:

1. **Silent zero-byte writes reported as success.** A run wrote both of its target files as zero bytes and reported the writes as successful; the defect was caught only because that run's Prime Builder re-verified its own output by hand. Absent that voluntary re-check, an implementation report would have been filed against two empty files.
2. **Tool-call serialization leaks that stall a session until the owner nudges it.** Three model lanes emitted tool calls as ordinary assistant *text* that was never executed — a DeepSeek DSML leak, nine dead text-form tool-call emissions in the GLM lanes, and raw tool-call text in the Qwen lane. The wrapper returns the final assistant text and exit `0`, so a stalled session is indistinguishable from a completed one.
3. **Post-compaction provenance drift stamping the wrong author model into formal artifacts.** Within one Goose session id, an artifact filed after a context compaction carried a Claude model identifier in a DeepSeek lane — a direct GOV-DOCUMENT-AUTHOR-PROVENANCE-001 exposure.

The remedy is a detection floor, not a behavior rewrite: a new guard module invoked by the existing wrapper that (a) reconciles claimed writes against on-disk bytes and independently sweeps the run window for zero-byte artifacts, (b) classifies leaked tool-call text and terminal stalls, and (c) re-derives author-model provenance from the live spawn model configuration and refuses to let a drifted artifact pass unnoticed. Every finding produces a structured diagnostic and a distinct non-zero exit code. Every bound and every pattern set is a configuration value; the diff introduces no timer, retry, or throttle literal.

This proposal is filed as the next numbered bridge file `bridge/gtkb-wi5831-goose-execution-reliability-floor-001.md`, continuing the append-only versioned bridge file chain. No prior versions are deleted or rewritten; the numbered bridge files form the canonical append-only audit trail per GOV-FILE-BRIDGE-AUTHORITY-001, and dispatcher/TAFE bridge state plus these status-bearing numbered files remain the canonical workflow state.

## Problem Statement And Live Evidence (fresh reads, 2026-07-31)

All claims below were re-derived this session from the live worktree, a fresh `gt backlog show WI-5831 --json`, a fresh `gt tests show TEST-11787 --json`, a fresh `gt projects show-authorization` read, and direct reads of the cited bridge files and evidence ledger. Line numbers are current-worktree references.

### 1. The wrapper is a thin CLI shim with no post-run verification

`scripts/goose_harness.py` (207 lines) wraps `goose run --no-session --quiet --output-format json` (lines 121-132), parses the returned JSON (line 177), walks the message list in reverse for the last assistant message (lines 191-199), prints its text blocks, and returns `0`. There is no inspection of tool requests, no reconciliation of claimed file writes against on-disk state, no leak classification, and no provenance check. The only non-zero exits are subprocess timeout (line 160), missing CLI (line 166), non-zero child return code (line 173), unparseable JSON (line 183), and structurally empty output (lines 188, 202).

Consequence: any failure that still yields a well-formed JSON payload with a terminal assistant text block — including a leaked tool call rendered as prose, and including a turn that "wrote" an empty file — is reported to the caller as exit `0` with human-readable text. This is the mechanical root of failure classes (1) and (2).

### 2. The Goose lane has no shared-base write interception

`scripts/goose_harness.py` does not import `scripts/cloud_harness_base.py`; verified by direct read. Goose executes file operations inside its own CLI extension surface, and the in-root `.goose/` tree contains only skill adapters and their manifest (verified: `.goose/skills/MANIFEST.json` is the sole in-root file). The shared cloud-harness base is therefore **not** on the Goose write path, so its write-dispatch surface is not the correct repair site for this work item.

That surface is worth noting for a sibling observation rather than for this scope: the shared base's write dispatch (`scripts/cloud_harness_base.py` lines 1909-1929) writes content and returns a success string with no size or content assertion, so the same "empty write reported as success" shape is structurally reachable on the cloud-harness lanes too. That is an out-of-scope observation recorded here for backlog capture, not a target of this proposal.

Because the wrapper is the only in-root interception point for harness `G`, the floor is implemented as pre-spawn environment derivation plus post-run verification over the run payload and the run window. This is stated plainly because it bounds what the design can honestly promise: the guard detects and surfaces, it cannot prevent a bad write mid-loop.

### 3. Zero-byte write class — evidence and current disk state

The defect record (`gt backlog show WI-5831 --json`, fresh read) states that run r1 wrote **both** target files as zero bytes while reporting success, and that only the Prime Builder's own re-verification caught it. The disk no longer preserves the zero-byte state — `scripts/harness_probe_dsv4pro-r1.py` is 7,773 bytes and `platform_tests/scripts/test_harness_probe_dsv4pro-r1.py` is 13,653 bytes at read time — because the same run re-wrote them after self-detection. The zero-byte state is therefore attested by the work-item record and the transcript-diagnosis phase, not by surviving on-disk bytes. This proposal does not claim otherwise, and the verification plan below uses constructed fixtures rather than asserting against unrecoverable historical state.

### 4. Leak and stall class — evidence

The defect record enumerates three lanes: a DeepSeek DSML serialization leak at 22:49Z in r1, nine dead text-form tool-call emissions across the GLM runs, and raw tool-call text in the Qwen lane. Each stalled the session until the owner nudged it. Grepping the filed bridge chain for leak markers returns nothing — the leaks lived in the interactive transcripts and the four transcript diagnoses, not in filed artifacts. This too is stated rather than papered over: the leak evidence is transcript-borne, so the implementation must build its fixture corpus from the recorded pattern classes rather than from replayable in-repo payloads.

### 5. Provenance-drift class — exact-verified in the filed chain

This class **is** directly verifiable in-repo, and it is the sharpest evidence in the work item:

- `bridge/gtkb-wi5808-harness-probe-dsv4pro-r3-001.md` header: session context id `G-2026-07-30T19-27-10Z`, author model `deepseek-v4-pro`, author model version `deepseek-v4-pro`, metadata source `interactive_session_envelope`.
- `bridge/gtkb-wi5808-harness-probe-dsv4pro-r3-003.md` header, **same session context id** `G-2026-07-30T19-27-10Z`, later in the same run: author model `claude-opus-4`, author model version `20250729`, metadata source `goose-harness-transcript`.

One session, one lane, two irreconcilable author-model stamps — the later one naming a model that was never running in that lane. The run-evidence ledger records the same finding in its diagnosis-phase synthesis ("post-compaction provenance drift (claude-opus-4 stamped into a DeepSeek artifact)", `.gtkb-state/owner-decisions/20260730-harness-test-run-evidence-ledger.md`). The mechanism is context decay: after compaction the model re-derives its header from stale in-context text rather than from live session configuration. Nothing in the current wrapper or the Goose lane compares a filed artifact's stamped provenance against what the harness actually spawned.

### 6. Timer-governance state

`config/governance/timer-inventory.toml` does **not** exist yet (verified this session); WI-5804 produces it and WI-5806 externalizes hard-coded timer values to the canonical configuration store per DELIB-202667722. The three pre-existing literals in `scripts/goose_harness.py` (the default max-turns, subprocess-timeout, and session-timeout constants, lines 23-25) predate this work item and are not modified here. This proposal adds no counterpart literals; see the Configuration Surface And Timer Discipline subsection.

## Proposed Design

One new guard module holds all detection logic; the existing wrapper gains derivation and invocation only. The split keeps `scripts/goose_harness.py` — the one file this work item shares with WI-5812 — as thin as possible.

### Slice A — Write verification: claimed writes reconciled, run window swept

`scripts/goose_execution_guard.py` gains two complementary detectors.

**A1. Write-claim reconciliation (payload-aware).** Walk the parsed goose run payload for tool-request and tool-response pairs whose tool name matches the configured write-tool name set. For each request, record the declared target path and the declared content length; for each paired response that reports success, verify post-run that the target exists and that its on-disk byte length is consistent with the declared content. A success-reported write whose target is absent, or is zero-length while non-empty content was declared, is a `write_claim_unfulfilled` finding naming the tool call, the path, the declared length, and the observed length.

The exact block shape of the Goose payload must be confirmed against a captured run payload at implementation time. The extractor is therefore written shape-tolerant, and — this is the load-bearing part — when it does not recognize the payload shape it records `write_claim_reconciliation: unavailable` in its diagnostic. It never reports `verified` for a check it could not perform. Fabricated green is the failure mode this whole work item exists to remove.

**A2. Run-window zero-byte sweep (schema-independent floor).** Independent of any goose-internal shape, bound a candidate set with `git --no-optional-locks status --porcelain` plus `git --no-optional-locks ls-files --modified --others --exclude-standard`, restrict it to files whose modification time falls inside the run window between spawn start and run completion, and report every candidate that is zero bytes and is not matched by the configured intentional-empty allowlist (package marker files and similar). This is the detector that would have caught the r1 incident with no dependence on payload schema, and it remains authoritative for the zero-byte class even when A1 reports `unavailable`.

**Outcome contract.** Any A1 or A2 finding emits a structured JSON diagnostic on stderr and returns a distinct non-zero exit code from the wrapper, so no caller can read the run as success.

### Slice B — Tool-call leak and stall detection

A leak detector scans assistant text blocks for leaked tool-call serializations drawn from the configured pattern classes: text-form tool-call envelopes (the GLM class), DeepSeek DSML tool-call markers (the r1 22:49Z class), and raw function-call or JSON tool envelopes rendered as prose (the Qwen class). The pattern set lives in configuration; the module ships no inline pattern literal, so a newly observed leak dialect is a configuration addition rather than a code change.

Findings are classified as:

- `leaked_tool_call_text` — a tool call serialized into assistant text with no corresponding executed tool request in the same turn.
- `terminal_leak_stall` — the run's terminal assistant message is itself a leak, or the run ended at the turn cap with no terminal assistant text. This is the exact shape that produced the observed owner-nudge stalls, and the exact shape the current wrapper reports as exit `0`.

Default disposition is **explicit failure**: a structured diagnostic naming the pattern class, the turn index, and a bounded excerpt of the offending span, plus a distinct non-zero exit code. Bounded retry is available but disabled by default (the retry-attempts setting defaults to `0` in configuration), because re-spawning a whole interactive-equivalent session is expensive and non-idempotent; making retry opt-in keeps the cheap deterministic signal in front of the expensive action, consistent with the poller-retirement lesson in `.claude/rules/bridge-essential.md`. When retry is enabled, both the attempt count and the backoff come from configuration.

### Slice C — Post-compaction provenance guard

**Live derivation.** The guard resolves the model configuration the wrapper actually spawned — the model argument when supplied, otherwise the routing default the wrapper resolved from `.api-harness/routing.toml` — as the single source of author-model truth for that spawn, and exports it into the child environment using the author-metadata field environment-variable names already registered in `scripts/bridge_author_metadata.py`. The wrapper *reads* those registered names; it adds nothing to that module and modifies nothing in it, which is what keeps this work item off WI-5812's editing surface.

**Post-run re-derivation check.** For every file under `bridge/` created or modified inside the run window, parse the author-metadata header block and compare the stamped author model and author model version against the live spawn model configuration. A mismatch is a `provenance_drift` finding naming the file, the stamped values, and the live values, with a distinct non-zero exit code. Had this existed on 2026-07-30, the `claude-opus-4` stamp in the DeepSeek r3 lane would have failed the run instead of entering the filed chain.

This is deliberately a detect-and-surface guard, not a rewriter. It does not edit artifacts, does not alter the attestation chain WI-5812 establishes, and does not adjudicate which value is correct — it refuses to let a contradiction pass unnoticed. Silent auto-correction of provenance would be a worse failure mode than loud detection, because it would erase the evidence that a compaction-induced drift happened at all.

### Configuration Surface And Timer Discipline

`config/agent-control/goose-execution-floor.toml` is the new configuration surface: a schema version, a write-verification table (enable flag, write-tool name set, intentional-empty allowlist), a leak-detection table (named pattern classes, retry attempts, retry backoff), and a provenance-guard table (enable flag, scan scope). Precedent for a `config/` target path in this program is `bridge/gtkb-wi5804-timer-inventory-evidence-classification-001.md`, which declares `config/governance/timer-inventory.toml`.

Timer discipline per DELIB-202667722: every bound this work item introduces — retry attempts, retry backoff, and any window tolerance — is a configuration value, not an inline literal. The guard module and the wrapper diff contain zero new timeout, interval, retry, or throttle literals; a drift-lock test asserts this against the touched surfaces. Coordination with WI-5806 is registration, not duplication: these values are declared in the new configuration surface in the shape WI-5804's inventory records and WI-5806's externalization consumes, so the externalization program inherits them rather than discovering them later as fresh hard-coded debt.

### Rejected alternatives

- **Repair the write dispatch in the shared cloud-harness base.** Rejected for this work item: that surface is not on the Goose write path (verified by direct read), so it would fix a different lane and leave WI-5831's observed defects untouched. Its own missing size assertion is recorded above as an out-of-scope observation for backlog capture.
- **Intercept writes mid-loop inside the Goose CLI.** Rejected: Goose's tool execution is internal to the vendor CLI and its configuration lives outside the project root, so there is no in-root interception point. Claiming otherwise would be a capability overclaim.
- **Auto-correct drifted provenance in place.** Rejected: rewriting a stamped header would destroy the drift evidence and would silently mutate a filed artifact, colliding with the append-only chain discipline. Detection with a loud failure preserves both the artifact and the evidence.
- **Automatic full-session retry on any leak.** Rejected as the default: it spends an expensive resource on every occurrence with no cheap gate in front of it, the exact anti-pattern recorded in the poller-retirement history. Retry stays configuration-gated and off by default.
- **Fail the run whenever the payload shape is unrecognized.** Rejected: it would convert an ordinary vendor-schema change into a total outage of the harness. The chosen posture reports `unavailable` for the payload-aware check while the schema-independent sweep continues to bind.

## Specification Links

- `GOV-HARNESS-ONBOARDING-CONTRACT-001` — required (blocking) — WI-5831's source specification and the source specification of TEST-11787; a harness that reports zero-byte writes as success, stalls silently on leaked tool calls, and stamps drifted provenance is below the capability floor this contract sets for a GT-KB coding harness.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — required (blocking) — the provenance contract directly breached by the exact-verified r3 drift evidence; Slice C is its mechanical detection surface for the Goose lane.
- `GOV-FILE-BRIDGE-AUTHORITY-001` — required (blocking) — the append-only numbered bridge file chain this proposal joins, and the chain whose artifacts Slice C inspects without editing any of them.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — required (blocking) — this proposal's own specification-linkage obligation.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — required (blocking) — governs the downstream verification phase; the Specification-Derived Verification Plan below is the derivation record the reviewer executes against.
- `GOV-ARTIFACT-APPROVAL-001` — required (blocking) — no formal MemBase artifact is created, updated, or retired by this implementation; bridge artifacts and the project authorization chain remain under the approval gate.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — required (blocking) — this proposal proceeds under the active list-free project authorization cited in the header, which does not replace the bridge GO, the claim, or the implementation-start packet.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — required (blocking) — root-boundary containment: every declared target path is an in-root platform surface under the GT-KB root; no adopter application subtree and no out-of-root dependency is touched.
- `GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001` — required (blocking) — this work item adds a mechanical enforcement layer at the harness boundary rather than relying on agent self-discipline, which is the enforcement posture this specification requires.
- `DCL-CROSS-HARNESS-ENFORCEMENT-001` — advisory — the recorded intended-but-partial gap that leaves Goose outside the Claude-side write-time hook surface; this work item narrows the practical consequence for three failure classes without claiming to close the gap.
- `GOV-SOURCE-OF-TRUTH-FRESHNESS-001` — advisory — every state claim in this proposal derives from a fresh canonical read made this session, and Slice C's core principle is that live configuration outranks stale in-context values.
- `GOV-DETERMINISTIC-SERVICES-PRINCIPLE-001` — advisory — the guard converts a manual, voluntary, easily-skipped re-verification habit into a deterministic service that runs on every spawn.
- `SPEC-1662` — advisory — assertion quality: the tests below assert behavioral outcomes (findings raised, exit codes returned, diagnostics emitted) rather than structural presence.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — advisory — the structured run diagnostic is a durable evidence artifact rather than transient console noise.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — advisory — traceability across work item, proposal, tests, report, and verification.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — advisory — defect-origin work-item lifecycle transitions for WI-5831.
- `GOV-STANDING-BACKLOG-001` — advisory — WI-5831 in MemBase is the sole work authority for this proposal; no parallel authority is created.
- `GOV-HARNESS-STATE-SOT-CONSOLIDATION-001` — advisory — harness identity and role reads stay on the canonical registry readers; this work item creates no new harness-state surface.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — advisory — the project-authorization triple and inline-JSON target paths in the header satisfy this proposal's linkage obligation.
- Deliberations cited: `DELIB-202667735`, `DELIB-202667726`, `DELIB-202667730`, `DELIB-202667731`, `DELIB-202667722`.

## Prior Deliberations

- **DELIB-202667735** — Delegated proposal authoring and unblock-implementation mandate with role-transition plan: the owner mandate under which this proposal-author worker files this NEW entry. The same directive plans harness `G` transitioning to the implementer-worker role once the DeepSeek lanes unblock, which raises the stakes on this work item: the harness about to take the implementer seat is the one whose execution floor is being repaired here.
- **DELIB-202667726** — Program pause + Harness Test program directive: the originating owner mandate for the Harness Test program whose nine-run evaluation produced every defect this proposal addresses.
- **DELIB-202667730** — Harness Test final synthesis (DeepSeek V4 Pro recommended; corrections project created): the synthesis whose diagnosis phase separates model-caused from platform-caused failures and attributes this work item's three classes to the platform side.
- **DELIB-202667731** — Harness Test Corrections whole-project authorization decision: the owner's list-free whole-project grant recorded as the project authorization cited in this proposal's header, fresh-verified this session as active with null included and excluded work-item lists and no expiry.
- **DELIB-202667722** — Timer and throttle governance is a first-class concern (relaxed-first bias, registry visibility, no hard-coded values): the constraint honored by putting every bound introduced here into the configuration surface, with a drift-lock test.
- Every deliberation, specification, work-item, and test identifier cited anywhere in this proposal was checked this session by read-only exact-id lookup against the live MemBase; no insert, update, or other record write was performed. The bridge evidence was checked by direct reads of the numbered files.

## Owner Decisions / Input

1. **DELIB-202667735** — the owner's delegated proposal-authoring mandate for the parallel-operation program authorizes this worker to file this NEW proposal for WI-5831. Authoring-only: this filing performs no implementation, no commit, and no review.
2. **DELIB-202667731 / AUQ-20260730-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-GRANT** — the owner's list-free whole-project grant (`PAUTH-PROJECT-GTKB-HARNESS-TEST-CORRECTIONS-WHOLE-PROJECT-20260730`) covers WI-5831 as a member work item of `PROJECT-GTKB-HARNESS-TEST-CORRECTIONS`. Per that grant's scope, this work item still requires its own full governed cycle: this proposal, an independent Loyal Opposition GO carrying complete Clause Applicability evidence, a fresh work-intent claim, an implementation-start packet before any mutation, exact target-path enforcement, both ruff gates plus tests, an implementation report, and an independent VERIFIED with governed atomic finalization.
3. **DELIB-202667726** — the Harness Test program directive is the program lineage under which the evaluation evidence was produced and the corrections program chartered.
4. No additional owner decision is required to review this proposal. This proposal does not itself authorize implementation.

## Requirement Sufficiency

**Existing requirements sufficient.** The WI-5831 defect description (fresh-read verified via `gt backlog show WI-5831 --json`), TEST-11787's recorded expected outcome (fresh-read verified via `gt tests show TEST-11787 --json`), GOV-HARNESS-ONBOARDING-CONTRACT-001, GOV-DOCUMENT-AUTHOR-PROVENANCE-001, GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001, and DELIB-202667722 fully constrain this implementation. No new or revised specification is required before implementation.

## Specification-Derived Verification Plan (Spec-to-Test Mapping)

MemBase test record `TEST-11787` ("Goose-lane writes and provenance survive stalls and compaction", source specification GOV-HARNESS-ONBOARDING-CONTRACT-001) is the spec-derived test anchor created with WI-5831 per GOV-12. Its recorded expected outcome is the acceptance spine of this plan, verbatim: *"A zero-byte post-write is detected and surfaced; author_model in artifacts filed after a compaction matches the session model configuration; leak-pattern stalls produce a detectable error rather than silence."*

All tests are fixture-rooted: constructed run payloads, a temporary git-backed worktree fixture for the sweep, and constructed bridge-header fixtures. No test spawns the Goose CLI, mutates live bridge state, or asserts against unrecoverable historical run state.

| Requirement source | Test | Behavior asserted |
|---|---|---|
| TEST-11787 clause 1 / GOV-HARNESS-ONBOARDING-CONTRACT-001 | `test_zero_byte_write_claim_is_detected` | A payload claiming a successful write of non-empty content to a path that is zero bytes on disk yields a `write_claim_unfulfilled` finding naming path, declared length, and observed length |
| TEST-11787 clause 1 / GOV-CROSS-CUTTING-REQUIREMENTS-MECHANICAL-ENFORCEMENT-001 | `test_run_window_sweep_detects_zero_byte_artifact` | The schema-independent sweep flags a zero-byte file created inside the run window in a temporary git fixture, with no payload parsing involved |
| TEST-11787 clause 1 (fail loud, not fail silent) | `test_unknown_payload_shape_reports_unavailable_not_verified` | An unrecognized payload shape yields `write_claim_reconciliation: unavailable`, never `verified`, while the sweep still runs and still binds |
| TEST-11787 clause 1 (no false positives) | `test_intentional_empty_allowlist_not_flagged`, `test_zero_byte_file_outside_run_window_not_flagged` | Allowlisted intentional-empty files and pre-existing zero-byte files outside the run window produce no finding |
| TEST-11787 clause 3 / WI-5831 leak class | `test_glm_text_form_tool_call_leak_detected`, `test_dsml_marker_leak_detected`, `test_raw_tool_call_text_leak_detected` | Each recorded leak dialect (text-form tool-call envelope, DSML marker, raw tool-call text) is classified as `leaked_tool_call_text` with turn index and bounded excerpt |
| TEST-11787 clause 3 (stall shape) | `test_terminal_leak_stall_detected`, `test_turn_cap_without_terminal_text_detected` | A terminal assistant message that is itself a leak, and a run ending at the turn cap with no terminal assistant text, each yield `terminal_leak_stall` |
| TEST-11787 clause 3 (detectable error rather than silence) | `test_leak_finding_returns_nonzero_exit_and_structured_diagnostic` | The wrapper returns a distinct non-zero exit code and emits a structured JSON diagnostic on stderr instead of printing leaked text with exit `0` — the exact current behavior at `scripts/goose_harness.py` lines 190-202 |
| TEST-11787 clause 3 (no false positives) | `test_clean_run_returns_zero_and_prints_terminal_text` | A clean payload preserves today's behavior: terminal assistant text printed, exit `0`, no findings |
| TEST-11787 clause 2 / GOV-DOCUMENT-AUTHOR-PROVENANCE-001 | `test_provenance_drift_detected_against_live_spawn_model` | A bridge-header fixture stamped with a model other than the live spawn model configuration yields a `provenance_drift` finding naming file, stamped values, and live values — the r3-001 versus r3-003 shape |
| TEST-11787 clause 2 (matching case) | `test_matching_provenance_passes` | A header whose stamped author model and version match the live spawn model configuration produces no finding |
| GOV-DOCUMENT-AUTHOR-PROVENANCE-001 (detect, never rewrite) | `test_provenance_guard_never_edits_artifacts` | Every fixture file under the bridge fixture directory is byte-identical before and after the guard runs |
| GOV-HARNESS-ONBOARDING-CONTRACT-001 / live derivation | `test_live_model_configuration_exported_using_registered_field_names` | The wrapper derives the spawn model configuration from the resolved model argument or routing default and exports it under the author-metadata field environment-variable names already registered in `scripts/bridge_author_metadata.py`, without modifying that module |
| DELIB-202667722 (timer discipline) | `test_no_new_timer_literals_in_touched_surfaces` | The guard module and the wrapper diff contain no new timeout, interval, retry, or throttle literal; retry attempts and backoff resolve from the configuration surface |
| DELIB-202667722 / configuration schema | `test_execution_floor_config_schema_and_defaults` | The configuration surface parses, carries a schema version, and defaults retry attempts to `0` (explicit-failure posture) |
| ADR-ISOLATION-APPLICATION-PLACEMENT-001 | `test_guard_paths_are_in_root` | The guard resolves and operates only on paths under the project root; no adopter application subtree or out-of-root path is read or written |

## Acceptance Criteria

1. `ruff check` and `ruff format --check` both pass clean on every changed Python file (two separate gates).
2. `python -m pytest platform_tests/scripts/test_goose_execution_guard.py platform_tests/scripts/test_goose_harness_reliability_floor.py -q --tb=short` passes green.
3. A payload claiming a successful write whose target is zero bytes on disk causes the wrapper to exit non-zero with a structured diagnostic; the same run today exits `0`.
4. A zero-byte artifact created inside the run window is detected by the schema-independent sweep with no dependence on payload shape.
5. An unrecognized payload shape reports `write_claim_reconciliation: unavailable` and never reports `verified`.
6. Each of the three recorded leak dialects, plus both stall shapes, produces a classified finding and a distinct non-zero exit code.
7. A clean run is unchanged: terminal assistant text is printed and the wrapper exits `0`.
8. A bridge artifact whose stamped author model disagrees with the live spawn model configuration produces a `provenance_drift` finding; a matching artifact produces none; no artifact is edited by the guard in either case.
9. The diff introduces zero new hard-coded timer, interval, retry, or throttle literals, and the three pre-existing literals in `scripts/goose_harness.py` are unmodified.
10. No target path overlaps WI-5815's declared target paths, and the only path shared with WI-5812 is `scripts/goose_harness.py`, edited after WI-5812 lands.

## Risk And Rollback

- **Payload-schema assumption risk.** The Goose run payload's tool-block shape is not confirmed in-repo. Mitigated structurally: A1 is shape-tolerant and reports `unavailable` rather than `verified` when it cannot parse, and A2 provides a schema-independent floor for the zero-byte class. Residual risk is that A1 contributes nothing until a captured payload is available; A2 still delivers the work item's primary outcome.
- **False-positive risk on the run-window sweep.** A concurrent unrelated process could create a zero-byte file inside the window. Mitigated by the git-bounded candidate set, the modification-time window, and the configured intentional-empty allowlist, with negative tests for each. Residual risk is a noisy failure rather than a missed defect, which is the correct direction for a reliability floor.
- **Leak-pattern coverage risk.** A future model may leak in a dialect not in the configured pattern set. Mitigated by making patterns configuration rather than code, so coverage extends without a code change; the stall detector also catches the turn-cap shape independent of dialect.
- **Provenance-guard scope risk.** Comparing a stamped header against the live spawn model configuration presumes the wrapper's derived configuration is correct. Mitigated by deriving it from what the wrapper actually invoked and by reusing the registered field names rather than inventing a parallel identity source; the guard reports contradictions and never adjudicates or rewrites them.
- **Sequencing risk with WI-5812.** Both work items edit `scripts/goose_harness.py`. Mitigated by strict sequencing and by function-scoped edits; see the Coordination Note.
- **Rollback** is the exact revert of the wrapper diff plus deletion of the new guard module, the new configuration surface, and the two new test modules. Nothing in this work item is stateful: no MemBase record, no dispatcher or TAFE state, no bridge chain file, and no harness-state record is touched, so a revert restores the prior behavior completely.

## Coordination Note (sequencing constraint, not scope)

**WI-5812 — sequenced strictly after.** `bridge/gtkb-wi5812-goose-governed-filing-attestation-003.md` (REVISED, awaiting a fresh GO) declares `scripts/goose_harness.py` among its target paths; its Slice D adds per-spawn session-id minting plus harness-name and session-id injection into the spawned child environment. WI-5831 implementation MUST be sequenced after WI-5812 lands through its own governed cycle. The two diffs are complementary rather than overlapping: WI-5812 owns *identity* injection, WI-5831 owns *model-configuration* derivation plus post-run verification, and WI-5831 extends the same injection site rather than replacing it. WI-5831 duplicates none of WI-5812's four slices — it adds no attestation branch, no author-metadata resolution entry, and no session-id environment-variable registry entry. If the landed WI-5812 diff has moved or renamed the injection site, the implementing session re-baselines line references before editing and records the re-baseline in the implementation report.

**WI-5815 — disjoint by construction.** `bridge/gtkb-wi5815-per-session-envelope-claim-isolation-001.md` declares `groundtruth-kb/src/groundtruth_kb/session/envelope.py`, `groundtruth-kb/src/groundtruth_kb/cli_session_handoff.py`, `scripts/session_self_initialization.py`, `scripts/gtkb_session_id.py`, `scripts/bridge_claim_cli.py`, and five test modules. WI-5831's five target paths intersect that set nowhere. WI-5831 adds no per-session envelope uniqueness enforcement and no claim-CLI change; it consumes whatever identity WI-5815 establishes and asserts nothing about how that identity is minted.

**WI-5806 and WI-5804 — registration, not duplication.** `config/governance/timer-inventory.toml` does not exist yet. WI-5831 declares its bounds in its own configuration surface in the shape the inventory records and the externalization consumes, so WI-5806 inherits them rather than discovering them later as fresh hard-coded debt. WI-5831 neither creates nor edits the timer inventory artifact.

## DISARM — KB Mechanics

This implementation creates and modifies source, configuration, and test files only. No MemBase records — no specifications, ADRs, DCLs, GOV records, work items, Deliberation Archive entries, or test records — are created, updated, inserted, or retired by this work, and no direct database edit of any kind is performed. The `kb_mutation_in_scope: false` flag accurately reflects a pure source, configuration, and test change; the specification, deliberation, work-item, and test identifiers cited throughout this proposal are read-only references rather than mutations. Any KB write elsewhere in the wider cycle, such as a work-item stage transition, follows its own governed path and is not performed by this implementation.

## DISARM — Packet Mechanics

The implementation-start packet (`scripts/implementation_authorization.py begin --bridge-id gtkb-wi5831-goose-execution-reliability-floor`, run only after an independent Loyal Opposition GO) is session-local implementation-scope evidence. It is not a formal artifact under GOV-ARTIFACT-APPROVAL-001 and requires no separate approval packet of its own, because it mutates no canonical record and writes no governed artifact; it derives from TAFE and dispatcher bridge state, the approved proposal file, and the GO verdict file, it expires, and it fails closed on bridge status drift. The project-authorization triple cited in this proposal's header supplies the project-authorization evidence the packet validator consumes; it never broadens the declared target paths and never replaces the live latest-GO requirement, the fresh work-intent claim, or the packet itself.

## Recommended Commit Type

Recommended commit type: **feat** — justified over `fix` because the diff's substance is a new capability surface rather than a repair of broken logic. `scripts/goose_harness.py` contains no write-verification, leak-detection, or provenance-comparison code to correct; nothing in it malfunctions against its current contract. This work item adds a new guard module, a new configuration surface, and a new detection contract at the harness boundary, and wires the existing wrapper into them. The *motivation* is defect evidence (WI-5831 carries defect origin), which is why `fix` is arguable; the *diff* is net-new detection capability with new regression coverage, and labeling roughly five new surfaces `chore` or `fix` is precisely the mis-categorization the Conventional Commits type discipline exists to prevent. If Loyal Opposition reads the absent verification as itself the defect, `fix` is an acceptable substitute and this proposal defers to that reading.

## Loyal Opposition Review Questions

1. Is the two-detector split in Slice A the right posture — a payload-aware reconciliation that reports `unavailable` when it cannot parse, plus a schema-independent run-window sweep that always binds — or should the payload-aware branch be deferred entirely until a captured Goose payload is available to specify it against?
2. Is explicit failure (retry attempts defaulting to `0`) the correct default disposition for a detected leak, or should a bounded configuration-driven retry be enabled by default given that the observed stalls required owner nudges to clear?
3. Is detect-and-surface the right scope for Slice C, or should the guard additionally refuse the spawn when live model configuration cannot be derived at all — a stricter fail-closed posture that would block runs rather than only failing them after the fact?
4. Does the sequencing plan hold: WI-5831 strictly after WI-5812, sharing only `scripts/goose_harness.py`, with WI-5815's target paths untouched?
5. Does the fixture-rooted verification plan satisfy the specification-derived testing requirement for every linked specification, given that the zero-byte and leak evidence are transcript-borne rather than replayable from in-repo state?

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
