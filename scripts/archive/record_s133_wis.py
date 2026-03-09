"""Record S133 work items for SPEC-1649/1650/1651 - Master Test Plan live-only enforcement."""
import sys
sys.path.insert(0, 'tools/knowledge-db')
import db

kdb = db.KnowledgeDB()

# Supersede WI-1015..1017 (scoped to Phase 12 only) — now replaced by broader phase-specific WIs
for wid in ['WI-1015', 'WI-1016', 'WI-1017']:
    wi = kdb.get_work_item(wid)
    kdb.insert_work_item(
        id=wid,
        title=wi['title'] + ' [SUPERSEDED by WI-1019..1026]',
        origin=wi['origin'],
        component=wi['component'],
        resolution_status='resolved',
        changed_by='S133',
        change_reason='Superseded: SPEC-1649 expanded to all phases. Replaced by phase-specific WIs.',
        description=wi.get('description', ''),
        source_spec_id='SPEC-1649',
        stage='resolved'
    )
    print(f'{wid} superseded')

print()

# Phase 2: Unit & Integration (22,109 MOCKED_UNIT tests)
kdb.insert_work_item(
    id='WI-1019',
    title='Remove Phase 2 (Unit & Integration) from PLAN-001',
    origin='new',
    component='test_plan',
    resolution_status='open',
    changed_by='S133',
    change_reason='SPEC-1649: All mocked tests removed from Master Test Plan.',
    description=(
        'Phase 2 contains 22,109 MOCKED_UNIT tests (tests/multi_tenant, tests/unit, tests/agents, '
        'tests/chat, tests/integrations). Remove from PLAN-001. These tests remain available via '
        'thermal-safe harness for localhost pre-deployment testing (SPEC-1650).'
    ),
    source_spec_id='SPEC-1649',
    stage='created'
)
print('WI-1019 created: Remove Phase 2')

# Phase 4: External URL Reachability (4 MOCKED_UNIT tests in tests/ops/)
kdb.insert_work_item(
    id='WI-1020',
    title='Remove Phase 4 mocked tests, replace with live URL checks',
    origin='new',
    component='test_plan',
    resolution_status='open',
    changed_by='S133',
    change_reason='SPEC-1649: Replace tests/ops/ mocked tests with live reachability checks.',
    description=(
        'Phase 4 contains 4 tests from tests/ops/ (MOCKED_UNIT). Remove and replace with live '
        'HTTP HEAD/GET requests against actual external URLs (docs site, API gateway health, '
        'Shopify app listing). Pre-flight already does some of this — consolidate.'
    ),
    source_spec_id='SPEC-1649',
    stage='created'
)
print('WI-1020 created: Phase 4 replacement')

# Phase 10: Load Testing (22 MOCKED_UNIT tests)
kdb.insert_work_item(
    id='WI-1021',
    title='Remove Phase 10 mocked load tests, replace with live Locust execution',
    origin='new',
    component='test_plan',
    resolution_status='open',
    changed_by='S133',
    change_reason='SPEC-1649: Replace mocked load test assertions with actual Locust load test.',
    description=(
        'Phase 10 contains 22 MOCKED_UNIT tests (test_concurrent_tenants.py, test_keda_scaling.py). '
        'Remove and replace with actual Locust load test execution against staging '
        '(locust-staging.conf already exists from S123). Live load test verifies real latency, '
        'throughput, and error rates.'
    ),
    source_spec_id='SPEC-1649',
    stage='created'
)
print('WI-1021 created: Phase 10 replacement')

# Phase 11: Conversation Quality (42 MOCKED_UNIT tests)
kdb.insert_work_item(
    id='WI-1022',
    title='Remove Phase 11 mocked conversation tests, replace with live conversation flow',
    origin='new',
    component='test_plan',
    resolution_status='open',
    changed_by='S133',
    change_reason='SPEC-1649: Replace mocked conversation quality tests with live API calls.',
    description=(
        'Phase 11 contains 42 MOCKED_UNIT tests. Remove and replace with live tests that: '
        '(1) start a conversation via widget API, (2) send messages, (3) verify AI responses, '
        '(4) check conversation appears in admin inbox. Tests must call real staging endpoints.'
    ),
    source_spec_id='SPEC-1651',
    stage='created'
)
print('WI-1022 created: Phase 11 replacement')

