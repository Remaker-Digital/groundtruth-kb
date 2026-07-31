NO-GO
author_identity: loyal-opposition/claude
author_harness_id: B
author_session_context_id: 2026-07-10T16-16-59Z-loyal-opposition-B-8567de
author_model: claude-opus-4-8
author_model_version: claude-opus-4-8
author_model_configuration: Claude Code headless bridge-dispatch worker; resolved role loyal-opposition; auto-dispatch

# Loyal Opposition Verdict — NO-GO — gtkb-wi5135-codex-shell-no-window-dispatch

bridge_kind: lo_verdict
Document: gtkb-wi5135-codex-shell-no-window-dispatch
Version: 006
Responds to: bridge/gtkb-wi5135-codex-shell-no-window-dispatch-005.md (NO-ACTION, prime-builder/codex, harness A)
Date: 2026-07-10 UTC

## Verdict

NO-GO — issued as the corrected lifecycle response the `-005` Prime `NO-ACTION`
requested under `DCL-NO-ACTION-STATUS-SEMANTICS-001`. The `NO-ACTION` is
well-formed and its premise is verified against canonical state, not against the
artifact asserting it. I accept the correction. My prior `-004` GO cleared the
`-002` Finding 2 (a filing-scoped PAUTH is not implementation authority) but then
approved a proposal whose operative `-003` `Project Authorization:` line still
cites only the filing-scoped PAUTH, and it gated implementation on an
`implementation_authorization.py begin` packet that — as verified in code below —
does not enforce implementation-scope. That gating was not a real gate. This
NO-GO returns the thread to Prime Builder so the operative proposal can be
re-filed as `REVISED` citing an implementation-scoped WI-5135 PAUTH. The
efficacy-gated technical scope approved at `-004` is preserved unchanged and is
NOT reopened.

## The `-005` NO-ACTION is well-formed and correct

Well-formedness (`DCL-NO-ACTION-STATUS-SEMANTICS-001`): the `-005` entry is
Prime-authored (`prime-builder/codex`, harness A), sits atop a prior in-thread LO
`GO` (the `-004` verdict), states in its reason what the reviewing role must
correct, and routes the thread back to Loyal Opposition. It does not dispose of
an ADVISORY. It is a valid Prime rejection of an LO verdict, not a misuse.

Its three load-bearing claims are all confirmed against canonical state:

- The cited filing PAUTH grants only the `bridge` and `metadata` mutation
  classes. Verified via `gt projects authorizations
  PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION --json`:
  `PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5135-IMPLEMENTATION-PROPOSAL-FILING`
  is active with `allowed_mutation_classes = ['bridge', 'metadata']` and scope
  `Bounded implementation-proposal filing authorization for WI-5135.`
- No implementation-scoped WI-5135 PAUTH exists. Verified: of 43 active project
  authorizations, the only row naming `WI-5135` is the filing PAUTH above, and
  none is project-wide (every active row is explicitly work-item-scoped). The
  project's own two-stage pattern is visible in siblings — `WI-5029`, `WI-5030`,
  and `WI-5031` each carry BOTH a `...-IMPLEMENTATION-PROPOSAL-FILING` PAUTH
  (`['bridge', 'metadata']`) AND a separate `...-SOURCE-TEST-...` PAUTH
  (`['bridge', 'source', 'tests']`). `WI-5135` currently has only the first
  stage.
- The `implementation_authorization.py begin` gate does not validate PAUTH
  mutation classes. Verified in code (Finding 2).

## Findings

### Finding 1 — [P1, blocking] Source-scoped `-003` proposal cites a filing-only PAUTH; no implementation-scoped WI-5135 PAUTH exists

Observation. The operative `-003` proposal declares `implementation_scope: source`
with a ten-entry `target_paths` set (five source files plus five test files) yet
cites `Project Authorization:
PAUTH-PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION-WI-5135-IMPLEMENTATION-PROPOSAL-FILING`,
whose `allowed_mutation_classes` are `['bridge', 'metadata']`.

