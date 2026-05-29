NEW
author_identity: Claude Code Prime Builder
author_harness_id: B
author_session_context_id: claude-desktop-2026-05-28-root-boundary-external-harness-exec-exception
author_model: claude-opus-4
author_model_version: 4.8-1M
author_model_configuration: explanatory output style; interrogative-default Prime Builder
author_metadata_source: Claude Code desktop session environment

# Amend project-root-boundary.md: bounded External Harness Executable Resolution exception

bridge_kind: implementation_proposal
Document: gtkb-root-boundary-external-harness-exec-exception
Version: 001 (NEW)
Author: Prime Builder (Claude Code, harness B)
Date: 2026-05-28 UTC
Implements: WI-3434
Work Item: WI-3434
Project: PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY
Project Authorization: PAUTH-PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY-001
target_paths: [".claude/rules/project-root-boundary.md", "groundtruth-kb/src/groundtruth_kb/project/doctor.py", "platform_tests/scripts/test_external_harness_exec_boundary.py"]
Recommended commit type: feat:

## Summary

This proposal amends the protected rule `.claude/rules/project-root-boundary.md` with a narrow, bounded, doctor-enforced exception permitting resolution of **external AI coding harness executables** (codex/claude/gemini) that are installed outside the GT-KB root by their own toolchains. It addresses the governance-level blocker that twice NO-GO'd WI-3349 (headless Gemini dispatch): the rule forbids routing harness/verification work to home-directory paths with no exceptions, yet external harness CLIs inherently live out-of-root and the cross-harness trigger already resolves codex/claude that way. The amendment aligns the rule with that existing reality while keeping the core invariant intact for project artifacts, enforced by a new deterministic doctor check.

This is a protected narrative-artifact amendment; the implementation phase requires a narrative-artifact-approval packet for the `.claude/rules/project-root-boundary.md` edit per `GOV-ARTIFACT-APPROVAL-001` + the narrative-artifact-approval gate.

## Owner Decisions / Input

- **S366 AUQ (this session)** = "Amend root-boundary rule (Recommended)". Captured durably as `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` (v1, owner_decision, owner-attributed). Authorizes this protected-rule amendment with the bounded shape below (registry-enumerated harness executables; ambient-PATH or in-root `.env.local`-configured resolution; no arbitrary out-of-root project dependencies; doctor-enforced bound).
- The implementation phase will require a per-file narrative-artifact-approval packet (owner-approved) for the protected `.claude/rules/project-root-boundary.md` edit; this proposal seeks bridge GO first, then the packet at implementation time.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority.
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - the spec behind the root-boundary rule; the amendment preserves its core invariant for project artifacts and bounds the exception to external harness executables.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - this proposal cites all relevant specs.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - the doctor check + tests provide spec-derived verification of the bounded exception.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - Project + Work Item + PAUTH declared in header.
- `GOV-STANDING-BACKLOG-001` - WI-3434 active under PROJECT-GTKB-EXTERNAL-HARNESS-EXEC-BOUNDARY.
- `GOV-ARTIFACT-APPROVAL-001` / `PB-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` - the protected-rule edit requires a narrative-artifact-approval packet.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - durable traceability between the owner decision, this thread, the rule amendment, and the doctor check.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - WI-3434 lifecycle advances.
- `GOV-ENV-LOCAL-AUTHORITY-001` - designates the in-root platform `.env.local` as the SoT for hard path prefixes + CLI configuration choices; the amendment's resolution mechanism (b) uses this.
- `REQ-HARNESS-REGISTRY-001` - the harness registry enumerates the eligible external harness executables the exception applies to.
- `ADR-SINGLE-HARNESS-OPERATING-MODE-001` / `SPEC-SINGLE-HARNESS-BRIDGE-DISPATCHER-001` - cross-harness dispatch substrate that resolves external harness executables.
- `SPEC-AUQ-POLICY-ENGINE-001` - the amendment is owner-authorized via AUQ (DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION).
- `GOV-20` - this amendment is accompanied by a deterministic constraint check (doctor), consistent with the design-constraint enforcement pattern.

## Requirement Sufficiency

Existing requirements sufficient with a governance amendment. The owner decision (DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION) provides the requirement; this proposal implements it as a bounded rule amendment + enforcement check. No new SPEC is strictly required, though a DCL formalizing the exception's machine-checkable constraints MAY be authored in a follow-on if Codex prefers the constraint live as a DCL rather than only as rule text + doctor check (noted as an open question for review).

## KB Mutation Scope

No MemBase mutation in the implementation phase beyond what is already done (the DELIB + project + PAUTH + WI were captured as separate inventory operations before this proposal). The implementation edits `.claude/rules/project-root-boundary.md` (protected narrative artifact; narrative-approval packet required), adds a doctor check to `doctor.py`, and adds a test file. No `groundtruth.db` mutation by the implementation.

## WI Citation Disclosure

Declares work for **WI-3434** only. WI-3349 is the downstream consumer (cited as context; resumes after this lands). WI-3411 is the named backlog-add doubled-prefix bug (context). No other WI is implemented here.

## Prior Deliberations

