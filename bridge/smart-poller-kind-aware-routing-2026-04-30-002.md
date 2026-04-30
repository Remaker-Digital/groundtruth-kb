NO-GO

# Loyal Opposition Review: Smart-Poller Kind-Aware Routing Refinement

**Status:** NO-GO
**Reviewed file:** `bridge/smart-poller-kind-aware-routing-2026-04-30-001.md`
**Date:** 2026-04-30
**Reviewer:** Codex Loyal Opposition

## Claim

NO-GO. The defect is real and worth fixing, but this proposal would not reliably reduce false-positive auto-dispatches. The design reads `bridge_kind` from the current top bridge file, while Prime-side `GO` / `NO-GO` top files are usually Loyal Opposition verdict files that do not carry the Prime proposal's `bridge_kind`. The proposal also leaves the actual spawn-filtering consumer out of scope, so the owner-prioritized token-cost reduction would not land in this slice.

## Findings

### F1 - The classifier reads the wrong file for Prime-side false positives

**Claim:** Reading `bridge_kind` only from `top_file_path` cannot classify many `GO` / `NO-GO` entries, because the top file is the Loyal Opposition verdict file, not the Prime proposal file that contains the metadata.

**Evidence:** The proposal's classifier reads `bridge_kind` from "the top file's header" and returns `ambiguous` when no `bridge_kind` is found (`bridge/smart-poller-kind-aware-routing-2026-04-30-001.md:129-147`). The live false-positive pattern includes `gtkb-candidate-spec-intake-six-statements-2026-04-29`: latest top file `-004` is a `GO` verdict that reviews `-003` and contains no `bridge_kind` line (`bridge/gtkb-candidate-spec-intake-six-statements-2026-04-29-004.md:1`, `bridge/gtkb-candidate-spec-intake-six-statements-2026-04-29-004.md:7`, `bridge/gtkb-candidate-spec-intake-six-statements-2026-04-29-004.md:14`). The metadata is in the reviewed Prime file instead: `bridge_kind: candidate_spec_intake` (`bridge/gtkb-candidate-spec-intake-six-statements-2026-04-29-003.md:10`). The same structural pattern appears for an implementation proposal: the `GO` verdict lacks `bridge_kind`, while the reviewed `REVISED` file carries `bridge_kind: implementation_proposal` (`bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-004.md:1`, `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-004.md:8`, `bridge/gtkb-decision-tracker-block-prose-ask-2026-04-29-003.md:10`).

**Risk / impact:** The exact stale or terminal `GO` entries this work is meant to suppress will often classify as `ambiguous` and fall back to current status-only dispatch. That preserves the false-positive token spend.

**Required action:** Define an effective-kind resolution rule for verdict files. Acceptable shapes include: carry `bridge_kind` into every Loyal Opposition verdict, parse the `Reviewed proposal` / `Request reviewed` reference and classify that file, or compute the kind from the latest Prime-authored `NEW` / `REVISED` version in the same document entry. Add tests for a `GO` verdict whose top file lacks `bridge_kind` but whose reviewed proposal is `candidate_spec_intake`, and for a `GO` verdict whose reviewed proposal is `implementation_proposal`.

### F2 - The actual auto-dispatch behavior remains unchanged

**Claim:** The proposed slice does not implement the behavior required by `DCL-SMART-POLLER-AUTO-TRIGGER-001` ("auto-triggers harness when work waits, never when idle").

**Evidence:** The proposal explicitly puts the auto-dispatch consumer update out of scope and states the new `dispatchable` field is ignored until a follow-on slice (`bridge/smart-poller-kind-aware-routing-2026-04-30-001.md:233-237`, `bridge/smart-poller-kind-aware-routing-2026-04-30-001.md:259`, `bridge/smart-poller-kind-aware-routing-2026-04-30-001.md:325`, `bridge/smart-poller-kind-aware-routing-2026-04-30-001.md:341-343`). The current runner dispatches every non-empty recipient list produced by `compute_actionable_pending`: `run_one_iteration` passes full `actionable_for_prime` and `actionable_for_codex` lists into `_dispatch_if_needed`, and `_dispatch_if_needed` launches whenever the list is non-empty and the signature changed (`groundtruth-kb/scripts/bridge_poller_runner.py:362-371`, `groundtruth-kb/scripts/bridge_poller_runner.py:283-296`). Current `compute_actionable_pending` is still status-only (`groundtruth-kb/src/groundtruth_kb/bridge/notify.py:141-143`).

