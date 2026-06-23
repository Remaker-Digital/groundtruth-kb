REVISED

author_identity: Claude Prime Builder
author_harness_id: B
author_session_context_id: 5b6095bb-bdb4-45f0-b3fb-2f06e87dee2b
author_model: Claude Opus 4.8
author_model_version: claude-opus-4-8
author_model_configuration: explanatory output style; mode=auto

# Auto-Retire on VERIFIED - WI-4741 (REVISED-4: implements GOV spec v6 member-WI criterion; supersedes -007)

bridge_kind: prime_proposal
Project Authorization: PAUTH-PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001-WI-4741-AUTO-RETIRE-ON-VERIFIED-AUTOMATION
Project: PROJECT-GTKB-BACKLOG-TRIAGE-AND-HYGIENE-001
Work Item: WI-4741
target_paths: ["groundtruth-kb/src/groundtruth_kb/project/lifecycle.py", ".claude/skills/verify/helpers/write_verdict.py", ".codex/skills/verify/helpers/write_verdict.py", "scripts/project_verified_completion_scanner.py", "platform_tests/scripts/test_auto_retire_on_verified.py"]

Document: gtkb-auto-retire-on-verified-actuation-slice-1

## Supersedes -007 (concurrent implements-link alignment, now obsolete)

A concurrent Codex auto-builder session (author `auto-builder-2026-06-22T15-20Z`) filed `-007`
choosing the `-006` NO-GO's option 1 - align to the strict v5 implements-link criterion,
removing the member-WI criterion. `-007` was filed BEFORE
`GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v6 existed. The owner subsequently chose the
NO-GO's option 2 (formalize the member-WI criterion), and v6 (owner-approved 2026-06-22;
decision `DELIB-20265584`) now makes the member-WI terminal-resolution condition the GOVERNING
automatic-retirement rule, superseding the v4/v5 implements-link gating. `-007`'s
implements-link alignment therefore contradicts the current governing spec. This `-008`
supersedes `-007` and implements v6.

## NO-GO Resolution (-006: criterion now has durable spec + DELIB authority)

The `-006` NO-GO required durable governing-spec + decision evidence for the member-WI
criterion. That authority now exists:

- **`GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v6** (inserted 2026-06-22) makes member-WI
  terminal-resolution the governing automatic-retirement rule. Owner-approved in native review
  format via the v6 formal-artifact-approval packet.
- **`DELIB-20265584`** records the owner's 2026-06-22 reconcile-to-member-WI decision, linked to
  the spec and WI-4741.

The `-004` cross-harness verify-helper parity fix (both twins + byte-identity test) is retained.

## Implemented Criterion = GOV-...-001 v6 (member-WI terminal resolution)

`member_completion_ready(project_id)`: project has >= 1 active member work item; every active
member work item is in a terminal resolution status {verified, resolved, retired, wont_fix,
not_a_defect}; no active `plan_incomplete` completion guard. Verbatim the v6 governing rule
(membership-scoped; project-scoped by construction). Additive: the existing implements-link
authorization-completion machinery is retained for its own purpose (v6 explicitly preserves it).

## Design

1. **Predicate + retire routine** in `lifecycle.py`:
   `auto_retire_completed_projects(project_root, changed_by=...) -> list[str]` retires each
   `member_completion_ready` active project, best-effort (per-project try/except, never raise).
2. **Actuation seam - BOTH verify-helper twins, identical call-site**: after a successful VERIFIED
   finalization (post-commit), `.claude/skills/verify/helpers/write_verdict.py` AND
   `.codex/skills/verify/helpers/write_verdict.py` lazily import the lifecycle service and call
   `auto_retire_completed_projects(...)`, re-evaluating active projects' current member-WI state.
   Broad try/except: a VERIFIED verdict/commit is never rolled back by an actuation failure.
   The inserted block is byte-identical in both twins.
3. **Detector reconciliation** in `scripts/project_verified_completion_scanner.py`: add a
   membership-based completion view using `member_completion_ready` over ALL active projects
   (not only authorized ones); existing implements-link view retained (additive).

## In-Root Placement Evidence (ADR-ISOLATION-APPLICATION-PLACEMENT-001 / CLAUSE-IN-ROOT)

All target paths are in-root under `E:\GT-KB`. No out-of-root path is created or required.

## Scope Clarifications

- **Cited WIs are references, not the declared work item.** Declares `Work Item: WI-4741`.
  `WI-4750` (verify-helper parity, addressed) and `WI-4755` (governing-spec drift, resolved by
  v6) are cited as related context.
