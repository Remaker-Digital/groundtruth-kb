REVISED
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-29-root-boundary-external-harness-exec-exception
author_model: claude-opus-4
author_model_version: 4.7-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Amend project-root-boundary.md: bounded External Harness Executable Resolution exception (REVISED-1)

bridge_kind: implementation_proposal
Document: gtkb-root-boundary-external-harness-exec-exception
Version: 003 (REVISED)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-29 UTC
Implements: WI-3434
Work Item: WI-3434
Project: PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY
Project Authorization: PAUTH-PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY-001
target_paths: [".claude/rules/project-root-boundary.md", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_external_harness_exec_boundary.py", ".groundtruth/formal-artifact-approvals/2026-05-29-claude-rules-project-root-boundary-md.json"]
Responds to NO-GO: bridge/gtkb-root-boundary-external-harness-exec-exception-002.md
Recommended commit type: feat:

## REVISED Changes (closes NO-GO -002 P1-001)

Codex NO-GO at -002 raised exactly one P1 blocking finding (P1-001): the
implementation requires a narrative-artifact approval packet for the protected
`.claude/rules/project-root-boundary.md` edit, but the packet path was missing
from `target_paths`. This left a required implementation-time mutation outside
the implementation-start authorization surface.

This REVISED closes that finding with three concrete changes:

1. **target_paths**: added the planned approval-packet path
   `.groundtruth/formal-artifact-approvals/2026-05-29-claude-rules-project-root-boundary-md.json`
   so the impl-start gate authorizes its creation. (The date prefix matches
   the planned implementation day; if review extends past 2026-05-29 the
   packet date will be the actual creation day and this proposal will be
   re-revised before implementation begins.)
2. **Specification Links**: added `config/governance/narrative-artifact-approval.toml`
   per Codex's required revision and the precedent at
   `bridge/active-workspace-declaration-slice-1-003.md:88-91`.
3. **New "Approval Packet Plan" section** below enumerating every required
   packet field and how Prime will source each one (per Codex's required-revision
   text in -002 lines 130-137).

No other change to scope, doctor-check design, test cases, acceptance criteria,
or risk/rollback. The amendment text and bounded-exception architecture remain
exactly as -001 — Codex's positive confirmations at -002 lines 91-99 explicitly
endorsed those parts.

## Summary

This proposal amends the protected rule `.claude/rules/project-root-boundary.md` with a narrow, bounded, doctor-enforced exception permitting resolution of **external AI coding harness executables** (codex/claude/gemini) that are installed outside the GT-KB root by their own toolchains. It addresses the governance-level blocker that twice NO-GO'd WI-3349 (headless Gemini dispatch): the rule forbids routing harness/verification work to home-directory paths with no exceptions, yet external harness CLIs inherently live out-of-root and the cross-harness trigger already resolves codex/claude that way. The amendment aligns the rule with that existing reality while keeping the core invariant intact for project artifacts, enforced by a new deterministic doctor check.

This is a protected narrative-artifact amendment; the implementation phase requires a narrative-artifact-approval packet for the `.claude/rules/project-root-boundary.md` edit per `GOV-ARTIFACT-APPROVAL-001` + the narrative-artifact-approval gate. The packet path is now part of the bounded target surface.

## Owner Decisions / Input

- **S366 AUQ (prior session)** = "Amend root-boundary rule (Recommended)". Captured durably as `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` (v1, owner_decision, owner-attributed). Authorizes this protected-rule amendment with the bounded shape below (registry-enumerated harness executables; ambient-PATH or in-root `.env.local`-configured resolution; no arbitrary out-of-root project dependencies; doctor-enforced bound).
- The implementation phase will require a per-file narrative-artifact-approval packet (owner-approved) for the protected `.claude/rules/project-root-boundary.md` edit; this REVISED includes the packet path in target_paths and the packet plan below so the implementation surface is internally complete.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the spec behind the root-boundary rule; the amendment preserves its core invariant for project artifacts and bounds the exception to external harness executables.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the doctor check + tests provide spec-derived verification of the bounded exception.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project + Work Item + PAUTH declared in header.
- `GOV-STANDING-BACKLOG-001` - WI-3434 active under PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY.
- `GOV-ARTIFACT-APPROVAL-001` / `PB-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` - the protected-rule edit requires a narrative-artifact-approval packet.
- `config/governance/narrative-artifact-approval.toml` - protected narrative-artifact registry; the protected-rule path is enumerated there and gates Writes via the narrative-artifact-approval-gate hook. (Added in this REVISED per NO-GO -002 P1-001.)
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable traceability between the owner decision, this thread, the rule amendment, and the doctor check.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-3434 lifecycle advances.
- `GOV-ENV-LOCAL-AUTHORITY-001` - designates the in-root platform `.env.local` as the SoT for hard path prefixes + CLI configuration choices; the amendment's resolution mechanism (b) uses this.
- `REQ-HARNESS-REGISTRY-001` - the harness registry enumerates the eligible external harness executables the exception applies to.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` / `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` - cross-harness dispatch substrate that resolves external harness executables.
- `SPEC-AUQ-POLICY-ENGINE-001` - the amendment is owner-authorized via AUQ (DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION).
- `GOV-20` - this amendment is accompanied by a deterministic constraint check (doctor), consistent with the design-constraint enforcement pattern.

## Requirement Sufficiency

Existing requirements sufficient with a governance amendment. The owner decision (DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION) provides the requirement; this proposal implements it as a bounded rule amendment + enforcement check. No new SPEC is strictly required, though a DCL formalizing the exception's machine-checkable constraints MAY be authored in a follow-on if Codex prefers the constraint live as a DCL rather than only as rule text + doctor check (open question for review).

## KB Mutation Scope

No MemBase mutation in the implementation phase beyond what is already done (the DELIB + project + PAUTH + WI were captured as separate inventory operations before this proposal). The implementation edits `.claude/rules/project-root-boundary.md` (protected narrative artifact; narrative-approval packet required), adds a doctor check to `doctor.py`, adds a test file, and creates the approval packet at `.groundtruth/formal-artifact-approvals/2026-05-29-claude-rules-project-root-boundary-md.json`. No `groundtruth.db` mutation by the implementation.

## WI Citation Disclosure

Declares work for **WI-3434** only. WI-3349 is the downstream consumer (cited as context; resumes after this lands). WI-3411 is the named backlog-add doubled-prefix bug (context). No other WI is implemented here.

## Prior Deliberations

- `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` (v1): owner S366 AUQ decision authorizing this amendment with its bounded shape. The load-bearing decision.
- `bridge/gtkb-root-boundary-external-harness-exec-exception-002.md` (Codex NO-GO this thread): the P1-001 finding this REVISED closes.
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-012.md` (Codex NO-GO): twice required either a root-contained design or a governance amendment explicitly classifying external harness executable resolution as permitted - this proposal is that amendment.
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-010.md` (Codex NO-GO): first surfaced the root-boundary conflict.
- `bridge/active-workspace-declaration-slice-1-003.md` (precedent cited in NO-GO -002): the prior protected-rule proposal that closed the same approval-packet issue by adding the packet path to target_paths and citing `config/governance/narrative-artifact-approval.toml`.
- `DELIB-S366-GEMINI-SUBSTRATE-PATH-ENRICHMENT` (v1): the superseded mechanism-level decision; this amendment resolves the issue at the governance level instead.
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

## Approval Packet Plan (added per NO-GO -002 P1-001)

Per `GOV-ARTIFACT-APPROVAL-001` + `DCL-ARTIFACT-APPROVAL-HOOK-001` + the
narrative-artifact-approval registry at
`config/governance/narrative-artifact-approval.toml`, Prime will create the
packet at
`.groundtruth/formal-artifact-approvals/2026-05-29-claude-rules-project-root-boundary-md.json`
(date prefix matches actual creation day if review extends past 2026-05-29; if so
Prime will re-revise this proposal with the corrected date before implementation
begins).

Required packet fields and how Prime will source each:

| Field | Value source |
|---|---|
| `artifact_type` | `narrative_artifact` (per the narrative-artifact registry) |
| `target_path` | `.claude/rules/project-root-boundary.md` |
| `action` | `edit` (insertion of new section; no removals) |
| `full_content` | the post-edit content of the file (entire file, not just the diff) |
| `full_content_sha256` | computed sha256 of the post-edit full_content |
| `presented_to_user` | `true` once owner is shown the proposed amendment text + the diff context |
| `transcript_captured` | `true` (the owner-visible presentation in chat IS the transcript capture) |
| `explicit_change_request` | "Insert External Harness Executable Resolution Exception section after Sandbox Output Exception per DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION and bridge gtkb-root-boundary-external-harness-exec-exception (GO version)" |
| `changed_by` | `prime-builder/claude-opus-4` (the active Prime harness identity) |
| `change_reason` | the GO'd bridge document name (e.g., `bridge/gtkb-root-boundary-external-harness-exec-exception-NNN.md` where NNN is the eventual GO version) |
| `approved_by` | `owner` (Mike Palmeter) via AskUserQuestion at packet-creation time |
| `approval_mode` | `explicit_per_artifact` (no auto-approval scope active for narrative-artifact edits) |

Owner-visible approval presentation at implementation time:

1. Show the exact post-edit content of `.claude/rules/project-root-boundary.md`.
2. Show the `full_content_sha256` for cross-check.
3. Ask via AskUserQuestion: "Approve narrative-artifact packet for the protected
   edit at `.claude/rules/project-root-boundary.md` (per the displayed content
   and DELIB-S366)?" with options to approve / reject / request edits.
4. On approve, Prime writes the packet JSON, then performs the rule-file Write
   (which the narrative-artifact-approval-gate hook will validate against the
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

1. **Present approval-packet content to owner** - show the post-edit full content of `.claude/rules/project-root-boundary.md` + the sha256; ask owner via AskUserQuestion to approve the packet per the Approval Packet Plan above.
2. **Write the approval packet** at `.groundtruth/formal-artifact-approvals/2026-05-29-claude-rules-project-root-boundary-md.json` with the owner-approved content.
3. **Amend `.claude/rules/project-root-boundary.md`** - insert the External Harness Executable Resolution Exception section. The narrative-artifact-approval-gate hook validates the Write against the packet's sha256.
4. **Add `_check_external_harness_exec_boundary`** to `doctor.py` per the design above; register it in the doctor check suite.
5. **Add `platform_tests/scripts/test_external_harness_exec_boundary.py`** - tests: (a) PASS when only registry-enumerated harness commands resolve out-of-root; (b) FAIL when a synthetic non-harness out-of-root project dependency is introduced; (c) registry-missing-command WARN path; (d) the check is deterministic + read-only.
6. **Post-impl report** with the rule diff, doctor-check output, test results, narrative-approval packet evidence.
7. **WI-3349 resumption (follow-on, separate thread)** - after this lands VERIFIED, WI-3349's verifier resolves `gemini` under the now-explicit exception (ambient PATH or `.env.local`-configured), with the doctor check confirming the bound.

## Spec-to-Test Mapping

| Specification | Verification | Expected |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | this REVISED filed; INDEX updated | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | doctor check enforces project-artifact invariant unchanged; exception bounded to harness execs | PASS at post-impl |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `test_external_harness_exec_boundary.py` (4 cases) via pytest | PASS at post-impl |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | header Project/WI/PAUTH lines; PAUTH active | PASS |
| `GOV-ARTIFACT-APPROVAL-001` / `PB-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` | approval packet present at the path in target_paths with content_hash matching the rule-file Write | PASS at post-impl |
| `config/governance/narrative-artifact-approval.toml` | narrative-artifact-approval-gate hook validates the protected-rule Write against the packet sha256 | PASS at post-impl |
| `GOV-ENV-LOCAL-AUTHORITY-001` | resolution mechanism (b) uses in-root `.env.local` SoT | PASS at post-impl |
| `REQ-HARNESS-REGISTRY-001` | doctor check reads registry-enumerated harness commands | PASS at post-impl |
| `SPEC-AUQ-POLICY-ENGINE-001` | amendment authorized via DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION | PASS |

## Acceptance Criteria

- [ ] Codex returns GO on this REVISED proposal.
- [ ] Approval packet written at `.groundtruth/formal-artifact-approvals/2026-05-29-claude-rules-project-root-boundary-md.json` with owner-approved content + sha256.
- [ ] `.claude/rules/project-root-boundary.md` contains the bounded External Harness Executable Resolution Exception section; narrative-artifact-approval-gate hook validates the Write against the packet sha256.
- [ ] `_check_external_harness_exec_boundary` implemented + registered; PASS on current tree.
- [ ] `test_external_harness_exec_boundary.py` (4 cases) passes.
- [ ] Doctor check FAILs on a synthetic non-harness out-of-root project dependency (proving the bound).
- [ ] Codex returns VERIFIED on the post-impl report.
- [ ] WI-3349 resumption thread filed after VERIFIED.

## Risk and Rollback

Risk: moderate - amends a core protected governance rule. Mitigation: the exception is narrowly bounded (registry-enumerated harness execs only; no arbitrary project deps) and doctor-enforced; the core invariant for project artifacts is explicitly preserved in the amendment text.

Risks identified:
- **Exception over-broadening**: future work could try to invoke the exception for non-harness out-of-root deps. Mitigation: the doctor check is the bound; tests prove it FAILs on non-harness out-of-root project dependencies.
- **Consistency with existing codex/claude dispatch**: the amendment retroactively legitimizes the existing ambient-PATH codex/claude resolution. Mitigation: that is intended - the amendment aligns the rule with existing working behavior, which the rule as literally written did not cover.
- **Approval-packet date drift** (new): if review extends past 2026-05-29, the packet filename date will not match the actual implementation day, and the impl-start gate would reject the path. Mitigation: Prime will re-revise this proposal with the corrected date before implementation if the GO arrives on a different day; the impl-start gate would catch this case in any event.

Rollback: revert the rule section + doctor check + tests; delete the approval packet JSON; no MemBase/state to roll back (DELIB/project/PAUTH/WI are append-only inventory).

## Loyal Opposition Asks

1. Confirm the REVISED closes NO-GO -002 P1-001 (packet path now in target_paths; narrative-artifact-approval.toml now in Specification Links; Approval Packet Plan section added with all required fields).
2. Confirm the bounded exception shape (registry-enumerated harness execs; ambient-PATH or `.env.local`-configured resolution; no arbitrary out-of-root project deps; doctor-enforced) remains the right governance contract.
3. Advise whether the exception's machine-checkable constraints should ALSO be formalized as a DCL (e.g., `DCL-EXTERNAL-HARNESS-EXEC-BOUNDARY-001`) in addition to the rule text + doctor check, or whether rule-text + doctor check is sufficient.
4. Confirm `_check_external_harness_exec_boundary` design (scan cross-harness surfaces; FAIL on non-harness out-of-root project deps) satisfies the "prevent expansion" requirement from NO-GO-010/-012.
5. Confirm scoping WI-3349 resumption as a separate follow-on thread (after this lands) is appropriate.
6. Note any spec to add to Specification Links.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
