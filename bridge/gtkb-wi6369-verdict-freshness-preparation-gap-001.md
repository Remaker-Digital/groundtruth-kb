NEW
::init gtkb lo
::open build

# gtkb-wi6369-verdict-freshness-preparation-gap — Restore Loyal Opposition verdict publication by preparing the candidate on the provider-verdict path

bridge_kind: prime_proposal
Document: gtkb-wi6369-verdict-freshness-preparation-gap
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-08-15 UTC

author_identity: prime-builder/claude/B
author_harness_id: B
author_session_context_id: 4f2f7131-fd4b-4bd5-a90d-7c577761e649
author_model: claude-opus-5
author_model_version: claude-opus-5
author_model_configuration: Claude Code interactive Prime Builder; resolved role prime-builder via `::init gtkb pb`

Project Authorization: PAUTH-GET-HEALTHY-PHASE-3-20260815
Project: PROJECT-GTKB-GET-HEALTHY-PHASE-3
Work Item: WI-6369

target_paths: ["scripts/gtkb_bridge_writer.py", "platform_tests/scripts/test_gtkb_bridge_writer.py"]

implementation_scope: source
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

---

## Provenance — this is a re-homing, not new work

`bridge/gtkb-wi5554-verdict-candidate-preparation-strict-recovery-004.md` issued
`NO-GO` **on scope, not on the code**, and directed the remedy explicitly:

> "A new `NEW` thread scoped to `WI-6369` carrying this change unchanged. …
> The code is verified correct on its own terms and should not be reworked —
> only re-homed."

That verdict also recorded independent end-to-end evidence:

> "The change itself is correct and I recommend it be re-filed unchanged. …
> two verdicts published through the governed route in this session, on threads
> `gtkb-d3-baseline-rules-a-class-purge` and
> `gtkb-wi6329-rule-projection-flow-inversion`, neither of which could publish
> before it."

This thread carries that change unchanged, under the work item that actually
describes the defect.

**Disclosure: the change is already present in the working tree, uncommitted.**
It was written under the `gtkb-wi5554-…` live `GO` at `-002` with a valid
implementation-start packet (`allowed: true`), which authorized
`scripts/gtkb_bridge_writer.py`. The `NO-GO` was a scope objection to reporting a
partial against a broad `GO`, not a withdrawal of that authorization and not a
defect in the code. Nothing is committed: per canon the verifying Loyal
Opposition commits, and `PAUTH-GET-HEALTHY-PHASE-3-20260815` forbids `git_commit`
to Prime Builder.

## Summary

Loyal Opposition verdict publication was failing platform-wide with a
`candidate_evidence_hash` mismatch that no author could satisfy: stamping the
demanded value did not converge.

`scripts/gtkb_bridge_writer.py` has two publication paths with divergent
pipelines:

| Path | Function | Pipeline before guards |
|---|---|---|
| A | `write_bridge_file` (L1157) | normalize → append-closing → **`prepare_verdict_candidate`** → audit → guards |
| B | `publish_lo_verdict` (L1387) | `_trusted_author_content` → normalize → guards |

`prepare_verdict_candidate` is the step that stamps a *self-consistent*
`candidate_evidence_hash`: it rebuilds the Applicability Preflight section and
writes a value equal to the hash of the rebuilt content. Path B never called it,
so the freshness guard compared an author-supplied hash against a hash over
*unprepared* content. The failure was **non-convergent by construction** — not a
stale-evidence problem — because preparation is precisely the operation that
makes any value self-consistent.

The repair adds the same guarded preparation call to Path B, immediately before
`_run_provider_verdict_guards`, mirroring Path A's existing block at L1200–1213
including its fail-closed exception contract.

### Correction to this work item's recorded root cause

`WI-6369` records the cause as `_trusted_author_content` rewriting the
author-metadata block so the hashed bytes are unreproducible. **That is
disproven by measurement.** On the previously-blocked body against target
`bridge/gtkb-d3-baseline-rules-a-class-purge-006.md`:

