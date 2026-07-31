REVISED

Document: gtkb-wi5640-scanner-fixture-placeholder-sweep
Version: 003
Date: 2026-07-20
Author role: Prime Builder
Responds to: bridge/gtkb-wi5640-scanner-fixture-placeholder-sweep-002.md (NO-GO)
Preflight packet_hash: sha256:95430d7465f8eea0580dce1a2f7e1af25e2f35bf23027a97f2f4d769c8bd5ab3
Work Item: WI-5640

# WI-5640 — Secret-scanner fixture placeholder sweep (A+B)

This REVISED proposal corrects the four structural/governance defects in LO verdict 002 (FINDING-1..5). The substantive change is unchanged and was confirmed sound by LO.

## Specification Links

The following governing specifications constrain this implementation:

- GOV-FILE-BRIDGE-AUTHORITY-001
- DCL-IMPLEMENTATION-PROPOSAL-SPEC-LINKAGE-MANDATORY-001
- DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001
- ADR-ISOLATION-APPLICATION-PLACEMENT-001
- GOV-ARTIFACT-ORIENTED-GOVERNANCE-001
- ADR-ARTIFACT-ORIENTED-DEVELOPMENT-001
- DCL-ARTIFACT-LIFECYCLE-TRIGGERS-001
- .claude/rules/file-bridge-protocol.md
- .claude/rules/project-root-boundary.md

Precedent (non-governing, cited in prose): WI-4880 and owner deliberation DELIB-20266274 establish the `# placeholder` marker as the codebase-standard suppression mechanism.

## Implementation-Start Authorization Metadata

target_paths: ["groundtruth-kb/tests/test_cli_deliberations.py", "applications/Agent_Red/tests/test_host/test_build_contract.py", "platform_tests/scripts/test_cloud_harness_base.py", "bridge/gtkb-wi5410-semantic-only-test-double-contract-004.md"]

### Requirement Sufficiency

Existing requirements sufficient. The requirement — suppress pre-existing scanner false-positive fixtures using the established `# placeholder` mechanism — is fully defined by WI-4880 and DELIB-20266274; no new or revised requirement is needed before implementation.

### Files Expected To Change

- groundtruth-kb/tests/test_cli_deliberations.py
- applications/Agent_Red/tests/test_host/test_build_contract.py
- platform_tests/scripts/test_cloud_harness_base.py
- bridge/gtkb-wi5410-semantic-only-test-double-contract-004.md

## 1. Problem statement

The local pre-commit hook (.githooks/pre-commit -> scripts/scan_secrets.py --staged) blocks git commit when a staged change touches four files containing pre-existing test fixtures that match secret patterns. None are real credentials. Running the scanner against the four files yields exactly 10 findings:

| # | File | Line | Sev | Pattern |
|---|------|------|-----|---------|
| 1 | groundtruth-kb/tests/test_cli_deliberations.py | 181 | HIGH | AWS Access Key |
| 2 | groundtruth-kb/tests/test_cli_deliberations.py | 181 | MEDIUM | Secret Key Assignment |
| 3 | applications/Agent_Red/tests/test_host/test_build_contract.py | 634 | MEDIUM | Secret Key Assignment |
| 4 | applications/Agent_Red/tests/test_host/test_build_contract.py | 661 | MEDIUM | Secret Key Assignment |
| 5 | platform_tests/scripts/test_cloud_harness_base.py | 447 | MEDIUM | Secret Key Assignment |
| 6 | platform_tests/scripts/test_cloud_harness_base.py | 449 | MEDIUM | Bearer Token |
| 7 | bridge/gtkb-wi5410-semantic-only-test-double-contract-004.md | 72 | HIGH | AWS Access Key |
| 8 | bridge/gtkb-wi5410-semantic-only-test-double-contract-004.md | 72 | MEDIUM | Secret Key Assignment |
| 9 | bridge/gtkb-wi5410-semantic-only-test-double-contract-004.md | 103 | HIGH | AWS Access Key |
| 10 | bridge/gtkb-wi5410-semantic-only-test-double-contract-004.md | 103 | MEDIUM | Secret Key Assignment |

## 2. Root cause

All ten are intentional, non-secret test fixtures or documentation quotes. The scanner skip list (scan_file ~L220-240) skips any line whose lowercased stripped text contains a marker such as placeholder. These fixture lines pre-date the scanner and carry no marker.

## 3. Proposed change (minimal, additive, non-breaking)