# Phase 12: UI Regression (560 MOCKED_UI tests)
kdb.insert_work_item(
    id='WI-1023',
    title='Remove Phase 12 mocked UI tests, expand live E2E to cover all admin pages',
    origin='new',
    component='test_plan',
    resolution_status='open',
    changed_by='S133',
    change_reason='SPEC-1649/SPEC-1651: Replace 521 mocked Playwright tests with live tests.',
    description=(
        'Phase 12 contains 560 MOCKED_UI tests (tests/e2e/ — Playwright with local Vite + route '
        'interception). Remove entirely. Expand tests/e2e_live/ (currently 90 tests) to cover all '
        'admin pages: dashboard, configuration, team, inbox, analytics, billing, knowledge base, '
        'memory/privacy, quick actions, integrations, widget config, widget preview. Each page must '
        'have live tests verifying content loads from real API.'
    ),
    source_spec_id='SPEC-1649',
    stage='created'
)
print('WI-1023 created: Phase 12 replacement')

# Phase 13: KB Assertions (108 tests — mix of live SPA + SOURCE_INSPECTION)
kdb.insert_work_item(
    id='WI-1024',
    title='Remove Phase 13 KB assertion checks, retain live SPA provisioning tests',
    origin='new',
    component='test_plan',
    resolution_status='open',
    changed_by='S133',
    change_reason='SPEC-1649: Remove source inspection KB assertions from PLAN-001.',
    description=(
        'Phase 13 currently combines: (a) 26 live config pipeline E2E tests (LIVE_API — KEEP), '
        '(b) ~82 KB assertion checks that read source files (SOURCE_INSPECTION — REMOVE). '
        'Split phase: keep the 26 live tests, remove the KB assertion runner from PLAN-001. '
        'KB assertions remain a development-time tool.'
    ),
    source_spec_id='SPEC-1649',
    stage='created'
)
print('WI-1024 created: Phase 13 split')

# Phase 15: Manual Verification (3 SOURCE_INSPECTION tests)
kdb.insert_work_item(
    id='WI-1025',
    title='Remove Phase 15 source inspection tests, replace with live verification',
    origin='new',
    component='test_plan',
    resolution_status='open',
    changed_by='S133',
    change_reason='SPEC-1649: Replace source inspection with live external checks.',
    description=(
        'Phase 15 contains 3 SOURCE_INSPECTION tests (manual verification). Remove and replace '
        'with live verification: check that docs site is reachable, GitHub wiki pages load, or '
        'equivalent external checks.'
    ),
    source_spec_id='SPEC-1649',
    stage='created'
)
print('WI-1025 created: Phase 15 replacement')

# Phase 16: Widget Visual Regression (50 tests — SOURCE_INSPECTION + VISUAL_WIDGET)
kdb.insert_work_item(
    id='WI-1026',
    title='Remove Phase 16 widget source/visual tests, replace with live widget E2E',
    origin='new',
    component='test_plan',
    resolution_status='open',
    changed_by='S133',
    change_reason='SPEC-1649/SPEC-1651: Replace widget source/visual tests with live widget tests.',
    description=(
        'Phase 16 contains tests from tests/widget/ (753 SOURCE_INSPECTION) + tests/visual/ '
        '(38 VISUAL_WIDGET). Remove from PLAN-001. Replace with live widget tests that: load '
        'widget on staging storefront or via direct staging URL, verify widget renders, opens, '
        'accepts input, sends messages, and displays responses through the real API.'
    ),
    source_spec_id='SPEC-1649',
    stage='created'
)
print('WI-1026 created: Phase 16 replacement')

print()
print('All 8 phase-specific WIs created (WI-1019..WI-1026)')
print('3 prior WIs superseded (WI-1015..WI-1017)')