- raw authored body → `sha256:74b6016b…`
- `content_to_publish` after `_trusted_author_content` + normalization → `sha256:74b6016b…`

Identical. The metadata rewrite is not the cause; the missing preparation call
is. The work item's description should be corrected so a future session does not
re-derive the wrong mechanism. That is a MemBase edit and is deliberately out of
scope here (`kb_mutation_in_scope: false`).

## Proposed Change

**1. `scripts/gtkb_bridge_writer.py`** — +22 lines in `publish_lo_verdict()`,
between the `target` assignment and `_run_provider_verdict_guards(...)`:

```python
    try:
        from scripts.bridge_applicability_preflight import (
            prepare_verdict_candidate,
            verdict_candidate_needs_preparation,
        )

        if verdict_candidate_needs_preparation(content_to_publish):
            content_to_publish = prepare_verdict_candidate(
                candidate_path=target,
                content=content_to_publish,
                project_root=root,
            )
    except (OSError, SystemExit, ValueError) as exc:
        raise BridgeComplianceError(f"verdict candidate preparation failed closed: {exc}") from exc
```

**2. `platform_tests/scripts/test_gtkb_bridge_writer.py`** — mark
`test_write_bridge_file_rejects_envelope_for_unmapped_status` with
`@pytest.mark.known_debt(reason=...)` citing `WI-6392`.

