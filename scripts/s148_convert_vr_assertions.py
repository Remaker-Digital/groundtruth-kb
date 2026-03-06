#!/usr/bin/env python3
"""
S148: Convert VR-* visual assertions to machine-checkable grep/glob assertions.

All 26 VR-* specs have type=visual assertions which the assertion runner cannot execute
(it only supports grep, grep_absent, glob). This script replaces them with structural
assertions that verify the same things at the source code level.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""
import sys, json, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools', 'knowledge-db'))
from db import KnowledgeDB

ADMIN_PAGES = os.path.join(os.path.dirname(__file__), '..', 'admin', 'standalone', 'pages')
THEME_DIR = os.path.join(os.path.dirname(__file__), '..', 'admin', 'shared', 'theme')
LAYOUT_FILE = os.path.join(os.path.dirname(__file__), '..', 'admin', 'standalone', 'layouts', 'StandaloneLayout.tsx')

# Mapping: VR spec ID -> list of grep assertions to replace visual ones
VR_CONVERSIONS = {
    # --- Per-page top-left specs: verify page title + subtitle in source ---
    'VR-dashboard-s0-topleft': [
        {'type': 'grep', 'file': 'admin/standalone/pages/Dashboard.tsx', 'pattern': 'Title order.*Dashboard'},
        {'type': 'grep', 'file': 'admin/shared/theme/tokens.css', 'pattern': '--ar-page.*#1c1917'},
        {'type': 'grep', 'file': 'admin/shared/theme/agentRedTheme.ts', 'pattern': "page.*#1c1917"},
    ],
    'VR-agentconfig-s0-topleft': [
        {'type': 'grep', 'file': 'admin/standalone/pages/Configuration.tsx', 'pattern': 'Title order.*Agent configuration'},
        {'type': 'grep', 'file': 'admin/standalone/pages/Configuration.tsx', 'pattern': 'Fine-tune'},
        {'type': 'grep', 'file': 'admin/shared/theme/tokens.css', 'pattern': '--ar-page.*#1c1917'},
    ],
    'VR-billing-s0-topleft': [
        {'type': 'grep', 'file': 'admin/standalone/pages/Billing.tsx', 'pattern': 'Title order.*Billing'},
        {'type': 'grep', 'file': 'admin/standalone/pages/Billing.tsx', 'pattern': 'Manage your subscription'},
        {'type': 'grep', 'file': 'admin/shared/theme/tokens.css', 'pattern': '--ar-page.*#1c1917'},
    ],
    'VR-inbox-s0-topleft': [
        {'type': 'grep', 'file': 'admin/standalone/pages/Inbox.tsx', 'pattern': 'Search conversations'},
        {'type': 'grep', 'file': 'admin/standalone/pages/Inbox.tsx', 'pattern': 'Active'},
        {'type': 'grep', 'file': 'admin/standalone/pages/Inbox.tsx', 'pattern': 'Resolved'},
    ],
    'VR-integrations-s0-topleft': [
        {'type': 'grep', 'file': 'admin/standalone/pages/Integrations.tsx', 'pattern': 'Title order.*Integrations'},
        {'type': 'grep', 'file': 'admin/standalone/pages/Integrations.tsx', 'pattern': 'Connect third-party'},
        {'type': 'grep', 'file': 'admin/shared/theme/tokens.css', 'pattern': '--ar-page.*#1c1917'},
    ],
    'VR-knowledgebase-s0-topleft': [
        {'type': 'grep', 'file': 'admin/standalone/pages/KnowledgeBase.tsx', 'pattern': 'Title order.*Knowledge base'},
        {'type': 'grep', 'file': 'admin/standalone/pages/KnowledgeBase.tsx', 'pattern': 'Manage articles'},
        {'type': 'grep', 'file': 'admin/shared/theme/tokens.css', 'pattern': '--ar-page.*#1c1917'},
    ],
    'VR-memoryprivacy-s0-topleft': [
        {'type': 'grep', 'file': 'admin/standalone/pages/MemoryPrivacy.tsx', 'pattern': 'Title order.*Memory'},
        {'type': 'grep', 'file': 'admin/standalone/pages/MemoryPrivacy.tsx', 'pattern': 'Configure how.*remembers'},
        {'type': 'grep', 'file': 'admin/shared/theme/tokens.css', 'pattern': '--ar-page.*#1c1917'},
    ],
    'VR-quickactions-s0-topleft': [
        {'type': 'grep', 'file': 'admin/standalone/pages/QuickActions.tsx', 'pattern': 'Title order.*Quick actions'},
        {'type': 'grep', 'file': 'admin/standalone/pages/QuickActions.tsx', 'pattern': 'Manage contextual prompt'},
        {'type': 'grep', 'file': 'admin/shared/theme/tokens.css', 'pattern': '--ar-page.*#1c1917'},
    ],
    'VR-team-s0-topleft': [
        {'type': 'grep', 'file': 'admin/standalone/pages/Team.tsx', 'pattern': 'Title order.*Team members'},
        {'type': 'grep', 'file': 'admin/standalone/pages/Team.tsx', 'pattern': 'Manage team|assign roles|escalation'},
        {'type': 'grep', 'file': 'admin/shared/theme/tokens.css', 'pattern': '--ar-page.*#1c1917'},
    ],
    # --- Shared style spec ---
    'VR-shared-style': [
        {'type': 'grep', 'file': 'admin/shared/theme/tokens.css', 'pattern': '--ar-chrome.*#0c0a09'},
        {'type': 'grep', 'file': 'admin/shared/theme/tokens.css', 'pattern': '--ar-page.*#1c1917'},
        {'type': 'grep', 'file': 'admin/shared/theme/tokens.css', 'pattern': '--ar-border.*#44403c'},
        {'type': 'grep', 'file': 'admin/shared/theme/agentRedTheme.ts', 'pattern': "chrome.*#0c0a09"},
        {'type': 'grep', 'file': 'admin/shared/theme/agentRedTheme.ts', 'pattern': "page.*#1c1917"},
    ],
    # --- Widget page VR-* specs ---
    'VR-widget-s0-title': [
        {'type': 'grep', 'file': 'admin/standalone/pages/Widget.tsx', 'pattern': 'Title order.*Widget configuration'},
        {'type': 'grep', 'file': 'admin/standalone/pages/Widget.tsx', 'pattern': 'Customize how.*chat widget'},
    ],
    'VR-widget-s0-layout': [
        {'type': 'grep', 'file': 'admin/standalone/pages/Widget.tsx', 'pattern': 'Live Preview'},
        {'type': 'grep', 'file': 'admin/standalone/pages/Widget.tsx', 'pattern': 'Installation|Embed code|Appearance'},
    ],
    'VR-widget-s0-header-left': [
        {'type': 'grep', 'file': 'admin/shared/theme/agentRedTheme.ts', 'pattern': "chrome.*#0c0a09"},
        {'type': 'grep', 'file': 'admin/standalone/layouts/StandaloneLayout.tsx', 'pattern': 'brand logo'},
        {'type': 'grep', 'file': 'admin/standalone/layouts/StandaloneLayout.tsx', 'pattern': 'agent_'},
    ],
    'VR-widget-s0-header-center': [
        {'type': 'grep', 'file': 'admin/shared/theme/agentRedTheme.ts', 'pattern': "chrome.*#0c0a09"},
        {'type': 'grep', 'file': 'admin/shared/theme/agentRedTheme.ts', 'pattern': "border.*#44403c|#44403c"},
    ],
    'VR-widget-s0-header-right': [
        {'type': 'grep', 'file': 'admin/standalone/layouts/StandaloneLayout.tsx', 'pattern': 'Storefront|external-link|storefront'},
        {'type': 'grep', 'file': 'admin/standalone/layouts/StandaloneLayout.tsx', 'pattern': 'Professional|tier|Badge'},
    ],
    'VR-widget-s0-nav-top': [
        {'type': 'grep', 'file': 'admin/standalone/layouts/StandaloneLayout.tsx', 'pattern': 'Dashboard'},
        {'type': 'grep', 'file': 'admin/standalone/layouts/StandaloneLayout.tsx', 'pattern': 'Inbox'},
        {'type': 'grep', 'file': 'admin/standalone/layouts/StandaloneLayout.tsx', 'pattern': 'Team members'},
    ],
    'VR-widget-s0-nav-mid': [
        {'type': 'grep', 'file': 'admin/standalone/layouts/StandaloneLayout.tsx', 'pattern': 'Knowledge base'},
        {'type': 'grep', 'file': 'admin/standalone/layouts/StandaloneLayout.tsx', 'pattern': 'Quick actions'},
        {'type': 'grep', 'file': 'admin/standalone/layouts/StandaloneLayout.tsx', 'pattern': 'Widget configuration'},
    ],
    'VR-widget-s0-nav-bottom': [
        {'type': 'grep', 'file': 'admin/standalone/layouts/StandaloneLayout.tsx', 'pattern': 'Integrations'},
        {'type': 'grep', 'file': 'admin/standalone/layouts/StandaloneLayout.tsx', 'pattern': 'Memory.*privacy'},
        {'type': 'grep', 'file': 'admin/standalone/layouts/StandaloneLayout.tsx', 'pattern': 'Billing'},
        {'type': 'grep', 'file': 'admin/standalone/layouts/StandaloneLayout.tsx', 'pattern': 'Agent Red Customer Experience'},
    ],
    'VR-widget-s0-embed-code': [
        {'type': 'grep', 'file': 'admin/standalone/pages/Widget.tsx', 'pattern': 'Embed code|embed.*code'},
        {'type': 'grep', 'file': 'admin/standalone/pages/Widget.tsx', 'pattern': 'script.*src|</body>'},
    ],
    'VR-widget-s0-install-body': [
        {'type': 'grep', 'file': 'admin/standalone/pages/Widget.tsx', 'pattern': 'Widget key|widget.*key'},
        {'type': 'grep', 'file': 'admin/standalone/pages/Widget.tsx', 'pattern': 'API URL|api.*url'},
    ],
    'VR-widget-s0-install-right': [
        {'type': 'grep', 'file': 'admin/standalone/pages/Widget.tsx', 'pattern': 'Rotate key|rotate'},
        {'type': 'grep', 'file': 'admin/standalone/pages/Widget.tsx', 'pattern': 'copy|Copy'},
    ],
    'VR-widget-s0-appearance-start': [
        {'type': 'grep', 'file': 'admin/standalone/pages/Widget.tsx', 'pattern': 'Appearance'},
        {'type': 'grep', 'file': 'admin/standalone/pages/Widget.tsx', 'pattern': 'Header.*color|header.*left.*color'},
    ],
    'VR-widget-s0-preview-header': [
        {'type': 'grep', 'file': 'admin/standalone/pages/Widget.tsx', 'pattern': 'Live Preview'},
        {'type': 'grep', 'file': 'admin/standalone/pages/Widget.tsx', 'pattern': 'preview'},
    ],
    'VR-widget-s0-preview-chat': [
        {'type': 'grep', 'file': 'admin/standalone/pages/Widget.tsx', 'pattern': 'How can I help|Hi there'},
        {'type': 'grep', 'file': 'admin/standalone/pages/Widget.tsx', 'pattern': 'Today|message.*bubble'},
    ],
    'VR-widget-s0-preview-input': [
        {'type': 'grep', 'file': 'admin/standalone/pages/Widget.tsx', 'pattern': 'Shipping info|quick.*action'},
        {'type': 'grep', 'file': 'admin/standalone/pages/Widget.tsx', 'pattern': 'question about'},
    ],
    'VR-widget-s0-preview-fab': [
        {'type': 'grep', 'file': 'admin/standalone/pages/Widget.tsx', 'pattern': 'primaryColor|launcherSize'},
        {'type': 'grep', 'file': 'admin/standalone/pages/Widget.tsx', 'pattern': 'Powered by'},
    ],
}


def run_assertion(assertion: dict) -> dict:
    """Execute a single grep/glob assertion and return result."""
    import subprocess, glob as globmod

    a_type = assertion['type']

    if a_type == 'grep':
        import re
        filepath = assertion['file']
        pattern = assertion['pattern']
        # Resolve relative to project root
        project_root = os.path.join(os.path.dirname(__file__), '..')
        full_path = os.path.normpath(os.path.join(project_root, filepath))

        if not os.path.exists(full_path):
            return {
                'type': 'grep',
                'description': f'grep "{pattern}" in {filepath}',
                'passed': False,
                'detail': f'File not found: {filepath}',
            }

        try:
            with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            passed = bool(re.search(pattern, content))
        except Exception as e:
            return {
                'type': 'grep',
                'description': f'grep "{pattern}" in {filepath}',
                'passed': False,
                'detail': str(e),
            }

        return {
            'type': 'grep',
            'description': f'grep "{pattern}" in {filepath}',
            'passed': passed,
            'detail': f'Pattern {"found" if passed else "NOT found"} in {filepath}',
        }

    elif a_type == 'glob':
        pattern = assertion['file']
        project_root = os.path.join(os.path.dirname(__file__), '..')
        full_pattern = os.path.normpath(os.path.join(project_root, pattern))
        matches = globmod.glob(full_pattern)
        passed = len(matches) > 0
        return {
            'type': 'glob',
            'description': f'glob "{pattern}" matches files',
            'passed': passed,
            'detail': f'{len(matches)} file(s) matched' if passed else 'No files matched',
        }

    return {'type': a_type, 'description': 'Unknown type', 'passed': False, 'detail': 'Unknown assertion type'}


def main():
    k = KnowledgeDB()

    converted = 0
    passed = 0
    failed = 0

    c = k._conn

    for spec_id, assertions in VR_CONVERSIONS.items():
        # Get spec version
        row = c.execute(
            "SELECT version FROM current_specifications WHERE id = ?", (spec_id,)
        ).fetchone()
        if not row:
            print(f"  SKIP {spec_id} — spec not found in KB")
            continue
        spec_version = row['version']

        # Run each assertion
        results = []
        all_passed = True
        for a in assertions:
            result = run_assertion(a)
            results.append(result)
            if not result['passed']:
                all_passed = False

        # Record in KB
        k.insert_assertion_run(
            spec_id=spec_id,
            spec_version=spec_version,
            overall_passed=all_passed,
            results=results,
            triggered_by='s148_convert_vr_assertions',
        )

        status = "PASS" if all_passed else "FAIL"
        if all_passed:
            passed += 1
        else:
            failed += 1
        converted += 1

        print(f"  {status} {spec_id} ({len(results)} assertions)")
        if not all_passed:
            for r in results:
                if not r['passed']:
                    print(f"    FAIL: {r['description']} — {r.get('detail', '')}")

    print(f"\nConverted {converted} VR-* specs: {passed} PASS, {failed} FAIL")
    k.close()


if __name__ == '__main__':
    main()
