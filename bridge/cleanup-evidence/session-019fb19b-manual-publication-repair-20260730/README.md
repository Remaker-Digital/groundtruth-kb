# Manual bridge-publication repair evidence

This directory preserves exact incident bytes from Prime Builder session
`019fb19b-7814-73c1-8707-204e432cbf00`. These copies are forensic evidence,
not live numbered bridge entries, publication receipts, verdicts, or
implementation authority. The disabled TAFE/dispatcher surface was not
activated or mutated during recovery.

| Evidence copy | Bytes | SHA-256 | Disposition |
| --- | ---: | --- | --- |
| `gtkb-advisory-wi5368-cross-thread-target-collision-001.md` | 14,228 | `50A06969B7242414A959001971F4132A04B413DDD591870FDCA2B9BB4E9C4FD6` | Original unreceipted draft bytes. Corrected live v001 is typed row 401, `consumed`. |
| `gtkb-advisory-wi5757-implementation-start-orchestration-concurrency-001.md` | 11,681 | `F96D22211F44ACD23314EB6ECED46F06F909B4989B1534B806D9DF37ECD7B7C2` | Original unreceipted bytes. Corrected live v001 is typed row 403, `consumed`, revision `SOTREV-B78208F10F10410997449CB4D633E539`. |
| `gtkb-wi5757-advisory-router-dedup-starvation-003.md` | 11,819 | `990BF79A3693EB39EB377FBD74DD04ED15DEB165148780CBC242F80CEC9792CA` | Original unreceipted report bytes. Corrected live v003 is typed row 404, `consumed`, revision `SOTREV-4E1201B0BDC94C15A360417F5258B931`. |
| `gtkb-wi5299-reissued-finalizer-failure-repair-008.md` | 11,308 | `FC27C688777087087736570C5877C9A7224EE4D63D968BA4B5FA1ED88F02AB64` | Exact copy made during audit. The identical top-level historical file was restored because strict lifecycle resolution is already poisoned at v005; no typed receipt exists for v008. |
| `gtkb-wi5759-ruff-gate-staged-blob-003.md` | 12,059 | `BBEEE63E3541B147412992CFAF13788426BFE90333C0A714DE0697FC96FE99CE` | Exact copy made during audit. The identical top-level predecessor was restored because later v004 exists; v004 capability row 393 is `recovery_required`. |

The separate directory
`bridge/cleanup-evidence/wi5368-unreceipted-v007-recovery-20260730/`
preserves the first unreceipted WI-5368 v007 bytes and its recovery record.

No later receipt retroactively authenticates any incident byte stream listed
here. Exact receipt state is authoritative only for the content digest recorded
by the corresponding `sot_registry_bridge_publication_capabilities` row.