**Risk / impact:** The owner-prioritized cost problem remains active after the slice. A `VERIFIED` report for metadata-only output would create a misleading sense that the smart poller is fixed when the scheduled dispatch path still spawns harnesses for the same pending list.

**Required action:** Either include the spawn-filtering consumer update in this same implementation bridge, or reframe this as a preparatory telemetry-only bridge that does not claim to satisfy `DCL-SMART-POLLER-AUTO-TRIGGER-001` or the owner token-cost directive. If kept as telemetry-only, add an explicit follow-on dependency gate: no `VERIFIED` closeout for the operational fix until `bridge_poller_runner.py` filters dispatch inputs on the computed dispatchable subset.

### F3 - The proposed validation command cannot show the new fields without reader changes

**Claim:** The production-state validation section requires `scripts/bridge_notify_reader.py` to display `dispatchable` and `classification`, but the proposal lists that reader as "not touched."

**Evidence:** The proposal says `python scripts/bridge_notify_reader.py` must show each pending entry's `dispatchable` and `classification` fields (`bridge/smart-poller-kind-aware-routing-2026-04-30-001.md:286-294`). It also says `scripts/bridge_notify_reader.py` is not touched because it already tolerates unknown JSON fields (`bridge/smart-poller-kind-aware-routing-2026-04-30-001.md:259-261`). The current reader's orient table only renders Document, Status, File, and INDEX line (`scripts/bridge_notify_reader.py:67-75`).

**Risk / impact:** The post-implementation evidence requested by the proposal cannot be produced by the proposed file scope. This weakens the claimed "production observation before behavior change" path.

**Required action:** Include `scripts/bridge_notify_reader.py` in scope, or change the verification command to inspect the JSON artifact directly. If the reader remains the validation surface, add tests proving it displays `dispatchable` and `classification`.

## Open Question Responses

1. **Substring grouping vs. canonicalization:** substring grouping is acceptable only after F1 is fixed. The main blocker is not substring matching; it is resolving the effective kind from the correct bridge version.
2. **`review` as terminal-on-GO:** likely correct, but add a fixture using an actual `bridge_kind: review` entry before treating it as settled.
3. **`verification` as terminal-on-GO:** likely correct for standalone verification threads; test with both `bridge_kind: verification` and any `post_implementation*` variants so implementation reports are not accidentally suppressed.
4. **Bare `proposal`:** status-only fallback is acceptable for legacy ambiguity, but the artifact should record `classification: ambiguous` and the follow-on consumer should make that fallback explicit.
5. **4 KB header read budget:** acceptable.
6. **Schema v3:** acceptable if all in-repo readers and tests are updated together; do not rely only on "unknown JSON fields are ignored" because the current reader formats a typed artifact.

## Recommended Action

Revise the proposal to:

1. Resolve bridge kind from the operative Prime proposal for `GO` / `NO-GO` verdict files, not only from the top verdict file.
2. Include the dispatch consumer filter in scope, or narrow the proposal to telemetry-only and stop claiming the operational token-cost fix lands here.
3. Bring the reader / production validation surface into file scope or verify the JSON artifact directly.
4. Add fixtures that model real bridge chains: terminal `candidate_spec_intake` `GO` verdict, dispatchable `implementation_proposal` `GO` verdict, `NO-GO` revision-needed verdict, and legacy no-kind fallback.

## Decision Needed From Owner

None. This is a bridge-review NO-GO; Prime can revise without owner input.

## Verification Performed

- Read live authoritative `bridge/INDEX.md`; selected entry latest status was `NEW`.
- Read `.claude/rules/file-bridge-protocol.md`.
- Read reviewed proposal `bridge/smart-poller-kind-aware-routing-2026-04-30-001.md`.
- Inspected current implementation surfaces:
  - `groundtruth-kb/src/groundtruth_kb/bridge/notify.py`
  - `groundtruth-kb/scripts/bridge_poller_runner.py`
  - `scripts/bridge_notify_reader.py`
  - `groundtruth-kb/tests/test_bridge_notify.py`
  - `groundtruth-kb/tests/test_bridge_poller_runner.py`
- Inspected representative current bridge chains for top verdict vs reviewed proposal metadata.

No test suite was run because this was a proposal review with no code changes to production files.
