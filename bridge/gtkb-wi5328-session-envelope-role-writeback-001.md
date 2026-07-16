NEW

# WI-5328: Session envelope never persists the owner explicit ::init gtkb (pb|lo) directive; role-authority checks silently fall back to durable dispatcher/registry role

bridge_kind: prime_proposal
Document: gtkb-wi5328-session-envelope-role-writeback
Version: 001
Author: Prime Builder (Claude Code, harness B)
Date: 2026-07-16 UTC

author_identity: prime-builder/claude
author_harness_id: B
author_session_context_id: ff93de8c-3ea2-4e9f-8549-d85cba5ff4d2
author_model: claude-sonnet-5
author_model_version: claude-sonnet-5
author_model_configuration: Claude Code interactive session; session-stated Prime Builder role via literal ::init gtkb pb opening message; explanatory output style

Work Item: WI-5328

target_paths: ["groundtruth-kb/src/groundtruth_kb/session/envelope.py", "scripts/session_self_initialization.py", ".claude/hooks/workstream-focus.py", "platform_tests/scripts/test_session_self_initialization.py"]

implementation_scope: source, test
requires_review: true
requires_verification: true
kb_mutation_in_scope: false

Recommended commit type: fix:

---

## Author Role-Provenance Disclosure (read before review)

This proposal is itself filed under the exact defect it describes. This session's `.claude/session/envelope.json` currently resolves `role_resolved: "loyal-opposition"` via `worker_role_provenance.role_resolution_source: "session_resolver_fallback"`, DESPITE this session literally opening with `::init gtkb pb`. The owner has explicitly confirmed in this session''s transcript that the session-stated directive is authoritative over dispatcher/registry configuration, and has directed proceeding with filing despite the known provenance inconsistency. Reviewers should treat `author_identity: prime-builder/claude` as OWNER-CONFIRMED-AUTHORITATIVE, and the `loyal-opposition`-tagged envelope/claim metadata as further live evidence of the defect this proposal fixes, not as a genuine role violation or self-review concern.

## Summary

`.claude/session/envelope.json` is written once at `SessionStart` -- before the owner''s `::init` directive is available to the harness -- and, for interactive Claude sessions, nothing subsequently writes the transcript-detected role back into it. Every downstream consumer that reads this envelope for role-gated decisions therefore silently falls back to the durable dispatcher/registry role instead of the actual session-stated role. This directly contradicts the owner''s standing principle (restated verbatim in this session''s transcript): "the configuration of the dispatcher is not a determinant of the role of any session-context; the role of the dispatched worker is carried in the dispatch itself and is authoritative; it can only be overridden by an explicit directive from the owner."

## Live Reproduction Evidence (this session, 2026-07-16)

Three independent observations across two distinct sessions this session-day, both opened with the literal first message `::init gtkb pb`:

1. **Foreign-session leakage (earlier session, session_id `019f69a3-...-wi5085`):** envelope contained a DIFFERENT harness''s data entirely (`harness_id: "A"`, `harness_name: "codex"`) -- not this session at all.
2. **Own-session role misresolution (this session, session_id `ff93de8c-3ea2-4e9f-8549-d85cba5ff4d2`, opened 2026-07-16T16:31:50Z with literal `::init gtkb pb`):** `harness_id`/`harness_name`/`session_id` now correctly reflect this session (the foreign-leakage symptom appears improved), but `init_keyword: null`, `role_resolved: "loyal-opposition"`, `role_resolution.interactive_role_source: "transcript_init_keyword"` (claims transcript-sourced) while `worker_role_provenance.role_resolution_source: "session_resolver_fallback"` (actually fell back) -- an internally inconsistent record.
3. **Downstream propagation:** `scripts/bridge_claim_cli.py claim <slug>` run in this same session recorded `acting_role: "loyal-opposition"` for the resulting work-intent claim, and the `GTKB-LO-FILE-SAFETY` PreToolUse hook blocked multiple Claude `Write`/`Bash` calls this session with "Loyal Opposition write ... outside the allow-list" -- both consuming the same stale/fallback role.

## Root Cause (investigated, call-site not yet pinpointed)

`groundtruth_kb/session/envelope.py` (~line 270-274) contains the correct resolution logic:

```python
durable_role = _resolve_role(project_root, harness_id)
resolved_role = role or durable_role
interactive_role_source = "transcript_init_keyword" if role else None
```

This resolves correctly **if the caller passes a non-empty `role`** derived from the owner''s init-keyword message. The defect is therefore upstream of this function: whatever code path is supposed to (a) detect `::init gtkb (pb|lo)` on the first `UserPromptSubmit` event and (b) call back into this envelope module to persist `role` either does not run for interactive Claude sessions, or runs but its result is not wired to an envelope write-back.

