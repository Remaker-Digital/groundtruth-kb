# WI-5016 MemBase/Governance Duplicate-SoT Audit

Claim: the MemBase and governance lane has no uncovered duplicate-SoT violation.

Evidence:

- `gt registry audit-duplicates --json --output-dir .gtkb-state/sot-singleton-audit/wi5016-membase-governance`
- Coverage complete: 25 registry records, 93,448 persistent files, 10,207 registered files.
- Violations: 1 total, 0 uncovered.
- The only violation is `duplicate-dispatch-harness-fields`, already covered by `WI-5012`.
- MemBase specification/work-item/test/deliberation/project/PAUTH/assertion-run rows classify as registered SoT classes.
- `gt registry validate --json` reports TOML/MemBase projection parity in sync: 25/25, no divergences.
- `gt spec show GOV-SOT-SINGLETON-001` confirms the singleton GOV exists in MemBase.

Risk/impact: no MemBase/governance remediation work item is required from this lane. The known dispatcher/harness duplicate remains open under `WI-5012`.

Recommended action: verify WI-5016 and keep any dispatch-field remediation inside `PROJECT-GTKB-DISPATCH-SELECTION-SELF-OPTIMIZATION` / `WI-5012`.

Decision needed from owner: none.
