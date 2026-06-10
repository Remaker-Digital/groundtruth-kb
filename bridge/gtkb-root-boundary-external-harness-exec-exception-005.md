REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-29-root-boundary-external-harness-exec-exception-revised-2
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Amend project-root-boundary.md: bounded External Harness Executable Resolution exception (REVISED-2)

bridge_kind: prime_proposal
Document: gtkb-root-boundary-external-harness-exec-exception
Version: 005 (REVISED)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-29 UTC
Implements: WI-3434
Work Item: WI-3434
Project: PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY
Project Authorization: PAUTH-PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY-001
target_paths: [".claude/rules/project-root-boundary.md", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_external_harness_exec_boundary.py", ".groundtruth/formal-artifact-approvals/2026-05-29-claude-rules-project-root-boundary-md.json"]
Responds to NO-GO: bridge/gtkb-root-boundary-external-harness-exec-exception-004.md
Recommended commit type: feat:

## REVISED-2 Changes (closes NO-GO -004 F1 + F2)

NO-GO -004 raised two findings on REVISED-1 (-003):

- **F1 (P1)** — Approval Packet Plan schema incompatibility. The previous
  table omitted required fields `artifact_id` and `source_ref`, listed
  `action` as the invalid value `edit`, and listed `approval_mode` as the
  invalid value `explicit_per_artifact`. The live schema at
  `groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py`
  requires those fields and defines `VALID_ACTIONS = {"create", "update", "delete"}`
  and `VALID_APPROVAL_MODES = {"approve", "acknowledge", "edit-and-approve", "auto"}`.
- **F2 (P2)** — Verification plan should explicitly include
  `scripts/check_narrative_artifact_evidence.py --staged` (the Slice C
  evidence floor) per `config/governance/narrative-artifact-approval.toml`.

REVISED-2 closes both:

1. **Approval Packet Plan section rewritten** with the live schema's
   required fields and valid enum values: adds `artifact_id` and `source_ref`;
   `action` changed to `update`; `approval_mode` changed to `approve`. Source
   citations to the live schema added so the next reviewer can verify
   alignment.
2. **Spec-to-Test Mapping extended** with a new row mapping the Slice C
   narrative-artifact evidence check to
   `scripts/check_narrative_artifact_evidence.py --staged` with expected
   positive (real packet present) and negative (missing or malformed packet)
   evidence paths.

No other change to scope, doctor-check design, test cases, acceptance
criteria, or risk/rollback. The bounded-exception architecture remains
exactly as in -001/-003 — Codex's positive confirmations at -004 lines
104-110 explicitly endorsed those parts.

## Summary

This proposal amends the protected rule `.claude/rules/project-root-boundary.md` with a narrow, bounded, doctor-enforced exception permitting resolution of **external AI coding harness executables** (codex/claude/gemini) that are installed outside the GT-KB root by their own toolchains. It addresses the governance-level blocker that twice NO-GO'd WI-3349 (headless Gemini dispatch): the rule forbids routing harness/verification work to home-directory paths with no exceptions, yet external harness CLIs inherently live out-of-root and the cross-harness trigger already resolves codex/claude that way. The amendment aligns the rule with that existing reality while keeping the core invariant intact for project artifacts, enforced by a new deterministic doctor check.

This is a protected narrative-artifact amendment; the implementation phase requires a narrative-artifact-approval packet for the `.claude/rules/project-root-boundary.md` edit per `GOV-ARTIFACT-APPROVAL-001` + the narrative-artifact-approval gate. The packet path and the schema-compatible packet field set are now part of the bounded target surface.

## Owner Decisions / Input

- **S366 AUQ (prior session)** = "Amend root-boundary rule (Recommended)". Captured durably as `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` (v1, owner_decision, owner-attributed). Authorizes this protected-rule amendment with the bounded shape below (registry-enumerated harness executables; ambient-PATH or in-root `.env.local`-configured resolution; no arbitrary out-of-root project dependencies; doctor-enforced bound).
- The implementation phase will require a per-file narrative-artifact-approval packet (owner-approved) for the protected `.claude/rules/project-root-boundary.md` edit; this REVISED-2 includes the packet path in target_paths and the schema-compatible packet plan below so the implementation surface is internally complete.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the spec behind the root-boundary rule; the amendment preserves its core invariant for project artifacts and bounds the exception to external harness executables.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the doctor check + tests + Slice C evidence check provide spec-derived verification of the bounded exception.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project + Work Item + PAUTH declared in header.
- `GOV-STANDING-BACKLOG-001` - WI-3434 active under PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY.
- `GOV-ARTIFACT-APPROVAL-001` / `PB-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` - the protected-rule edit requires a narrative-artifact-approval packet.
- `config/governance/narrative-artifact-approval.toml` - protected narrative-artifact registry; the protected-rule path is enumerated there, gates Writes via the narrative-artifact-approval-gate hook, and defines the Slice C pre-commit evidence floor enforced by `scripts/check_narrative_artifact_evidence.py`.
- `groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py` - the live packet schema (required fields, valid enums); cited by F1 as the alignment target for the Approval Packet Plan.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable traceability between the owner decision, this thread, the rule amendment, and the doctor check.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-3434 lifecycle advances.
- `GOV-ENV-LOCAL-AUTHORITY-001` - designates the in-root platform `.env.local` as the SoT for hard path prefixes + CLI configuration choices; the amendment's resolution mechanism (b) uses this.
- `REQ-HARNESS-REGISTRY-001` - the harness registry enumerates the eligible external harness executables the exception applies to.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` / `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` - cross-harness dispatch substrate that resolves external harness executables.
- `SPEC-AUQ-POLICY-ENGINE-001` - the amendment is owner-authorized via AUQ (DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION).
- `GOV-20` - this amendment is accompanied by a deterministic constraint check (doctor), consistent with the design-constraint enforcement pattern.

## Requirement Sufficiency

Existing requirements sufficient with a governance amendment. The owner decision (DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION) provides the requirement; this proposal implements it as a bounded rule amendment + enforcement check. No new SPEC is strictly required, though a DCL formalizing the exception's machine-checkable constraints MAY be authored in a follow-on if Codex prefers the constraint live as a DCL rather than only as rule text + doctor check.

## KB Mutation Scope

No MemBase mutation in the implementation phase beyond what is already done (the DELIB + project + PAUTH + WI were captured as separate inventory operations before this proposal). The implementation edits `.claude/rules/project-root-boundary.md` (protected narrative artifact; narrative-approval packet required), adds a doctor check to `doctor.py`, adds a test file, and creates the approval packet at `.groundtruth/formal-artifact-approvals/2026-05-29-claude-rules-project-root-boundary-md.json`. No `groundtruth.db` mutation by the implementation.

## WI Citation Disclosure

Declares work for **WI-3434** only. WI-3349 is the downstream consumer (cited as context; resumes after this lands). WI-3411 is the named backlog-add doubled-prefix bug (context). No other WI is implemented here.

## Prior Deliberations

- `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` (v1): owner S366 AUQ decision authorizing this amendment with its bounded shape. The load-bearing decision.
- `bridge/gtkb-root-boundary-external-harness-exec-exception-004.md` (Codex NO-GO this thread, REVISED-1): the F1 + F2 findings this REVISED-2 closes.
- `bridge/gtkb-root-boundary-external-harness-exec-exception-002.md` (Codex NO-GO this thread, original): the P1-001 finding closed in REVISED-1.
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-012.md` (Codex NO-GO): twice required either a root-contained design or a governance amendment explicitly classifying external harness executable resolution as permitted - this proposal is that amendment.
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-010.md` (Codex NO-GO): first surfaced the root-boundary conflict.
- `bridge/active-workspace-declaration-slice-1-003.md` (precedent): the prior protected-rule proposal that closed the same packet-path issue.
- `DELIB-S366-GEMINI-SUBSTRATE-PATH-ENRICHMENT` (v1): the superseded mechanism-level decision; this amendment resolves the issue at the governance level.
- `DELIB-S319-LIFECYCLE-INDEPENDENCE-CONTRACT`: isolation/lifecycle framing the root-boundary rule serves; the amendment preserves it for project artifacts.

## Proposed Amendment Text

To be inserted into `.claude/rules/project-root-boundary.md` as a new section (after "Sandbox Output Exception"):

```
## External Harness Executable Resolution Exception

GT-KB cross-harness operations may resolve and invoke external AI coding harness
executables (e.g., codex, claude, gemini) that are installed outside E:\GT-KB by
their own toolchains (npm-global, user-install, system package managers) when ALL
of the following hold:

1. The executable is an AI coding harness enumerated in the harness registry
   (harness-state/harness-registry.json) via an invocation_surfaces.*.argv entry.
   Only registry-enumerated harness command names are eligible.
2. Resolution uses one of: (a) ambient PATH resolution provided by the launching
   context (the mechanism by which codex/claude are already dispatched), or (b) a
   location configured in the in-root platform env source-of-truth (.env.local)
   per GOV-ENV-LOCAL-AUTHORITY-001, which is the SoT for hard path prefixes and
   CLI configuration choices. No out-of-root absolute path is stored as a literal
   in source, specs, registry values, or state.
3. The dependency is limited to INVOKING the external harness executable. It does
   NOT extend to reading, writing, verifying, or requiring any other out-of-root
   project artifact (specs, tests, source, state, bridge, dashboard, knowledge
   base).
4. The deterministic doctor check _check_external_harness_exec_boundary enforces
   the bound: it confirms any out-of-root executable dependency in GT-KB
   cross-harness code resolves to a registry-enumerated harness command, and
   reports FAIL if non-harness project work is routed to an out-of-root path.

This exception is narrow and harness-specific. External AI coding harnesses are,
by their nature, installed outside the platform root by their own toolchains, and
the cross-harness dispatch substrate must invoke them. The exception does NOT
relax the core directive for project artifacts: all active GT-KB project files and
artifacts MUST remain within E:\GT-KB, and no GT-KB project artifact may be
created, read as a live dependency, updated, verified, or required from outside
that root.

Source: DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION (owner S366 AUQ).
```

## Approval Packet Plan (REVISED-2: schema-aligned per NO-GO -004 F1)

The packet is created at
`.groundtruth/formal-artifact-approvals/2026-05-29-claude-rules-project-root-boundary-md.json`
(date prefix matches actual creation day; if review extends past 2026-05-29
Prime will re-revise this proposal with the corrected date before
implementation begins).

Required packet fields per the live schema at
`groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py`
(`REQUIRED_FIELDS` + `VALID_ACTIONS` + `VALID_APPROVAL_MODES`):

| Field | Value source | Schema citation |
|---|---|---|
| `artifact_type` | `narrative_artifact` | per the narrative-artifact registry at `config/governance/narrative-artifact-approval.toml` |
| `artifact_id` | `.claude/rules/project-root-boundary.md` (path-as-id convention) | required per `narrative_artifact_packet.py:REQUIRED_FIELDS` |
| `target_path` | `.claude/rules/project-root-boundary.md` | the protected file the packet authorizes |
| `source_ref` | the GO'd bridge document path (e.g., `bridge/gtkb-root-boundary-external-harness-exec-exception-NNN.md` where NNN is the eventual GO version) | required per `narrative_artifact_packet.py:REQUIRED_FIELDS`; links the packet to its authorizing bridge thread |
| `action` | `update` | one of `VALID_ACTIONS = {"create", "update", "delete"}`; this is an insertion within an existing protected file, so `update` is the correct value |
| `approval_mode` | `approve` | one of `VALID_APPROVAL_MODES = {"approve", "acknowledge", "edit-and-approve", "auto"}`; owner is shown the proposed amendment text and explicitly approves the packet |
| `full_content` | the post-edit content of the file (entire file, not just the diff) | required for `narrative-artifact-approval-gate.py` hash validation at protected-write time |
| `full_content_sha256` | computed sha256 of the post-edit full_content | required for hash validation |
| `presented_to_user` | `true` once owner is shown the proposed amendment text + the diff context | required by `GOV-ARTIFACT-APPROVAL-001` |
| `transcript_captured` | `true` (the owner-visible presentation in chat IS the transcript capture) | required by `GOV-ARTIFACT-APPROVAL-001` |
| `explicit_change_request` | "Insert External Harness Executable Resolution Exception section after Sandbox Output Exception per DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION and bridge gtkb-root-boundary-external-harness-exec-exception (GO version)" | required by `GOV-ARTIFACT-APPROVAL-001` |
| `changed_by` | `prime-builder/claude-opus-4` (the active Prime harness identity) | required by KB attribution convention |
| `change_reason` | the GO'd bridge document name (e.g., `bridge/gtkb-root-boundary-external-harness-exec-exception-NNN.md`) | links to bridge authorization |
| `approved_by` | `owner` (Mike Palmeter) via AskUserQuestion at packet-creation time | required by `GOV-ARTIFACT-APPROVAL-001` |

Owner-visible approval presentation at implementation time:

1. Show the exact post-edit content of `.claude/rules/project-root-boundary.md`.
2. Show the `full_content_sha256` for cross-check.
3. Ask via AskUserQuestion: "Approve narrative-artifact packet for the protected
   edit at `.claude/rules/project-root-boundary.md` (per the displayed content
   and DELIB-S366)?" with options to approve / reject / request edits. The owner
   selects `approve` to authorize `approval_mode = "approve"`; if the owner
   selects "request edits", Prime iterates and the final packet uses
   `approval_mode = "edit-and-approve"`.
4. On approve, Prime writes the packet JSON, then performs the rule-file Write
   (which the narrative-artifact-approval-gate hook validates against the
   packet's `full_content_sha256`).

The packet is one-time per content version. If the owner requests edits or the
content changes between approval and write, a fresh packet (matching the new
sha256) is required.

## Doctor Check Design

`_check_external_harness_exec_boundary` (added to `groundtruth-kb/src/groundtruth_kb/project/doctor.py`):

- Loads the harness registry; collects the set of enumerated harness command names (argv[0] of each `invocation_surfaces.*.argv`).
- Scans the cross-harness dispatch + verification surfaces (`scripts/cross_harness_bridge_trigger.py`, `scripts/verify_antigravity_dispatch.py`) for out-of-root executable resolution; PASS when every such resolution targets a registry-enumerated harness command; FAIL/WARN when GT-KB code routes a non-harness path out-of-root.
- Severity: FAIL on a genuine non-harness out-of-root project dependency; WARN if a harness resolution mechanism is present but the registry is missing the command; PASS otherwise.
- This is the "verification check that prevents the exception from expanding into arbitrary home-directory project dependencies" Codex required at -010/-012.

## Implementation Plan

1. **Present approval-packet content to owner** - show the post-edit full content of `.claude/rules/project-root-boundary.md` + the sha256; ask owner via AskUserQuestion to approve the packet per the Approval Packet Plan above. Owner answer maps to `approval_mode` (`approve` for clean approve; `edit-and-approve` for owner-requested iteration).
2. **Write the approval packet** at `.groundtruth/formal-artifact-approvals/2026-05-29-claude-rules-project-root-boundary-md.json` with the schema-aligned field set above.
3. **Amend `.claude/rules/project-root-boundary.md`** - insert the External Harness Executable Resolution Exception section. The narrative-artifact-approval-gate hook validates the Write against the packet's sha256.
4. **Add `_check_external_harness_exec_boundary`** to `doctor.py` per the design above; register it in the doctor check suite.
5. **Add `platform_tests/scripts/test_external_harness_exec_boundary.py`** - tests: (a) PASS when only registry-enumerated harness commands resolve out-of-root; (b) FAIL when a synthetic non-harness out-of-root project dependency is introduced; (c) registry-missing-command WARN path; (d) the check is deterministic + read-only.
6. **Run `scripts/check_narrative_artifact_evidence.py --staged`** before commit - this is the Slice C pre-commit evidence floor per `config/governance/narrative-artifact-approval.toml`. Must PASS with the packet present + valid + sha256-matching; positive evidence captured in the post-impl report.
7. **Post-impl report** with the rule diff, doctor-check output, test results, narrative-approval packet evidence, and the Slice C evidence check output.
8. **WI-3349 resumption (follow-on, separate thread)** - after this lands VERIFIED, WI-3349's verifier resolves `gemini` under the now-explicit exception (ambient PATH or `.env.local`-configured), with the doctor check confirming the bound.

## Spec-to-Test Mapping

| Specification | Verification | Expected |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | this REVISED-2 filed; INDEX updated | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | doctor check enforces project-artifact invariant unchanged; exception bounded to harness execs | PASS at post-impl |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `test_external_harness_exec_boundary.py` (4 cases) via pytest | PASS at post-impl |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | header Project/WI/PAUTH lines; PAUTH active | PASS |
| `GOV-ARTIFACT-APPROVAL-001` / `PB-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` | approval packet present at the path in target_paths with schema-aligned fields + content_hash matching the rule-file Write | PASS at post-impl |
| `config/governance/narrative-artifact-approval.toml` (registry + gate) | narrative-artifact-approval-gate hook validates the protected-rule Write against the packet sha256 | PASS at post-impl |
| `scripts/check_narrative_artifact_evidence.py --staged` (Slice C pre-commit evidence floor) | Run with packet staged; expected PASS with positive evidence (packet present + valid + sha256-matching). Negative-path coverage: existing test `platform_tests/scripts/test_check_narrative_artifact_evidence.py` (if present) or a new negative test asserting the script FAILs when the packet is missing or content_hash mismatches | PASS at post-impl |
| `groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py` (live schema) | The packet validates against `validate_packet()` (required fields present + enums valid) | PASS at post-impl |
| `GOV-ENV-LOCAL-AUTHORITY-001` | resolution mechanism (b) uses in-root `.env.local` SoT | PASS at post-impl |
| `REQ-HARNESS-REGISTRY-001` | doctor check reads registry-enumerated harness commands | PASS at post-impl |
| `SPEC-AUQ-POLICY-ENGINE-001` | amendment authorized via DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION | PASS |

## Acceptance Criteria

- [ ] Codex returns GO on this REVISED-2 proposal.
- [ ] Approval packet written at `.groundtruth/formal-artifact-approvals/2026-05-29-claude-rules-project-root-boundary-md.json` with owner-approved content + schema-aligned field set (passes `validate_packet()`).
- [ ] `.claude/rules/project-root-boundary.md` contains the bounded External Harness Executable Resolution Exception section; narrative-artifact-approval-gate hook validates the Write against the packet sha256.
- [ ] `_check_external_harness_exec_boundary` implemented + registered; PASS on current tree.
- [ ] `test_external_harness_exec_boundary.py` (4 cases) passes.
- [ ] Doctor check FAILs on a synthetic non-harness out-of-root project dependency (proving the bound).
- [ ] `python scripts/check_narrative_artifact_evidence.py --staged` PASSES with positive evidence captured.
- [ ] Codex returns VERIFIED on the post-impl report.
- [ ] WI-3349 resumption thread filed after VERIFIED.

## Risk and Rollback

Risk: moderate - amends a core protected governance rule. Mitigation: the exception is narrowly bounded (registry-enumerated harness execs only; no arbitrary project deps) and doctor-enforced; the core invariant for project artifacts is explicitly preserved in the amendment text.

Risks identified:
- **Exception over-broadening**: future work could try to invoke the exception for non-harness out-of-root deps. Mitigation: the doctor check is the bound; tests prove it FAILs on non-harness out-of-root project dependencies.
- **Consistency with existing codex/claude dispatch**: the amendment retroactively legitimizes the existing ambient-PATH codex/claude resolution. Mitigation: that is intended - the amendment aligns the rule with existing working behavior, which the rule as literally written did not cover.
- **Approval-packet date drift**: if review extends past 2026-05-29, the packet filename date will not match the actual implementation day, and the impl-start gate would reject the path. Mitigation: Prime will re-revise this proposal with the corrected date before implementation if the GO arrives on a different day; the impl-start gate would catch this case in any event.

Rollback: revert the rule section + doctor check + tests; delete the approval packet JSON; no MemBase/state to roll back (DELIB/project/PAUTH/WI are append-only inventory).

## Loyal Opposition Asks

1. Confirm the REVISED-2 closes NO-GO -004 F1 (Approval Packet Plan now lists `artifact_id` and `source_ref` as required, `action = "update"`, `approval_mode = "approve"`; matches live schema at `groundtruth-kb/src/groundtruth_kb/governance/narrative_artifact_packet.py`).
2. Confirm the REVISED-2 closes NO-GO -004 F2 (Spec-to-Test Mapping now includes `scripts/check_narrative_artifact_evidence.py --staged` as the Slice C pre-commit evidence floor with positive + negative coverage).
3. Confirm the bounded exception shape remains the right governance contract.
4. Advise whether the exception's machine-checkable constraints should ALSO be formalized as a DCL.
5. Confirm `_check_external_harness_exec_boundary` design satisfies the "prevent expansion" requirement.
6. Confirm scoping WI-3349 resumption as a separate follow-on thread is appropriate.
7. Note any spec to add to Specification Links.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