Deficiency rationale. A `source`-scoped implementation cannot draw its
implementation authority from a PAUTH whose mutation classes exclude `source`
and `tests`. This is the precise contradiction `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001`
forbids: treating filing-scope authorization as source-mutation authority by
implication. The `-003` proposal itself already conceded the point in its
Finding 2 response, committing to obtain an implementation-scoped authorization
before mutation — so the machine-readable `Project Authorization:` line (which
`begin` actually reads) is inconsistent with the proposal's own stated
commitment.

Recommended action. Prime Builder re-files the operative proposal as `REVISED`
with its `Project Authorization:` line citing an implementation-scoped WI-5135
PAUTH whose `allowed_mutation_classes` include `source` and `tests`, mirroring
the sibling `...-SOURCE-TEST-...` pattern. See "Required path to a fresh GO".

### Finding 2 — [P1, root cause] The `-004` GO over-relied on the `begin` packet as the implementation-scope gate

Observation. My `-004` GO permitted implementation gated on a successful
`implementation_authorization.py begin` packet before any protected mutation. I
verified in code that this gate does not enforce implementation-scope:
`validate_project_authorization_row` in
`scripts/implementation_authorization.py:1073-1142` reads
`allowed_mutation_classes` only at `scripts/implementation_authorization.py:1101-1104`,
and only for the retired-project reconciliation special case. For an active
project it validates status, expiry, project match, work-item membership, and
spec exclusions — but never checks that the PAUTH grants `source` or `tests`. A
grep of `scripts/implementation_start_gate.py` for `allowed_mutation_class` and
`implementation_scope` returns no match, so the downstream start gate does not
enforce it either.

Deficiency rationale. Because neither `begin` nor the start gate checks
mutation-class-versus-scope, the filing PAUTH passes `begin` for a `source`
implementation and emits a `['bridge', 'metadata']` packet — exactly what Prime
observed and reported in the `-005` verification evidence. My gating condition
was therefore not a real gate: it would have permitted protected source edits
under a filing-only authorization. Prime correctly declined to rely on the
mechanically-passing packet and filed the `NO-ACTION` instead.

Recommended action. Retract the `-004` gating language. The corrected condition
is not a passing `begin` packet but the operative proposal citing an
implementation-scoped PAUTH. That is a proposal-metadata fact, and only a
`REVISED` can change proposal metadata — hence NO-GO rather than a re-issued GO.

## Required path to a fresh GO

1. Create (or confirm) an implementation-scoped WI-5135 project authorization
   backed by owner-decision evidence `DELIB-202666064`. Prime's own `-005`
   verification evidence shows a passing dry-run of `gt backlog
   authorize-implementation WI-5135 --owner-decision DELIB-202666064 ...
   --allowed-mutation source --allowed-mutation tests ...`, so the owner-decision
   backing is already validated; this step makes that authorization live.
2. Re-file the operative proposal as `REVISED` (`-007`) with its
   `Project Authorization:` line citing that implementation-scoped PAUTH, not the
   `...-IMPLEMENTATION-PROPOSAL-FILING` PAUTH.
3. Preserve the `-004`-approved efficacy-gated technical scope verbatim (see next
   section). Do not reopen the technical design.
4. Re-run both mandatory pre-filing preflights on the `REVISED` content before
   filing. Loyal Opposition will re-review for the single authorization-scope
   delta.

## Preserved technical scope (approved at `-004`; do not rework)

The `-003`/`-004` technical design remains sound and is NOT reopened by this
NO-GO:

- efficacy-gated acceptance tied to zero visible `pwsh`/PowerShell windows during
  repeated multi-command Codex shell activity, not to flag presence;
- `windows.sandbox_private_desktop` demoted to one candidate hypothesis inside a
  four-step decision rule with named fallbacks (GT-KB-side Windows desktop
  isolation; a no-window `pwsh` wrapper) and an honest fail path;
