"""Record S133 test artifacts for SPEC-1649/1650/1651 (GOV-12) and assign to phases (GOV-13)."""
import sys
sys.path.insert(0, 'tools/knowledge-db')
import db

kdb = db.KnowledgeDB()

# Test artifacts for SPEC-1649 (Master Test Plan must use only live external interfaces)
tests_1649 = [
    ('TEST-2956', 'SPEC-1649', 'A1', 'Every test in every PLAN-001 phase verifies behavior through live external interfaces', 'requirement'),
    ('TEST-2957', 'SPEC-1649', 'A2', 'No PLAN-001 phase contains mocked API, stub, code inspection, or source-reading tests', 'requirement'),
    ('TEST-2958', 'SPEC-1649', 'A3', 'tests/e2e/ directory is not referenced in any PLAN-001 phase test_ids', 'requirement'),
    ('TEST-2959', 'SPEC-1649', 'A4', 'tests/widget/ directory is not referenced in any PLAN-001 phase test_ids', 'requirement'),
    ('TEST-2960', 'SPEC-1649', 'A5', 'tests/visual/ directory is not referenced in any PLAN-001 phase test_ids', 'requirement'),
    ('TEST-2961', 'SPEC-1649', 'A6', 'tests/ops/ directory is not referenced in any PLAN-001 phase test_ids', 'requirement'),
    ('TEST-2962', 'SPEC-1649', 'A7', 'Phase 2 unit/integration mocked tests are not in any PLAN-001 phase', 'requirement'),
    ('TEST-2963', 'SPEC-1649', 'A8', 'KB assertion checks (source inspection) are not in any PLAN-001 phase', 'requirement'),
    ('TEST-2964', 'SPEC-1649', 'A9', 'All code paths from removed tests have equivalent live interface coverage', 'requirement'),
]

# Test artifacts for SPEC-1650 (Retained mocked tests for localhost)
tests_1650 = [
    ('TEST-2965', 'SPEC-1650', 'A1', 'tests/e2e/, tests/widget/, tests/visual/, tests/ops/ directories exist in repository', 'requirement'),
    ('TEST-2966', 'SPEC-1650', 'A2', 'tests/multi_tenant/, tests/unit/, tests/agents/, tests/chat/, tests/integrations/ directories exist', 'requirement'),
    ('TEST-2967', 'SPEC-1650', 'A3', 'No test file deleted as part of SPEC-1649 implementation', 'requirement'),
    ('TEST-2968', 'SPEC-1650', 'A4', 'Thermal-safe harness can still execute mocked tests for local development', 'requirement'),
]

# Test artifacts for SPEC-1651 (E2E tests must flex all production code paths)
tests_1651 = [
    ('TEST-2969', 'SPEC-1651', 'A1', 'Every admin UI page has at least one live E2E test against staging', 'requirement'),
    ('TEST-2970', 'SPEC-1651', 'A2', 'Every API endpoint has at least one live test against staging', 'requirement'),
    ('TEST-2971', 'SPEC-1651', 'A3', 'Widget functionality verified by loading widget against staging', 'requirement'),
    ('TEST-2972', 'SPEC-1651', 'A4', 'New live tests created for code paths previously covered only by mocked tests', 'requirement'),
    ('TEST-2973', 'SPEC-1651', 'A5', 'All live tests pass against current staging deployment', 'requirement'),
]

all_tests = tests_1649 + tests_1650 + tests_1651
for test_id, spec_id, assertion_id, description, test_type in all_tests:
    kdb.insert_test(
        id=test_id,
        title=description,
        spec_id=spec_id,
        test_type=test_type,
        expected_outcome=f'{assertion_id}: PASS when verified against live PLAN-001 execution',
        changed_by='S133',
        change_reason=f'GOV-12: test creation triggered by WI creation for {spec_id}',
        description=f'Assertion {assertion_id} from {spec_id}. {description}',
    )
    print(f'{test_id} created ({spec_id}:{assertion_id})')

print(f'\n{len(all_tests)} test artifacts created (TEST-2956..TEST-2973)')

# GOV-13: Assign all new tests to PLAN-001 phases
# These tests verify the test plan structure itself, so assign to Phase 1 (Pre-flight)
import json
phase = kdb.list_test_plan_phases('PLAN-001')
phase_1 = [p for p in phase if p['id'] == 'PHASE-001'][0]
existing_ids = json.loads(phase_1['test_ids']) if phase_1['test_ids'] else []
new_ids = [t[0] for t in all_tests]
combined = existing_ids + new_ids

kdb.update_test_plan_phase(
    id='PHASE-001',
    changed_by='S133',
    change_reason='GOV-13: Assign SPEC-1649/1650/1651 test artifacts to Phase 1 (pre-flight verification)',
    test_ids=json.dumps(combined)
)
print(f'\nPhase 1 updated: {len(existing_ids)} -> {len(combined)} tests')