- **No canonical KB mutation during implementation; `groundtruth.db` is intentionally NOT a
  target_path.** Source-only change; `retire_project()` is a RUNTIME effect of deployed code;
  tests use temporary databases.
- **PAUTH scope confirmed.** The active PAUTH covers WI-4741 and includes
  `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` by spec ID (version-agnostic); v6 is that
  spec ID; the PAUTH scope (WI-4741 auto-retire actuation + detector) matches the v6 criterion.
  No PAUTH change required.

## Specification Links

- `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` (v6) - the governing spec this proposal
  implements (member-WI terminal-resolution retirement criterion).
- `GOV-STANDING-BACKLOG-001` - project authority reflects real lifecycle state.
- `GOV-08` - KB single source of truth.
- `GOV-FILE-BRIDGE-AUTHORITY-001` - bridge protocol authority.
- `GOV-HARNESS-ROLE-PORTABILITY-001` - cross-harness behavior parity (both verify-helper twins).
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` - in-root placement.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `.claude/rules/bridge-essential.md`

## Requirement Sufficiency

Existing requirements sufficient AS OF v6. The member-WI terminal-resolution criterion is the
governing requirement in `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` v6 (owner-approved
2026-06-22; decision `DELIB-20265584`). This proposal implements that requirement; no further
requirement change is needed.

## Prior Deliberations

- `DELIB-20265584` - owner reconcile-to-member-WI decision + v6 approval (the durable evidence
  the `-006` NO-GO required).
- `DELIB-20265569` - owner build-now decision (WI-4741).
- `DELIB-20265228` - decoupling authorization completion from automatic retirement (preserved in v6).
- `WI-4750` (verify-helper parity, addressed in -005/-008) and `WI-4755` (governing-spec drift,
  resolved by v6).
- `-001`..`-007` of this thread: implements-link proposal -> GO -> member-WI REVISED -> parity
  NO-GO -> parity REVISED -> criterion-authority NO-GO -> concurrent implements-link REVISED (-007,
  superseded here).
- `WI-3481` - premature multi-slice retirement risk (member-WI predicate uses current active
  membership; v6 codifies this safeguard).

## Spec-Derived Verification

New `platform_tests/scripts/test_auto_retire_on_verified.py`:

| Behavior (maps to GOV-...-001 v6) | Test |
|---|---|
| Auto-retire fires on all-member-terminal | all active member WIs terminal -> VERIFIED finalization -> project `status='retired'` |
| Open WI / guard / no-members block (v6 fail-safe) | non-terminal member, active `plan_incomplete` guard, or zero members -> NOT retired |
| Membership-scoped (no auth needed) | project with NO active authorization but all member WIs terminal -> detected/retired |
| Best-effort safety | actuation raising does NOT roll back the VERIFIED verdict/commit |
| Cross-harness parity (-004 fix) | both verify-helper twins byte-identical AND both contain the actuation call |
| Detector parity | scanner's membership view lists the same projects the predicate retires |

Commands: `python -m pytest platform_tests/scripts/test_auto_retire_on_verified.py -q`;
`python -m pytest groundtruth-kb/tests/test_project_artifacts.py -q` (regression of the
untouched authorization-completion machinery); `ruff check` + `ruff format --check` on all
changed files (both twins included).

## Risk / Rollback

- The member-WI criterion is now the owner-approved governing rule (v6); guards + append-only
  reversibility mitigate over-retirement.
- Twin drift mitigated by the byte-identity parity test.
- Actuation error cannot corrupt the verdict transaction (best-effort swallow + lazy import).
- Rollback: revert the lifecycle/scanner predicate + both twins' actuation call + remove the test.

## Owner Decisions / Input

- AUQ 2026-06-22 "Build the auto-retire automation now" (`DELIB-20265569`).
- AUQ 2026-06-22 "Reconcile to member-WI criterion" + "Formalize member-WI as a spec revision"
  + "Approve v6 as drafted" -> recorded as `DELIB-20265584`;
  `GOV-PROJECT-VERIFIED-COMPLETION-RETIREMENT-001` advanced to v6 via the v6 formal-artifact-approval
  packet. This supersedes the concurrent `-007` implements-link alignment, which predated v6.

## Recommended Commit Type

`feat:` - new event-driven auto-retirement capability implementing GOV-...-001 v6, wired into
both verify-helper twins with regression-locked parity.
