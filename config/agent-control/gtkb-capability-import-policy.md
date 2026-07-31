# GT-KB Capability Import Policy

Source: WI-3304 adoption of LO ecosystem advisory.

## 1. Third-Party Provenance and License Validation

Before any third-party package or repository is imported or integrated into the GT-KB platform:
1. **Provenance Check:** Validate the source repository's health, maintainer activity, security history, and release signatures.
2. **License Compatibility:** Ensure the license is compatible with the GT-KB commercial/private distribution model. Specifically:
   - Permissive licenses (MIT, Apache 2.0, BSD) are pre-approved.
   - AGPL-3.0 compatibility must be strictly verified. No hostile copyleft packages may be imported into execution-path products.
3. **Security Auditing:** Run vulnerability scans (e.g., `npm audit`, `pip-audit`, dependency checks) on all new dependencies.

## 2. Strict Containment and Isolation

> [!IMPORTANT]
> No third-party code, package, or tool may mutate GT-KB governance artifacts, rule files, or databases unless explicitly authorized by the owner via an approved work item and authorization packet.

- Third-party packages must run under strict security sandboxes.
- Network access by third-party packages must be blocked or isolated to authorized endpoints.
- Any tool, script, or package that requires system-wide permissions (outside the sandboxed directory) must be explicitly flagged and approved by the owner.