Append the codebase-standard placeholder marker. For Python source lines this is a trailing comment (does not alter the string value, so in-based substring assertions and the env-file content written by the fixture are unchanged). For the two .md documentation-quote lines, append a parenthetical (placeholder) so the marker substring is present.

### 3.1 groundtruth-kb/tests/test_cli_deliberations.py line 181
-        secret = "AKIAIOSFODNN7EXAMPLE"
+        secret = "AKIAIOSFODNN7EXAMPLE"  # placeholder

### 3.2 applications/Agent_Red/tests/test_host/test_build_contract.py lines 634, 661
-        source.write_text("VITE_API_BASE=/api\nAGENT_RED_TEST_SECRET=super-secret-value\n", encoding="utf-8")
+        source.write_text("VITE_API_BASE=/api\nAGENT_RED_TEST_SECRET=super-secret-value\n", encoding="utf-8")  # placeholder
-            assert "AGENT_RED_TEST_SECRET=super-secret-value" in target.read_text(encoding="utf-8")
+            assert "AGENT_RED_TEST_SECRET=super-secret-value" in target.read_text(encoding="utf-8")  # placeholder

### 3.3 platform_tests/scripts/test_cloud_harness_base.py lines 447, 449
-            "message": "named selector rejected; api_key=abcdefghijklmnop" + " x" * 400,
+            "message": "named selector rejected; api_key=abcdefghijklmnop" + " x" * 400,  # placeholder
-            "authorization": "Bearer ignored-authorization-sentinel",
+            "authorization": "Bearer ignored-authorization-sentinel",  # placeholder

### 3.4 bridge/gtkb-wi5410-semantic-only-test-double-contract-004.md lines 72, 103
-   secret = "AKIAIOSFODNN7EXAMPLE" inside test_add_content_file_redaction,
+   secret = "AKIAIOSFODNN7EXAMPLE" inside test_add_content_file_redaction, (placeholder)
--        secret = "AKIAIOSFODNN7EXAMPLE"
+-        secret = "AKIAIOSFODNN7EXAMPLE"   # (placeholder)

## 4. Why annotation (not rotation / removal / scanner change)

- No real credentials exist; there is nothing to rotate. The fixtures are load-bearing test inputs.
- Removal breaks tests; the assertions depend on these exact fixture strings.
- Scanner change is out of scope; modifying scan_secrets.py would weaken detection for real secrets.
- Annotation is the established precedent (WI-4880 + DELIB-20266274).

## 5. Specification-Derived Verification Plan

Per DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001, the verification below maps each linked requirement to a concrete command:

1. ADR-ISOLATION-APPLICATION-PLACEMENT-001 / project root boundary — all four target_paths are inside E:/GT-KB and respect the applications/ boundary; confirmed by the path list in Implementation-Start Authorization Metadata.
2. DCL-VERIFIED-SPEC-DERIVED-TESTING-MANDATORY-001 — re-run the staged scanner after edits and confirm zero findings:
   python scripts/scan_secrets.py --staged   (expect: Found 0 potential secret(s))
3. GOV-FILE-BRIDGE-AUTHORITY-001 — no mutation occurs until a live GO verdict is recorded for this thread.
4. Regression check — run the touched test modules:
   python -m pytest groundtruth-kb/tests/test_cli_deliberations.py applications/Agent_Red/tests/test_host/test_build_contract.py platform_tests/scripts/test_cloud_harness_base.py -q --tb=short
   (The Agent Red suite may still hit the pre-existing jwt ModuleNotFoundError environment issue noted in WI-5381; that is external to this change.)
5. Lint/format on the three touched .py files:
   python -m ruff check <files> && python -m ruff format --check <files>

## 6. Files touched (all PROTECTED — mutation gated on GO)

- groundtruth-kb/tests/test_cli_deliberations.py
- applications/Agent_Red/tests/test_host/test_build_contract.py
- platform_tests/scripts/test_cloud_harness_base.py
- bridge/gtkb-wi5410-semantic-only-test-double-contract-004.md

## 7. Risk / impact

- Severity: low. Pure additive comment/doc-text annotations; no runtime behavior change.
- Reversibility: trivially revertible (comment removal).
- Blast radius: none beyond the four files.

## 8. Work-item note (FINDING-4)

WI-5640 is referenced by this bridge thread. MemBase creation via backlog add is blocked in this session by a resolve_changed_by provenance error; per the LO verdict's own alternative, WI-5640 will be created in MemBase at implementation start (backlog add) and linked to this thread. This is a P3 informational item and does not block GO.

## 9. Decision requested

GO / NO-GO on applying the four placeholder-annotation edits above.

---
*(c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.*
