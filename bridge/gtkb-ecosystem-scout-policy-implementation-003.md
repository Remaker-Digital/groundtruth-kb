REVISED

# Implementation Proposal — GT-KB Ecosystem Scout and Import Policy

**Status:** REVISED
**Document name:** `gtkb-ecosystem-scout-policy-implementation`
**Version:** 003
**Author:** Prime Builder (antigravity, harness C)
**Session:** S509 (2026-06-09)
**Builds on:** `bridge/gtkb-github-ai-harness-ecosystem-advisory-2026-05-11-001.md` (Advisory adopted via work item WI-3304).

## Specification Links

- `GOV-FILE-BRIDGE-AUTHORITY-001` — File bridge protocol governance (config/governance/gov-file-bridge-authority-001.md)
- `DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001` — Implementation proposals must cite specs
- `DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001` — Verified proposals must have spec-to-test mapping
- `ADR-ISOLATION-APPLICATION-PLACEMENT-001` — Placement contract for application isolation
- `REQ-ECOSYSTEM-SCOUT-PROCEDURE` — Periodic public project scanner and capability review procedure.
- `REQ-CAPABILITY-IMPORT-POLICY` — Strict third-party provenance, license, security, and containment policy.
- `DELIB-S509-B1-B5-TRIAGE` — S509 triage deliberation.

## 2. Implementation Scope

- **Project:** `PROJECT-GTKB-PLATFORM-CORE`
- **Work Item:** `WI-3304` (Route LO advisory & adoption)
- **Requirement Sufficiency:** Existing requirements sufficient
- **target_paths:**
  - `docs/procedures/gtkb-ecosystem-scout.md`
  - `.claude/rules/gtkb-capability-import-policy.md`

All target paths reside under the project root (`E:\\GT-KB`), satisfying the in-root requirement of `ADR-ISOLATION-APPLICATION-PLACEMENT-001`.

## 3. Requirement Sufficiency

| Requirement | Source | Satisfied By | Test Coverage |
|-------------|--------|--------------|---------------|
| REQ-ECOSYSTEM-SCOUT-PROCEDURE | `bridge/gtkb-github-ai-harness-ecosystem-advisory-2026-05-11-001.md` | `docs/procedures/gtkb-ecosystem-scout.md` | Doc verification via validator script |
| REQ-CAPABILITY-IMPORT-POLICY | `bridge/gtkb-github-ai-harness-ecosystem-advisory-2026-05-11-001.md` | `.claude/rules/gtkb-capability-import-policy.md` | Doc verification via validator script |

## 4. Deliverables

### 4.1 Scout Procedure (`docs/procedures/gtkb-ecosystem-scout.md`)
- A standardized, machine-followable routine describing how to perform search, taxonomy classification, and analysis of public GitHub projects relevant to harness capabilities.
- Classification categories: `adopt`, `adapt`, `reject`, `defer`, or `monitor`.
- Explicit warning against installing or executing unverified third-party scripts.

### 4.2 Import Policy (`.claude/rules/gtkb-capability-import-policy.md`)
- Governance guidelines for third-party provenance checks, licensing validation (e.g., AGPL-3.0 compatibility), and security audits.
- Strict containment rules: no third-party mutation of GT-KB governance artifacts until explicitly authorized by owner.

## 5. Specification-Derived Verification Plan

As this is a documentation-only change, verification focuses on:
1. Link integrity and file paths check.
2. Compliance of the document with the project's glossary and syntax.
3. Doctor check validation.

### Automated Tests

- Verify documentation formatting and integrity by executing the project doctor:
  ```powershell
  groundtruth-kb\.venv\Scripts\gt.exe doctor
  ```

### Spec-to-Test Mapping

| Spec ID | Test File | Test Case(s) |
|---------|-----------|--------------|
| REQ-ECOSYSTEM-SCOUT-PROCEDURE | `groundtruth-kb/src/groundtruth_kb/project/doctor.py` | `gt doctor` documentation sweep |
| REQ-CAPABILITY-IMPORT-POLICY | `groundtruth-kb/src/groundtruth_kb/project/doctor.py` | `gt doctor` rule file compliance check |

## target_paths

- `docs/procedures/gtkb-ecosystem-scout.md`
- `.claude/rules/gtkb-capability-import-policy.md`

## Requirement Sufficiency

Existing requirements sufficient
