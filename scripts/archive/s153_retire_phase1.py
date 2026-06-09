"""S153 Phase 1 — Retire contradicted, WI approvals, and business/creative specs as OBSOLETE.

Per owner directive: these categories are not specifications and should be removed
from future consideration.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import sys

sys.path.insert(0, "tools/knowledge-db")
from db import KnowledgeDB

db = KnowledgeDB()

SESSION = "S153"

# =============================================================================
# Category 1: CONTRADICTED BY IMPLEMENTATION (37 specs)
# Implementation deliberately differs from what the spec requires.
# =============================================================================
contradicted = {
    "SPEC-0006": "No purchase button exists in widget — cannot hover on non-existent element",
    "SPEC-0021": "Conversation view AI label uses warm stone palette, not lighter grey",
    "SPEC-0025": "Integration logos are 180x180px, not 150px (IntegrationsManager.tsx)",
    "SPEC-0056": "Pages use diverse layouts, not uniform scroll-down workflow",
    "SPEC-0084": "Logo uses primary-logo-no-wordmark.svg, not primary-logo-light/dark.svg",
    "SPEC-0089": "Chat bg is #1c1917 (warm stone), not #19191A (cold grey)",
    "SPEC-0090": "Border is #44403c (warm stone), not #363636 (cold grey)",
    "SPEC-0132": "Pages use multi-column layout, not single column",
    "SPEC-0140": "Sidebar order differs — no Setup wizard item, Memory & Privacy present",
    "SPEC-0142": "OnboardingWizard has 3 steps, not 8",
    "SPEC-0143": "Test mode field restrictions not implemented in wizard",
    "SPEC-0144": "Go-live checklist not implemented in test mode",
    "SPEC-0146": "No welcome pop-up when system is inactive",
    "SPEC-0147": "Inactive indicator does not navigate to wizard on click",
    "SPEC-0236": "Assign-to-agent deliberately kept in inbox UI",
    "SPEC-0243": "Auto-open behavior deliberately retained in widget",
    "SPEC-0244": "Offline form deliberately retained in widget",
    "SPEC-0315": "Wizard deliberately kept as OnboardingWizard (3-step, serves setup + test mode)",
    "SPEC-0316": "Test mode deliberately kept as core wizard feature (Step 1 toggle)",
    "SPEC-0367": "seed_tenant.py initializes with empty escalation keywords, not 9 defaults",
    "SPEC-0373": "Sidebar uses single primary-logo-no-wordmark.svg, not dark/light variants",
    "SPEC-0374": "NEW-BLOCK-LOGO-HORIZONTAL-LIGHT.svg does not exist in branding assets",
    "SPEC-0375": "NEW-BLOCK-LOGO-HORIZONTAL-DARK.svg does not exist in branding assets",
    "SPEC-0390": "Layout renders separate 'Customer Experience' text next to logo — logo has no wordmark",
    "SPEC-0518": "Storefront margin is mb={4} (16px Mantine), not 40px",
    "SPEC-0519": "Storefront text is smaller than Dashboard heading, not matching",
    "SPEC-0532": "Integration logos are 180x180px, not 260px",
    "SPEC-0562": "Saved configurations section deliberately retained in Configuration page",
    "SPEC-0567": "Cross-session learning tooltip not present on pricing features page",
    "SPEC-0568": "Dedicated model training tooltip not present on pricing features page",
    "SPEC-0586": "No widget toggle control exists — widget visibility gated on is_active",
    "SPEC-0616": "Widget activation deliberately requires is_active gate, not auto-enabled",
    "SPEC-0679": "primary-logo-dark/light SVG+PNG files do not exist — only icon-master and no-wordmark",
    "SPEC-0680": "primary-logo-dark file does not exist in branding assets",
    "SPEC-0681": "primary-logo-light file does not exist in branding assets",
    "SPEC-0682": "primary-logo-light.svg does not exist — cannot have SVG comment",
    "SPEC-1632": "Email card uses 16px padding/margin, not 50px",
}

# =============================================================================
# Category 2: WI APPROVALS (20 specs)
# These are approvals for work items, not code specifications.
# =============================================================================
wi_approvals = {
    "SPEC-0325": "WI approval record, not a specification",
    "SPEC-0326": "WI approval record, not a specification",
    "SPEC-0327": "WI approval record, not a specification",
    "SPEC-0328": "WI approval record, not a specification",
    "SPEC-0329": "WI approval record, not a specification",
    "SPEC-0330": "WI approval record, not a specification",
    "SPEC-0331": "WI approval record, not a specification",
    "SPEC-0332": "WI approval record, not a specification",
    "SPEC-0333": "WI approval record, not a specification",
    "SPEC-0334": "WI approval record, not a specification",
    "SPEC-0335": "WI approval record, not a specification",
    "SPEC-0336": "WI approval record, not a specification",
    "SPEC-0337": "WI approval record, not a specification",
    "SPEC-0348": "WI approval record, not a specification",
    "SPEC-0349": "WI delegation record, not a specification",
    "SPEC-0394": "WI approval record, not a specification",
    "SPEC-0395": "WI approval record, not a specification",
    "SPEC-0396": "WI approval record, not a specification",
    "SPEC-0397": "WI approval record, not a specification",
    "SPEC-0398": "WI approval record, not a specification",
}

# =============================================================================
# Category 3: BUSINESS/CREATIVE DECISIONS (26 specs)
# Pricing, competitive references, creative direction — not code specifications.
# =============================================================================
business_creative = {
    "SPEC-0079": "Business decision — competitive positioning target (Tidio), not code spec",
    "SPEC-0080": "Business decision — UX polish target (Tidio), not code spec",
    "SPEC-0083": "Business decision — pricing orthogonal to release scope",
    "SPEC-0200": "Creative reference — Hugo chat UI as functional reference",
    "SPEC-0204": "Business decision — beta tenant provisioning names",
    "SPEC-0208": "Creative reference — Tidio as primary functional reference",
    "SPEC-0209": "Creative reference — Zapier as visual styling reference",
    "SPEC-0253": "Business decision — upsell presentation pattern",
    "SPEC-0260": "Business direction — iterative chat quality improvement",
    "SPEC-0350": "Creative asset — Shopify merchant category images",
    "SPEC-0431": "Business decision — 1.0 as full GA release",
    "SPEC-0434": "Business decision — affiliate revenue deferred",
    "SPEC-0464": "Creative asset — color palette worksheet for designer",
    "SPEC-0465": "Business decision — dual-purpose Remaker Digital storefront",
    "SPEC-0660": "Business decision — 50% lower pricing target",
    "SPEC-0663": "Business decision — itemized pricing structure (Option C)",
    "SPEC-0739": "Business decision — roadmap priority ordering",
    "SPEC-0794": "Business decision — dedicated model training deferred to post-launch",
    "SPEC-0795": "Business decision — Rewardful affiliate integration",
    "SPEC-0796": "Business decision — Rewardful requires Stripe live mode",
    "SPEC-0804": "Business analysis — platform market size assessment",
    "SPEC-0809": "Business decision — evaluation priority criteria",
    "SPEC-0810": "Business decision — communication guidelines (avoid generalizations)",
    "SPEC-0824": "Creative asset — category images for merchant verticals",
    "SPEC-0861": "Business decision — AI greeting moved to Group 3",
    "203": "Business decision — UX consultant evaluation (Mazel)",
}

# =============================================================================
# Execute retirements
# =============================================================================
total = 0

print("=" * 60)
print("CATEGORY 1: CONTRADICTED BY IMPLEMENTATION")
print("=" * 60)
for sid, reason in contradicted.items():
    db.update_spec(
        sid,
        changed_by=SESSION,
        change_reason=f"OBSOLETE — Contradicted by implementation: {reason}",
        status="retired",
    )
    print(f"  Retired {sid}")
    total += 1
print(f"  Subtotal: {len(contradicted)} specs retired\n")

print("=" * 60)
print("CATEGORY 2: WI APPROVALS")
print("=" * 60)
for sid, reason in wi_approvals.items():
    db.update_spec(
        sid,
        changed_by=SESSION,
        change_reason=f"OBSOLETE — {reason}. Owner directive: WI approvals are not specifications.",
        status="retired",
    )
    print(f"  Retired {sid}")
    total += 1
print(f"  Subtotal: {len(wi_approvals)} specs retired\n")

print("=" * 60)
print("CATEGORY 3: BUSINESS/CREATIVE DECISIONS")
print("=" * 60)
for sid, reason in business_creative.items():
    db.update_spec(
        sid,
        changed_by=SESSION,
        change_reason=f"OBSOLETE — {reason}. Owner directive: business/creative decisions should not be specs.",
        status="retired",
    )
    print(f"  Retired {sid}")
    total += 1
print(f"  Subtotal: {len(business_creative)} specs retired\n")

print("=" * 60)
print(f"TOTAL RETIRED: {total} specs")
print("=" * 60)