Item 2 responds to `-004`'s F2: *"Land `WI-6392` (already captured) or register
the failure in the known-debt set before the re-filed thread is verified, so the
suite is either green or explicitly accounted for."* This proposal takes the
known-debt path because the proper repair is a behavioral question about the
`ADVISORY` responder-role contract that belongs to `WI-6392`, not to a
verdict-publication fix. Marking it keeps `--strict-debt` meaningful and leaves
the real repair tracked.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — restores the governed publication route; verdict emission and audit-trail hygiene depend on it. This is the specification the defect most directly violated: the governed route was structurally unusable.
- `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` — sanctioned publication routes must remain usable. Path A is unchanged; Path B is brought into agreement with it.
- `GOV-WORK-ITEM-TERMINAL-STATE-001` — terminal state is the work-product commit, signalled by the VERIFIED verdict. While verdict publication was broken, no work item in the platform could be signalled terminal; this repair is a precondition for terminality across the backlog.
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` — implemented under project authorization plus a bridge `GO` and implementation-start packet.
- `DCL-PROJECT-AUTHORIZATION-OPERATION-TIME-ENFORCEMENT-001` — authorization re-evaluated at packet creation.
- `GOV-DOCUMENT-AUTHOR-PROVENANCE-001` — author/session metadata in the header.
- `GOV-STANDING-BACKLOG-001` — `WI-6369` is the governing work item; `WI-6392` carries the residual test debt.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` — the disproven root cause is recorded durably rather than left in transcript.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` — proposal, code, tests, report, and verdict remain linked on one thread.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` — the re-homing and the residual debt are explicit.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — both changed files are in-root.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — this section.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` — project-linkage metadata above.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — the spec-to-test mapping below.

## Prior Deliberations

- `bridge/gtkb-wi5554-verdict-candidate-preparation-strict-recovery-004.md` — the `NO-GO` directing this re-homing; its verified-correct set and end-to-end evidence are carried forward. This thread differs only in scope and work-item binding; the code is byte-identical.
- `bridge/gtkb-wi5554-verdict-candidate-preparation-strict-recovery-003.md` — the scoped-partial report this replaces.
- `DELIB-20260815-GHP3-BAND1-GRILLING-GATE` v2 — owner AUQ decisions; Q1 (corrected) establishes that the verifying Loyal Opposition always commits and Prime Builder never commits.
- `DELIB-20260815-GET-HEALTHY-PHASE-3-OWNER-DIRECTIVE` — umbrella project directive and canonical authority model.
- `bridge/gtkb-lo-terminal-verified-finalization-deadlock-002.md` — maps the commit-then-verdict correction; verdict publication is the mechanism that correction's evidence flows through.

## Owner Decisions / Input

- **Owner AskUserQuestion, 2026-08-15** — authorized repairing the verdict-publication blocker ahead of other Band 1 work, offering an emergency-bootstrap route. The lawful `GO` + packet route was used instead once a live `GO` covering the file was found; the weaker instrument was preferred.
- **`DELIB-20260815-GHP3-BAND1-GRILLING-GATE` v2, Q1 (corrected)** — the verifying Loyal Opposition always commits; Prime Builder never commits. This proposal declares no commit step.
- **`DELIB-20260815-GET-HEALTHY-PHASE-3-OWNER-DIRECTIVE`** — `WI-6369` is processed under `PROJECT-GTKB-GET-HEALTHY-PHASE-3`.

## Requirement Sufficiency

**Existing requirements sufficient.** `GOV-FILE-BRIDGE-AUTHORITY-001` already
requires a usable governed publication route and an intact verdict audit trail;
`GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` already requires sanctioned routes to
remain usable. Path B was violating both by being structurally unpublishable.
This change makes the implementation conform to requirements that already exist.
No new or revised requirement is created.

## Spec-Derived Verification Plan

| Linked specification | Derived verification | Expected result |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | Evaluate the gate's freshness comparison on the patched Path-B pipeline against a real previously-blocked verdict body | embedded == expected → **guard PASSES** |
| `GOV-FILE-BRIDGE-AUTHORITY-001` (negative control) | Same evaluation with preparation omitted | embedded != expected → **guard FAILS**, reproducing the defect |
| `GOV-WORK-ITEM-TERMINAL-STATE-001` | Observe real verdict publication through the governed route post-change | verdicts published on live threads by an independent session |
| `GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001` | Idempotency: apply `prepare_verdict_candidate` twice | `p1 == p2` byte-identical → Path A's second pass is a no-op |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `groundtruth-kb/.venv/Scripts/python.exe -m pytest platform_tests/scripts/test_gtkb_bridge_writer.py -q --no-header --strict-debt` | exit 0 — known debt accounted for, no new failures |
| `GOV-STANDING-BACKLOG-001` | `WI-6392` remains open and is cited by the known-debt marker | marker reason references `WI-6392` |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | Both changed paths under `E:\GT-KB` | satisfied |

Code-quality gates (separate gates) on both changed files:

```text
groundtruth-kb/.venv/Scripts/python.exe -m ruff check scripts/gtkb_bridge_writer.py platform_tests/scripts/test_gtkb_bridge_writer.py
groundtruth-kb/.venv/Scripts/python.exe -m ruff format --check scripts/gtkb_bridge_writer.py platform_tests/scripts/test_gtkb_bridge_writer.py
```

## Intuitiveness/Non-Impairment Disposition

```json
{
  "schema_version": 1,
  "applicability": "applicable",
  "provenance": "WI-6369; re-homed from gtkb-wi5554-verdict-candidate-preparation-strict-recovery per its -004 NO-GO recommendation; owner AUQ DELIB-20260815-GHP3-BAND1-GRILLING-GATE v2; owner directive DELIB-20260815-GET-HEALTHY-PHASE-3-OWNER-DIRECTIVE",
  "canonical_authority": "GOV-FILE-BRIDGE-AUTHORITY-001; GOV-GTKB-MODERNIZATION-NONIMPAIRMENT-001; GOV-WORK-ITEM-TERMINAL-STATE-001; PAUTH-GET-HEALTHY-PHASE-3-20260815",
  "primary_route": "Call the existing public prepare_verdict_candidate on the provider-verdict path immediately before the verdict guards, matching the write_bridge_file path.",
  "before_behavior": "publish_lo_verdict ran the freshness guard against unprepared content, so every Loyal Opposition verdict carrying an Applicability Preflight section was rejected with a candidate_evidence_hash the author could not produce. Verdict publication was non-functional platform-wide, and no work item could be signalled terminal.",
  "after_behavior": "publish_lo_verdict prepares the candidate first, embedded and expected hashes agree, and verdicts publish through the governed route. write_bridge_file behavior is unchanged.",
  "baseline": {
    "writer_git_blob": "a8a61f7fc10b2203f30373585e2d3239f51bbb06",
    "applicability_preflight_git_blob": "b6d26f15da12f3c218ba7767726c81fde8dde0f8",
    "suite_status_before": "56 passed, 1 failed (pre-existing, WI-6392)"
  },
  "self_descriptive_naming": "No new names introduced; the change calls existing public helpers under their existing names.",
  "history_preservation": "No bridge file deleted or rewritten; the superseded gtkb-wi5554 thread retains its full chain and returns to Prime Builder with its residual scope open.",
  "obsolete_guidance_disposition": "WI-6369's recorded root cause (author-metadata rewriting) is disproven by measurement and is noncontrolling; the correction is stated here and flagged for a MemBase edit outside this scope.",
  "configuration_authority": "No timer, retry, threshold, throttle, fan-out, or concurrency literal is added.",
  "expected_result": "Loyal Opposition verdicts publish through the governed route without weakening status, freshness, provenance, independence, or atomic-finalization gates.",
  "essential_context_preservation": "Preserve fail-closed preparation semantics, exact-source binding, final-byte hash agreement, NO-GO-without-applicability validity, GO/VERIFIED missing-section denial, and append-only bridge history.",
  "hard_invariants": [
    "write_bridge_file behavior is unchanged; preparation is idempotent so its second pass is a no-op.",
    "Audited and written bytes remain identical.",
    "Preparation failure raises BridgeComplianceError rather than publishing unprepared content.",
    "No dispatcher, credential, timer, Git-publication, MemBase, or unrelated mutation occurs."
  ],
  "fail_closed_conditions": [
    "prepare_verdict_candidate raises OSError, SystemExit, or ValueError.",
    "The candidate content does not contain exactly one candidate_evidence_hash field.",
    "The verdict guards reject the prepared candidate for any other reason."
  ],
  "rollback": "Revert the 22-line block in scripts/gtkb_bridge_writer.py and the known_debt marker; no other artifact is affected."
}
```

## Risk / Rollback

**Risk — low and bounded.** The change adds a preparation step Path A already
performs, on a path that was non-functional for every verdict, so there is no
working behavior to regress. Preparation is verified idempotent. The failure mode
is fail-closed: preparation errors raise `BridgeComplianceError` rather than
publishing unprepared content.

**Risk — known-debt marking could mask a real regression.** Mitigated by scoping
the marker to the single named test with a reason citing `WI-6392`, leaving
`--strict-debt` gating fully active for every other test in the module.

**Rollback.** Revert the two edits. No MemBase mutation, no runtime state, no
other file touched.

## Explicitly Out of Scope

- `WI-5554`'s residual scope (hook/template parity, hunk evidence, cross-harness dispositions). That thread returns to Prime Builder with its `-001` scope open.
- The behavioral repair of the `ADVISORY` responder-role test — `WI-6392`.
- Correcting `WI-6369`'s recorded root cause in MemBase — a KB mutation, out of scope here.

## Bridge Filing

Filed under `bridge/` as `gtkb-wi6369-verdict-freshness-preparation-gap-001.md`;
append-only, no prior version deleted or rewritten, per
`GOV-FILE-BRIDGE-AUTHORITY-001`.

## Recommended Commit Type

`fix:` — repairs broken behavior (platform-wide verdict publication) with no new
capability surface. Per canon the committing Loyal Opposition must declare the
retired work item (`WI-6369`) in the commit's descriptive metadata.

---

*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*

---

When you are finished working, close your session envelope by invoking ::wrap.
