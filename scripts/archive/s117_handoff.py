"""Generate S117 handoff prompt.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys

sys.path.insert(0, "tools/knowledge-db")
import db  # noqa: E402

kdb = db.KnowledgeDB()

prompt = """Continue work on Agent Red Customer Experience commercial project.
Location: E:\\Claude-Playground\\CLAUDE-PROJECTS\\Agent Red Customer Engagement
Key files: CLAUDE.md, memory/MEMORY.md
Session: S118 (previous: S117)

## S117 Summary

Feature backlog triage + GOV-10 governance + targeting rules specs.

**Key outcomes:**
1. **Feature backlog:** 55 WIs (WI-0771..0825) populated, batch-investigated, 35 resolved (65% already implemented). 20 remain open.
2. **GOV-10 enacted:** Tests must exercise exposed production interfaces (API, SSE, Playwright). Source inspection tests are regression supplements only. Tests written BEFORE implementation.
3. **WI-0771 implemented:** Customer context pre-computation warm_up() call site in endpoints.py. WI-0826 tracks missing GOV-10 live test.
4. **Targeting rules cluster (WI-0813..0816):** Critical bug — shouldShowOnPage() doesn't parse +/- prefixes. Plan approved. Phase 1 COMPLETE (5 specs SPEC-1504..1508, 9 test artifacts TEST-2677..2685). Phases 2-4 pending.
5. **162 source inspection tests** across 4 new files, all PASS. 1 product code change (endpoints.py). No build/deploy.

## S118 Priority: Continue Targeting Rules Implementation

The approved plan is at: C:\\Users\\micha\\.claude\\plans\\swift-gathering-thimble.md

**Next steps (Phases 2-4):**
- Phase 2: Write live E2E test CODE for TEST-2677..2685 (config pipeline httpx tests + admin UI Playwright tests)
- Phase 3: Implementation (fix shouldShowOnPage, admin UI page rules, 4-layer pipeline for exit-intent + scroll-depth, trigger listeners, admin trigger controls)
- Phase 4: Execute tests — all must PASS

**Key files to modify:**
- widget/src/index.ts — shouldShowOnPage() rewrite + trigger listeners
- widget/src/theme/tokens.ts — WidgetConfig type additions
- admin/standalone/pages/Widget.tsx — page rules UI + trigger controls
- src/multi_tenant/schema/fields.yaml — 2 new field definitions
- src/multi_tenant/config/field_mapping.py — 2 fields to _PREFS_DIRECT_FIELDS
- src/multi_tenant/cosmos_schema.py — 2 fields on PreferencesDocument
- tests/security/test_config_pipeline_live.py — 4 new live API tests
- tests/e2e_live/test_widget_live.py — 5 new live admin UI tests

**After targeting rules:** Continue item-by-item review of remaining 16 backlog items (items 3-20).

## KB State
- 1,681 specs (232 verified, 759 implemented, 686 specified, 4 retired)
- 2,685 test artifacts, 826 work items (20 open)
- 80 assertions (75 PASS, 5 FAIL — targeting specs expected)
- Uncommitted changes: CLAUDE.md, endpoints.py, knowledge.db, 7 new files

## Uncommitted Files (commit triage needed — S120 audit session)
Modified: CLAUDE.md, src/chat/endpoints.py, tests/widget/test_widget_core.py, tools/knowledge-db/knowledge.db, .gitignore
New: scripts/populate_feature_backlog.py, scripts/resolve_batch_wis_s117.py, scripts/record_targeting_specs_s117.py, tests/widget/test_admin_features_batch.py, tests/widget/test_admin_tooltips.py, tests/widget/test_admin_ui_labels.py, tests/widget/test_warm_up_call_site.py
"""

kdb.insert_session_prompt(
    session_id="S117",
    prompt_text=prompt.strip(),
)

print("S117 handoff prompt recorded.")
