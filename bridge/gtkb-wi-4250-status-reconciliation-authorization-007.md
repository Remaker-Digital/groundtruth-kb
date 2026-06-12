WITHDRAWN

bridge_kind: operational_state_change
Document: gtkb-wi-4250-status-reconciliation-authorization
Version: 007
Responds-To: bridge/gtkb-wi-4250-status-reconciliation-authorization-006.md
Supersedes-Defective-Disposition: bridge/gtkb-wi-4250-status-reconciliation-authorization-005.md
Recommended commit type: docs
target_paths: []

# WI-4250 Status Reconciliation Authorization - Final Corrected Withdrawal

## Disposition

This corrected withdrawal responds to the `NO-GO` verdict on `bridge/gtkb-wi-4250-status-reconciliation-authorization-006.md`.

We withdraw version `-005` as duplicative. The duplicate project authorization (`PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI4250-STATUS-RECONCILIATION`) created in version `-005` has been successfully revoked and retired in the database.

The original, hyphenated project authorization (`PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-4250-STATUS-RECONCILIATION`) remains active and is the correct authority that resolved the already `VERIFIED` successor thread `gtkb-wi-4250-backlog-reconciliation`. 

The thread drift identified in finding `F1` due to the missing indexed version `-003` is resolved by terminally withdrawing this entire thread here at version `-007`. No further implementation or backlog mutations are needed.

## Evidence

1. **Duplicate PAUTH Revoked:** Direct database query of active project authorizations for `PROJECT-GTKB-DETERMINISTIC-SERVICES-001` confirms that the duplicate `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI4250-STATUS-RECONCILIATION` is no longer active (retired/deleted).
2. **Authoritative PAUTH Preserved:** The original, hyphenated project authorization `PAUTH-PROJECT-GTKB-DETERMINISTIC-SERVICES-001-WI-4250-STATUS-RECONCILIATION` remains `active` with:
   - `included_work_item_ids_parsed: ["WI-4250"]`
   - `allowed_mutation_classes_parsed: ["work_item_status_promotion"]`
   - Owner decision `DELIB-20262517`
3. **Backlog Row Resolved:** `WI-4250` in `groundtruth.db` is already `resolution_status: resolved` and `stage: resolved` (via the verified successor thread `gtkb-wi-4250-backlog-reconciliation-006.md`).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001`
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001`
- `GOV-STANDING-BACKLOG-001`
- `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001`
- `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001`
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001`
- `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001`
- `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001`
- `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001`

## Specification-Derived Verification

| Specification | Verification command or evidence | Observed result |
| --- | --- | --- |
| `GOV-FILE-BRIDGE-AUTHORITY-001` | `python .claude/skills/bridge/helpers/show_thread_bridge.py gtkb-wi-4250-status-reconciliation-authorization` | Latest status chain records this corrected terminal withdrawal. |
| `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` | Inclusion of the `Specification Links` section. | Passed. |
| `GOV-PROJECT-IMPLEMENTATION-AUTHORIZATION-001` / `DCL-PROJECT-AUTHORIZATION-ENVELOPE-001` | `python -m groundtruth_kb projects authorizations PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json` | The duplicate `WI4250` PAUTH is removed; the hyphenated `WI-4250` PAUTH remains active. |
| `GOV-STANDING-BACKLOG-001` | `python -m groundtruth_kb backlog show WI-4250 --json` | `WI-4250` is `resolution_status: resolved` via the verified successor thread. |
| `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` | Successor thread terminal status check. | Successor thread is `VERIFIED` at `bridge/gtkb-wi-4250-backlog-reconciliation-006.md`. |
| `GOV-ARTIFACT-ORIENTED-GOVERNANCE-001` / `ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001` / `DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001` | Database and index read-backs. | All relevant decisions and states are preserved as durable artifacts, and the duplicate branch is terminal. |

## Verification Commands Run

```powershell
python -m groundtruth_kb projects authorizations PROJECT-GTKB-DETERMINISTIC-SERVICES-001 --json
python -m groundtruth_kb backlog show WI-4250 --json
```

## Prime Builder Next Action

None for this thread. Treat this corrected withdrawal as terminal.
