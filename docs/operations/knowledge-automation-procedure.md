# Repeatable Procedure: Knowledge Automation Verification

> Verifies the Knowledge Automation system (KA-1 through KA-8) is functioning correctly.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.

---

## Procedure Identity

| Field | Value |
|-------|-------|
| **Procedure ID** | PROC-KA |
| **Version** | 1.0 |
| **Created** | 2026-02-20 |
| **Classification** | Functional verification |
| **Destructive** | No (creates KB articles; can be cleaned up) |
| **Prerequisites** | Active tenant with KB access; backend running |

## Pinned Variables

```
TENANT_ID       = remaker-digital-001
API_BASE        = https://agent-red-api-gateway.orangeglacier-f566a4e7.eastus.azurecontainerapps.io
SUPERADMIN_KEY  = ar_user_rema_qcHQpv0bhGwXpEou14WH3fnE_RZMvI_N
```

---

## Step 1: Verify Template System (KA-3)

**Action:** List available category templates.

```bash
curl -s -H "X-API-Key: ${SUPERADMIN_KEY}" \
  "${API_BASE}/api/admin/knowledge/templates" | python -m json.tool
```

**Expected:** JSON array with 10 template entries. Each entry has `id`, `name`, `description`, `articleCount`.

**Post-condition:** At least 10 templates returned, each with `articleCount > 0`.

---

## Step 2: Apply a Template (KA-3 + KA-2)

**Action:** Apply the "Apparel & Fashion" template.

```bash
curl -s -X POST -H "X-API-Key: ${SUPERADMIN_KEY}" \
  -H "Content-Type: application/json" \
  "${API_BASE}/api/admin/knowledge/templates/apparel_fashion/apply" | python -m json.tool
```

**Expected:** JSON response with `articlesCreated > 0`, `totalChars > 0`.

**Post-condition:** KB article count increased by the template's `articleCount`.

---

## Step 3: Verify Config Suggestions (KA-4)

**Action:** Fetch config suggestions generated from KB content.

```bash
curl -s -H "X-API-Key: ${SUPERADMIN_KEY}" \
  "${API_BASE}/api/admin/knowledge/suggestions" | python -m json.tool
```

**Expected:** JSON object with suggestion keys (e.g., `brand_name`, `brand_voice`, `escalation_keywords`, `greeting_message`, `widget_agent_display_name`). Each suggestion has `value`, `confidence` (0.0–1.0), `source`.

**Post-condition:** At least 2 suggestions returned with `confidence > 0.3`.

---

## Step 4: Verify Ingestion Job Status (KA-1 + KA-2)

**Action:** Check ingestion status for the tenant.

```bash
curl -s -H "X-API-Key: ${SUPERADMIN_KEY}" \
  "${API_BASE}/api/admin/knowledge/ingest/status" | python -m json.tool
```

**Expected:** JSON response. If no prior ingestion, returns null/empty. If a job exists, shows `status`, `articlesCreated`, `progressPercent`.

**Post-condition:** Endpoint responds with 200 OK.

---

## Step 5: Verify Customer Identification Mode (KA-5 + KA-8)

**Action:** Set identification mode to each value and verify persistence.

```bash
# Set to aggressive (saves to draft)
curl -s -X PUT -H "X-API-Key: ${SUPERADMIN_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"fields": {"customer_identification_mode": "aggressive"}}' \
  "${API_BASE}/api/config" | python -m json.tool

# Activate the draft (promotes draft to active)
curl -s -X POST -H "X-API-Key: ${SUPERADMIN_KEY}" \
  -H "Content-Type: application/json" -d '{}' \
  "${API_BASE}/api/config/draft/activate" | python -m json.tool

# Read back (reads active config)
curl -s -H "X-API-Key: ${SUPERADMIN_KEY}" \
  "${API_BASE}/api/config" | python -m json.tool | grep customer_identification_mode
```

**Expected:** Config save returns `state: "draft"`, activate returns `state: "active"`. Read-back shows `"customer_identification_mode": "aggressive"` inside the `config` object.

**Post-condition:** Field persists through save/activate/read cycle. Valid values: `off`, `gentle`, `standard`, `aggressive`.

---

## Step 6: Verify Admin UI Rendering (KA-7 + KA-8)

**Action:** Open the standalone admin UI and verify new sections render.

1. Navigate to Knowledge Base page → verify "Knowledge automation" section exists
2. Click "Show" → verify template selector grid renders with 10 templates
3. Verify IngestionPanel renders (even if no job exists — shows empty state)
4. Navigate to Configuration page → verify "Suggested" badges appear on empty fields
5. Navigate to Memory & Privacy page → verify "Customer identification" section with SegmentedControl

**Post-condition:** All 5 UI sections render without JavaScript errors.

---

## Step 7: End-to-End Template Apply (KA-3 + KA-7)

**Action:** Apply a template via the UI and verify articles appear.

1. In Knowledge Base → Knowledge automation → Show
2. Select "Beauty & Cosmetics" template
3. Click "Apply to knowledge base"
4. Verify success alert shows article count
5. Verify articles appear in the KB table
6. Navigate to Configuration page → verify suggestion badges update

**Post-condition:** Articles created match template `articleCount`. Suggestion badges appear on previously empty fields.

---

## Failure Classification

| Symptom | Classification | Action |
|---------|---------------|--------|
| Template list returns empty | Procedure defect | Verify `_registry.json` and template JSON files exist |
| Suggestion endpoint returns 500 | Environment transient | Check backend logs for KB repository errors |
| UI section doesn't render | Procedure defect | Check browser console for import/component errors |
| Ingestion job stuck in "running" | Environment transient | Check background loop in `background.py` logs |
| Config field doesn't persist | Procedure defect | Verify field registered in `tenant_config_schema.py` |

---

## Cleanup

To remove test articles created during verification:

```bash
# List articles and delete template-created ones
curl -s -H "X-API-Key: ${SUPERADMIN_KEY}" \
  "${API_BASE}/api/admin/knowledge" | python -m json.tool
# Delete specific articles by ID as needed
```

---

*Last updated: 2026-02-20*