`scripts/session_self_initialization.py` (the `SessionStart` source) and `.claude/hooks/workstream-focus.py` (the first-registered `UserPromptSubmit` hook) are the primary candidates investigated this session; neither was confirmed (grep for `envelope` in `workstream-focus.py` returned no matches) to contain the missing write-back call. **Pinpointing the exact call site is in-scope implementation work**, not a pre-solved design in this proposal -- the proposal establishes the reproducible defect and the two-part fix shape below; Loyal Opposition and the implementer should trace the exact `UserPromptSubmit` -> envelope write-back wiring (or its absence) as the first implementation step.

## Proposed Fix (two parts)

1. **Primary: write-back on init-keyword detection.** Whichever `UserPromptSubmit`-time code path detects a valid `::init gtkb (pb|lo)` match must call an envelope write-back (new or existing function in `groundtruth_kb/session/envelope.py`) that sets `role`, `role_resolved`, `role_asserted`, `init_keyword`, and `role_resolution.interactive_role_source: "transcript_init_keyword"` to the session-stated value, and sets `worker_role_provenance.role_resolution_source` to a value that truthfully reflects the transcript source (not `"session_resolver_fallback"`) for the CURRENT session id.
2. **Secondary: fail-loud on inconsistency.** Add a lightweight consistency assertion (session-start or doctor-check level) that flags an envelope where `role_resolution.interactive_role_source == "transcript_init_keyword"` but `worker_role_provenance.role_resolution_source == "session_resolver_fallback"` for the same `session_id` -- the internally-contradictory state observed in this session -- so a recurrence is caught mechanically rather than requiring manual reproduction.

## Specification Links

- `GOV-SESSION-ROLE-AUTHORITY-001`
- `DCL-SESSION-ROLE-RESOLUTION-001`
- `ADR-INTERACTIVE-SESSION-ROLE-OVERRIDE-001`
- `ADR-ROLE-AUTHORITY-INTERACTIVE-PERSISTENCE-001`
- `DCL-INTERACTIVE-SESSION-ROLE-PERSISTENCE-001`
- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`

## Prior Deliberations

- `bridge/gtkb-session-envelope-durability-001-007.md` (WITHDRAWN) -- a related, withdrawn-as-stale prior proposal on session-envelope durability; distinct scope (DCL durability), not this defect.
- `bridge/gtkb-wi5252-session-envelope-cli-provenance-006.md` (VERIFIED) -- related, resolved CLI-provenance scope; does not cover the UserPromptSubmit init-keyword write-back gap.
- `bridge/gtkb-wi5314-nonspawn-session-envelope-suppression-004.md` (GO, not yet VERIFIED at time of this filing) -- adjacent, in-flight session-envelope work; this proposal is a distinct defect (role write-back, not nonspawn suppression) and should be sequenced/coordinated with WI-5314 by Loyal Opposition and the implementer, not duplicated.
- Owner directive, this session''s transcript, verbatim: "the configuration of the dispatcher is not a determinant of the role of any session-context; the role of the dispatched worker is carried in the dispatch itself and is authoritative; it can only be overridden by an explicit directive from the owner."


### Helper-suggested candidates

_No prior deliberations: <fill in reason before filing>._

## Requirement Sufficiency

Existing requirements sufficient. `GOV-SESSION-ROLE-AUTHORITY-001` and `DCL-SESSION-ROLE-RESOLUTION-001` already establish that the session-stated role must take precedence; this proposal is a defect fix to the envelope-persistence mechanics that should already implement that requirement.

## Owner Decisions / Input

- Owner explicitly routed the sibling WI-5320 implementation to Codex earlier this session specifically because this defect blocked a Claude Prime Builder attempt to implement it -- direct owner-observed impact evidence.
- Owner explicitly restated (verbatim, quoted above) the governing principle this defect violates.
- Owner explicitly directed, via AskUserQuestion in this session''s transcript, "resume filing anyway, flag the role mismatch in the proposals," after being shown that this session''s write-probe succeeded despite the envelope still showing the wrong role -- the resulting Author Role-Provenance Disclosure section above is that flag.

## Safety Note for Implementation (not a review gate; carried forward for the implementer)

Per this session''s prior AskUserQuestion exchange, autonomous unattended implementation of this specific work item by a Claude session should pause for fresh explicit owner confirmation once a `GO` is live, given the self-referential risk (this fix touches the very mechanism that determines whether a session''s role-gated actions -- including implementing this very fix -- are trustworthy).

## Risk / Rollback

- **Blast radius:** session envelope construction/update logic plus the UserPromptSubmit init-keyword handling path; no KB mutation, no bridge-protocol status semantics change.
- **Risk:** moderate -- touches role-resolution machinery that gates a wide range of downstream actions (work-intent claims, `resolve_changed_by`, LO-file-safety, handoff-prompt generation). Requires careful, incremental testing (see target test file) rather than a single sweeping change.
- **Rollback:** revert the write-back call site; the durable-registry-fallback behavior (current state) is the safe rollback target, not a broken state -- it is merely over-conservative, not unsafe.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.