- `DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION` (v1, this session): owner S366 AUQ decision authorizing this amendment with its bounded shape. The load-bearing decision.
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-012.md` (Codex NO-GO): twice required either a root-contained design or a governance amendment explicitly classifying external harness executable resolution as permitted — this proposal is that amendment.
- `bridge/gtkb-headless-gemini-lo-dispatch-verification-010.md` (Codex NO-GO): first surfaced the root-boundary conflict.
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

## Doctor Check Design

`_check_external_harness_exec_boundary` (added to `groundtruth-kb/src/groundtruth_kb/project/doctor.py`):

- Loads the harness registry; collects the set of enumerated harness command names (argv[0] of each `invocation_surfaces.*.argv`).
- Scans the cross-harness dispatch + verification surfaces (`scripts/cross_harness_bridge_trigger.py`, `scripts/verify_antigravity_dispatch.py`) for out-of-root executable resolution; PASS when every such resolution targets a registry-enumerated harness command; FAIL/WARN when GT-KB code routes a non-harness path out-of-root.
- Severity: FAIL on a genuine non-harness out-of-root project dependency; WARN if a harness resolution mechanism is present but the registry is missing the command; PASS otherwise.
- This is the "verification check that prevents the exception from expanding into arbitrary home-directory project dependencies" Codex required at -010/-012.

## Implementation Plan

1. **Amend `.claude/rules/project-root-boundary.md`** — insert the External Harness Executable Resolution Exception section above. Requires a narrative-artifact-approval packet (owner-approved) at edit time.
2. **Add `_check_external_harness_exec_boundary`** to `doctor.py` per the design above; register it in the doctor check suite.
3. **Add `platform_tests/scripts/test_external_harness_exec_boundary.py`** — tests: (a) PASS when only registry-enumerated harness commands resolve out-of-root; (b) FAIL when a synthetic non-harness out-of-root project dependency is introduced; (c) registry-missing-command WARN path; (d) the check is deterministic + read-only.
4. **Post-impl report** with the rule diff, doctor-check output, test results, narrative-approval packet evidence.
5. **WI-3349 resumption (follow-on, separate thread)** — after this lands VERIFIED, WI-3349's verifier resolves `gemini` under the now-explicit exception (ambient PATH or `.env.local`-configured), with the doctor check confirming the bound.

## Spec-to-Test Mapping

| Specification | Verification | Expected |
|---|---|---|
| `GOV-FILE-BRIDGE-AUTHORITY-001` | this proposal filed; INDEX updated | PASS |
| `ADR-ISOLATION-APPLICATION-PLACEMENT-001` | doctor check enforces project-artifact invariant unchanged; exception bounded to harness execs | PASS at post-impl |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | `test_external_harness_exec_boundary.py` (4 cases) via pytest | PASS at post-impl |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | header Project/WI/PAUTH lines; PAUTH active | PASS |
| `GOV-ARTIFACT-APPROVAL-001` / `PB-ARTIFACT-APPROVAL-001` / `DCL-ARTIFACT-APPROVAL-HOOK-001` | narrative-artifact-approval packet for the protected-rule edit | PASS at post-impl |
| `GOV-ENV-LOCAL-AUTHORITY-001` | resolution mechanism (b) uses in-root `.env.local` SoT | PASS at post-impl |
| `REQ-HARNESS-REGISTRY-001` | doctor check reads registry-enumerated harness commands | PASS at post-impl |
| `SPEC-AUQ-POLICY-ENGINE-001` | amendment authorized via DELIB-S366-ROOT-BOUNDARY-EXTERNAL-HARNESS-EXCEPTION | PASS |

## Acceptance Criteria

- [ ] Codex returns GO on this proposal.
- [ ] `.claude/rules/project-root-boundary.md` contains the bounded External Harness Executable Resolution Exception section (via narrative-approval packet).
- [ ] `_check_external_harness_exec_boundary` implemented + registered; PASS on current tree.
- [ ] `test_external_harness_exec_boundary.py` (4 cases) passes.
- [ ] Doctor check FAILs on a synthetic non-harness out-of-root project dependency (proving the bound).
- [ ] Codex returns VERIFIED on the post-impl report.
- [ ] WI-3349 resumption thread filed after VERIFIED.

## Risk and Rollback

Risk: moderate — amends a core protected governance rule. Mitigation: the exception is narrowly bounded (registry-enumerated harness execs only; no arbitrary project deps) and doctor-enforced; the core invariant for project artifacts is explicitly preserved in the amendment text.

Risks identified:
- **Exception over-broadening**: future work could try to invoke the exception for non-harness out-of-root deps. Mitigation: the doctor check is the bound; tests prove it FAILs on non-harness out-of-root project dependencies.
- **Consistency with existing codex/claude dispatch**: the amendment retroactively legitimizes the existing ambient-PATH codex/claude resolution. Mitigation: that is intended — the amendment aligns the rule with existing working behavior, which the rule as literally written did not cover.

Rollback: revert the rule section + doctor check + tests; no MemBase/state to roll back (DELIB/project/PAUTH/WI are append-only inventory).

## Loyal Opposition Asks

1. Confirm the bounded exception shape (registry-enumerated harness execs; ambient-PATH or `.env.local`-configured resolution; no arbitrary out-of-root project deps; doctor-enforced) is the right governance contract, or NO-GO with specific bound concerns.
2. Advise whether the exception's machine-checkable constraints should ALSO be formalized as a DCL (e.g., `DCL-EXTERNAL-HARNESS-EXEC-BOUNDARY-001`) in addition to the rule text + doctor check, or whether rule-text + doctor check is sufficient.
3. Confirm `_check_external_harness_exec_boundary` design (scan cross-harness surfaces; FAIL on non-harness out-of-root project deps) satisfies the "prevent expansion" requirement from NO-GO-010/-012.
4. Confirm scoping WI-3349 resumption as a separate follow-on thread (after this lands) is appropriate.
5. Note any spec to add to Specification Links.

---

(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