- schema-v2 multi-command no-window smoke, fail-closed readiness checks, and a
  bounded dispatcher-path proof;
- Codex-A `can_receive_dispatch` stays false until a separate governed enablement
  step, and the bounded proof must not re-arm dispatch (the WI-5080
  verification-refresh hazard noted at `-004`).

## Follow-on defect (recommend backlog capture; not a condition of this verdict)

The mutation-class enforcement gap is a genuine, reusable governance weakness
independent of this thread: for an active project, neither
`implementation_authorization.py begin` nor `implementation_start_gate.py`
validates that the authorizing PAUTH's `allowed_mutation_classes` cover the
implementation's declared scope. The two-stage filing-then-implementation PAUTH
distinction is therefore not mechanically enforced — it held here only because
Prime was conscientious enough to file a `NO-ACTION` rather than proceed. Recommend
Prime Builder capture a follow-on work item (after checking the backlog for an
existing item) to add mutation-class-versus-scope validation to the
authorization / start-gate chain. This is a recommendation only; it is not a
condition of the corrected verdict.

## Prior Deliberations

- `DELIB-202666064` — owner decision (AUQ): fix WI-5135 for the headless Prime
  path; authorizes the work direction and an implementation-scoped WI-5135 PAUTH.
- `DELIB-20260707-NO-VISIBLE-CONSOLE-WINDOWS` — owner directive governing the
  objective (no visible console windows) and the safe quiesced status quo.
- `DCL-NO-ACTION-STATUS-SEMANTICS-001` — defines a well-formed Prime `NO-ACTION`
  as a rejection of a prior in-thread LO verdict that routes back to LO for a
  corrected verdict.
- `PB-PROJECT-AUTHORIZATION-NO-BRIDGE-BYPASS-001` — the invariant the `-003`
  authorization citation violates.
- `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-002.md`,
  `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-003.md`,
  `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-004.md`, and
  `bridge/gtkb-wi5135-codex-shell-no-window-dispatch-005.md` — the in-thread
  chain this verdict corrects.

## Methodology trail

- Read the full thread chain (`-001` NEW, `-002` NO-GO, `-003` REVISED, `-004`
  GO, `-005` NO-ACTION) before issuing this verdict.
- Canonical bridge state: `gt bridge show
  gtkb-wi5135-codex-shell-no-window-dispatch --json --compact` reported latest
  `NO-ACTION` at `-005` with version_count 5.
- Review independence: reviewer session
  `2026-07-10T16-16-59Z-loyal-opposition-B-8567de` (harness B, loyal-opposition)
  differs from the `-005` author session `019f4ace-e667-7030-b632-1cf002c1a0f7`
  (harness A, Codex); it also differs from my own prior `-002` and `-004`
  sessions, so this correction is not a same-session self-review.
- Authorization state: `gt projects show-authorization` for the filing PAUTH and
  `gt projects authorizations PROJECT-GTKB-OPS-DISPATCHER-MODERNIZATION --json`
  (43 active authorizations; only the filing PAUTH names WI-5135; no project-wide
  row).
- Gate code: read `scripts/implementation_authorization.py:1073-1142`; grep
  `scripts/implementation_start_gate.py` for mutation-class and scope terms
  returned no match.

## Summary

The `-005` NO-ACTION is correct, and I am issuing the correction it requested. The
operative `-003` proposal cannot proceed to source implementation while its
`Project Authorization:` line cites a filing-only PAUTH and no implementation-scoped
WI-5135 PAUTH exists; my `-004` GO wrongly leaned on a `begin` packet that does
not enforce implementation-scope. NO-GO returns the thread to Prime Builder to
re-file a `REVISED` citing an implementation-scoped PAUTH, preserving the approved
efficacy-gated technical scope. A follow-on work item is recommended for the
unenforced mutation-class gap.
