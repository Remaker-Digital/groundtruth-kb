WITHDRAWN

bridge_kind: operational_state_change
Document: gtkb-fab-10-codex-index-adapter-addendum
Version: 003
Responds-To: bridge/gtkb-fab-10-codex-index-adapter-addendum-002.md
Superseded-By: bridge/gtkb-fab-10-codex-index-adapter-addendum-sufficiency-001.md
Recommended commit type: docs

target_paths: ["bridge/gtkb-fab-10-codex-index-adapter-addendum-003.md", "bridge/INDEX.md"]

---

# FAB-10 Codex INDEX Adapter Addendum - Withdrawn As Mechanically Unusable

## Disposition

This bridge thread is withdrawn as a Prime-actionable GO because the approved
proposal at `bridge/gtkb-fab-10-codex-index-adapter-addendum-001.md` is
mechanically unusable by the implementation-start gate.

Loyal Opposition returned GO at
`bridge/gtkb-fab-10-codex-index-adapter-addendum-002.md`, and the substantive
scope remains valid. However, `scripts/implementation_authorization.py begin`
refuses to mint an implementation-start packet from that approved proposal
because the proposal omitted the mandatory `## Requirement Sufficiency`
section. Without that packet, Prime Builder must not mutate the scoped adapter
or test files under this thread.

The implementable replacement is already filed as
`bridge/gtkb-fab-10-codex-index-adapter-addendum-sufficiency-001.md`. That
replacement preserves the exact narrow adapter/test scope and adds the missing
mandatory requirement-sufficiency metadata.

## Evidence

Command:

```text
python scripts\implementation_authorization.py begin --bridge-id gtkb-fab-10-codex-index-adapter-addendum
```

Observed result:

```json
{"authorized": false, "error": "Approved proposal is missing ## Requirement Sufficiency"}
```

Live replacement thread read-back:

```text
python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-fab-10-codex-index-adapter-addendum-sufficiency --format json --preview-lines 160
```

Observed result: the replacement thread is present, latest `NEW`, and has
`drift: []`.

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` - this disposition records the live bridge lifecycle state.
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` - the original proposal cannot satisfy the implementation-start metadata gate.
- `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` - the replacement proposal carries project/work-item/authorization metadata.
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` - no implementation is claimed under this withdrawn thread; verification will belong to the replacement thread after GO and implementation.
- `GOV-STANDING-BACKLOG-001` - WI-4422 remains the backlog authority.
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` - the supersession is preserved as a durable bridge artifact.
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` - the defective GO is retired through an explicit lifecycle artifact instead of being silently ignored.
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` - the implementation-start gate failure is concrete lifecycle evidence requiring a disposition.

## Owner Decisions / Input

No new owner decision is required. This withdrawal does not change the
owner-approved FAB-10 HYG-039 scope from `DELIB-FAB10-REMEDIATION-20260610`; it
only closes a mechanically unusable bridge thread now superseded by a corrected
proposal.

## Specification-Derived Verification

| Specification | Verification command or evidence | Observed result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python .claude\skills\bridge\helpers\show_thread_bridge.py gtkb-fab-10-codex-index-adapter-addendum --format json --preview-lines 80` | Expected latest status is this `WITHDRAWN` file with `drift: []`. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | `python scripts\implementation_authorization.py begin --bridge-id gtkb-fab-10-codex-index-adapter-addendum` | Fails closed because the approved proposal is missing `## Requirement Sufficiency`. |
| `DCL-BRIDGE-PROPOSAL-PROJECT-LINKAGE-MANDATORY-001` | Replacement proposal metadata in `bridge/gtkb-fab-10-codex-index-adapter-addendum-sufficiency-001.md` | Replacement carries `Project`, `Work Item`, `Project Authorization`, and target paths. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | No source/test mutation is claimed here. | Verification is intentionally deferred to the replacement thread after GO and implementation. |
| Artifact-oriented governance trio | This disposition cites the gate failure and replacement thread. | Defective GO no longer remains a silent Prime-actionable trap. |

## Prime Builder Next Action

None for this withdrawn thread. Continue via
`gtkb-fab-10-codex-index-adapter-addendum-sufficiency` after Loyal Opposition
reviews the corrected proposal.
