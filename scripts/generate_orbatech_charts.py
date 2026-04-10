"""
Generate all charts for the OrbaTech Technical Evaluation Report v2.
Produces PNG files in a temp directory, returns paths for DOCX embedding.

© 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os
import tempfile

# ── Shared style ─────────────────────────────────────────────────────────
BRAND_BLUE = '#1B3A5C'
BRAND_LIGHT = '#4A90D9'
BRAND_ORANGE = '#E67E22'
BRAND_RED = '#CC0000'
BRAND_GREEN = '#27AE60'
BRAND_GRAY = '#7F8C8D'
BRAND_YELLOW = '#F39C12'

plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Calibri', 'Arial', 'Helvetica'],
    'font.size': 10,
    'axes.titlesize': 13,
    'axes.labelsize': 11,
    'figure.facecolor': 'white',
    'axes.facecolor': '#F8F9FA',
    'axes.grid': True,
    'grid.alpha': 0.3,
})

CHART_DIR = os.path.join(tempfile.gettempdir(), 'orbatech_charts')
os.makedirs(CHART_DIR, exist_ok=True)


def save(fig, name, dpi=200):
    path = os.path.join(CHART_DIR, f'{name}.png')
    fig.savefig(path, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    return path


# ══════════════════════════════════════════════════════════════════════════
# Figure 1: Engineering Maturity Radar Chart
# ══════════════════════════════════════════════════════════════════════════
def fig1_radar():
    categories = ['Tech Stack', 'Architecture', 'Code Quality', 'Testing',
                  'CI/CD', 'Security', 'Documentation', 'Deployment']
    # Updated: Testing score 2->4 per Codex correction
    values = [8, 6, 4, 4, 1, 3, 3, 2]

    N = len(categories)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    values_plot = values + values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_rlabel_position(30)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_yticklabels(['2', '4', '6', '8', '10'], fontsize=8)
    ax.set_ylim(0, 10)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=10, fontweight='bold')

    # Fill zones
    for threshold, color, alpha in [(3, '#FFCCCC', 0.15), (6, '#FFF3CD', 0.15), (10, '#D4EDDA', 0.15)]:
        circle = np.full(len(angles), threshold)
        ax.fill(angles, circle, color=color, alpha=alpha)

    ax.plot(angles, values_plot, 'o-', color=BRAND_BLUE, linewidth=2.5, markersize=8)
    ax.fill(angles, values_plot, color=BRAND_LIGHT, alpha=0.25)

    # Score labels
    for i, (angle, val) in enumerate(zip(angles[:-1], values)):
        offset = 0.8
        ax.text(angle, val + offset, str(val), ha='center', va='center',
                fontsize=11, fontweight='bold', color=BRAND_BLUE)

    ax.set_title('OrbaTech Engineering Maturity Assessment', fontsize=14,
                 fontweight='bold', color=BRAND_BLUE, pad=20)

    legend_elements = [
        mpatches.Patch(facecolor='#FFCCCC', alpha=0.4, label='Critical (1-3)'),
        mpatches.Patch(facecolor='#FFF3CD', alpha=0.4, label='Developing (4-6)'),
        mpatches.Patch(facecolor='#D4EDDA', alpha=0.4, label='Mature (7-10)'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', bbox_to_anchor=(1.3, -0.05), fontsize=9)

    return save(fig, 'fig1_radar')


# ══════════════════════════════════════════════════════════════════════════
# Figure 2: Application Architecture Diagram
# ══════════════════════════════════════════════════════════════════════════
def fig2_architecture():
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7)
    ax.axis('off')

    def box(x, y, w, h, label, color, sublabel=None):
        rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.1',
                                        facecolor=color, edgecolor=BRAND_BLUE, linewidth=1.5)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2 + (0.12 if sublabel else 0), label,
                ha='center', va='center', fontsize=10, fontweight='bold', color='white')
        if sublabel:
            ax.text(x + w/2, y + h/2 - 0.18, sublabel,
                    ha='center', va='center', fontsize=7.5, color='#E0E0E0')

    # Client tier
    ax.text(5, 6.7, 'CLIENT TIER', ha='center', fontsize=11, fontweight='bold', color=BRAND_BLUE)
    box(0.5, 6.0, 2.5, 0.5, 'Blazor Server', '#3498DB', 'SSR + SignalR')
    box(3.5, 6.0, 2.5, 0.5, 'Blazor WASM', '#2980B9', 'Interactive Components')
    box(6.5, 6.0, 2.5, 0.5, 'DevExpress UI', '#1ABC9C', 'Grid, Dashboard, Scheduler')

    # Application tier
    ax.text(5, 5.5, 'APPLICATION TIER', ha='center', fontsize=11, fontweight='bold', color=BRAND_BLUE)
    box(0.5, 4.7, 2.0, 0.5, 'Services', '#2C3E50', 'Business Logic')
    box(3.0, 4.7, 2.0, 0.5, 'Repositories', '#34495E', 'Data Access')
    box(5.5, 4.7, 2.0, 0.5, 'Identity', '#8E44AD', 'Auth + 2FA')
    box(8.0, 4.7, 1.5, 0.5, 'API', '#E74C3C', 'REST')

    # Data tier
    ax.text(5, 4.2, 'DATA TIER', ha='center', fontsize=11, fontweight='bold', color=BRAND_BLUE)
    box(0.5, 3.4, 2.5, 0.5, 'EF Core 8', '#27AE60', 'CRUD Operations')
    box(3.5, 3.4, 2.5, 0.5, 'Dapper', '#2ECC71', 'Stored Procedures')
    box(6.5, 3.4, 2.5, 0.5, 'SQL Server', '#16A085', '40+ SPs, 5 Triggers')

    # External
    ax.text(5, 2.9, 'EXTERNAL SERVICES', ha='center', fontsize=11, fontweight='bold', color=BRAND_BLUE)
    box(1.0, 2.1, 2.0, 0.5, 'MailKit', BRAND_ORANGE, 'Email Service')
    box(4.0, 2.1, 2.0, 0.5, 'SF Import', BRAND_YELLOW, 'Salesforce Data')
    box(7.0, 2.1, 2.0, 0.5, 'File Storage', BRAND_GRAY, 'Local Disk')

    # Tenant isolation note
    rect = mpatches.FancyBboxPatch((1.5, 1.2), 7, 0.6, boxstyle='round,pad=0.1',
                                    facecolor='#FFF3CD', edgecolor=BRAND_ORANGE, linewidth=1.5)
    ax.add_patch(rect)
    ax.text(5, 1.5, 'TENANT ISOLATION: TenantId column + EF Core Global Query Filters\n'
            '(47 IgnoreQueryFilters bypasses require audit)',
            ha='center', va='center', fontsize=9, color='#856404')

    # Arrows
    for y_from, y_to in [(6.0, 5.2), (4.7, 3.9)]:
        ax.annotate('', xy=(5, y_to), xytext=(5, y_from),
                    arrowprops=dict(arrowstyle='->', color=BRAND_GRAY, lw=1.5))

    ax.set_title('OrbaTech Application Architecture', fontsize=14,
                 fontweight='bold', color=BRAND_BLUE, pad=10)
    return save(fig, 'fig2_architecture')


# ══════════════════════════════════════════════════════════════════════════
# Figure 3: Security Posture Assessment
# ══════════════════════════════════════════════════════════════════════════
def fig3_security():
    domains = ['Secrets Mgmt', 'Authentication', 'Authorization', 'Transport (TLS)',
               'Data Encryption', 'Input Validation', 'API Security', 'Rate Limiting',
               'Audit Logging', 'Compliance']
    scores = [1, 6, 4, 2, 3, 5, 3, 1, 1, 1]
    colors = [BRAND_RED if s <= 2 else BRAND_ORANGE if s <= 4 else BRAND_YELLOW if s <= 6
              else BRAND_GREEN for s in scores]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(domains, scores, color=colors, edgecolor='white', height=0.6)
    ax.set_xlim(0, 10)
    ax.set_xlabel('Score (1-10)')
    ax.set_title('Security Posture Assessment', fontsize=14, fontweight='bold', color=BRAND_BLUE)
    ax.invert_yaxis()

    for bar, score in zip(bars, scores):
        ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2,
                str(score), va='center', fontsize=10, fontweight='bold')

    legend_elements = [
        mpatches.Patch(facecolor=BRAND_RED, label='Critical (1-2)'),
        mpatches.Patch(facecolor=BRAND_ORANGE, label='Concerning (3-4)'),
        mpatches.Patch(facecolor=BRAND_YELLOW, label='Developing (5-6)'),
        mpatches.Patch(facecolor=BRAND_GREEN, label='Adequate (7-10)'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9)
    return save(fig, 'fig3_security')


# ══════════════════════════════════════════════════════════════════════════
# Figure 4: Feature Capability Comparison (Original 12 dimensions)
# ══════════════════════════════════════════════════════════════════════════
def fig4_features():
    dims = ['Contacts', 'Pipeline', 'Email', 'Calendar', 'Reporting',
            'Mobile', 'API', 'AI/ML', 'Localization', 'Integrations',
            'Customization', 'Support']
    # OrbaTech, Salesforce, HubSpot, Zoho, Pipedrive
    orbatech = [7, 7, 5, 4, 3, 1, 2, 1, 4, 1, 5, 2]
    salesforce = [10, 10, 9, 9, 10, 9, 10, 9, 10, 10, 10, 10]
    hubspot = [9, 9, 10, 9, 9, 8, 9, 7, 8, 9, 8, 9]
    zoho = [8, 8, 8, 8, 8, 7, 8, 6, 10, 8, 9, 7]
    pipedrive = [8, 9, 8, 7, 7, 8, 8, 5, 5, 7, 6, 7]

    x = np.arange(len(dims))
    width = 0.15

    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(x - 2*width, orbatech, width, label='OrbaTech', color=BRAND_BLUE)
    ax.bar(x - width, salesforce, width, label='Salesforce', color='#00A1E0')
    ax.bar(x, hubspot, width, label='HubSpot', color='#FF7A59')
    ax.bar(x + width, zoho, width, label='Zoho', color='#D72B2B')
    ax.bar(x + 2*width, pipedrive, width, label='Pipedrive', color='#017737')

    ax.set_xticks(x)
    ax.set_xticklabels(dims, rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Capability Score (1-10)')
    ax.set_ylim(0, 11)
    ax.set_title('Feature Capability Comparison', fontsize=14, fontweight='bold', color=BRAND_BLUE)
    ax.legend(loc='upper right', fontsize=9)
    fig.tight_layout()
    return save(fig, 'fig4_features')


# ══════════════════════════════════════════════════════════════════════════
# Figure 5: Recommended Azure Architecture
# ══════════════════════════════════════════════════════════════════════════
def fig5_azure():
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')

    def azure_box(x, y, w, h, label, sublabel, color):
        rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.08',
                                        facecolor=color, edgecolor='#2C3E50', linewidth=1.2)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2 + 0.12, label,
                ha='center', va='center', fontsize=9, fontweight='bold', color='white')
        ax.text(x + w/2, y + h/2 - 0.12, sublabel,
                ha='center', va='center', fontsize=7, color='#E0E0E0')

    # Title
    ax.text(6, 7.7, 'Recommended Azure Architecture — OrbaTech CRM', ha='center',
            fontsize=14, fontweight='bold', color=BRAND_BLUE)

    # Region box
    rect = mpatches.FancyBboxPatch((0.3, 0.3), 11.4, 7.0, boxstyle='round,pad=0.15',
                                    facecolor='#F0F4F8', edgecolor=BRAND_BLUE, linewidth=2, linestyle='--')
    ax.add_patch(rect)
    ax.text(6, 7.1, 'Azure Canada Central (Primary) / East US (Secondary)',
            ha='center', fontsize=10, color=BRAND_BLUE, fontstyle='italic')

    # Ingress
    azure_box(4.5, 6.2, 3.0, 0.6, 'Azure Front Door', 'SSL + WAF + Geo-routing', '#0078D4')

    # Compute
    azure_box(1.0, 5.0, 2.5, 0.6, 'App Service P1v3', 'Blazor (2-6 instances)', '#0078D4')
    azure_box(4.0, 5.0, 2.5, 0.6, 'ACS Email', 'Email + SMS', '#0078D4')
    azure_box(7.0, 5.0, 2.5, 0.6, 'Entra ID B2C', 'Identity + MFA + SSO', '#0078D4')

    # Data
    azure_box(1.0, 3.6, 2.5, 0.6, 'Azure SQL', 'S2 → Elastic Pool', '#0078D4')
    azure_box(4.0, 3.6, 2.5, 0.6, 'Redis Cache', 'Session + Config', '#0078D4')
    azure_box(7.0, 3.6, 2.5, 0.6, 'Blob Storage', 'Attachments', '#0078D4')

    # Security
    azure_box(1.0, 2.2, 2.5, 0.6, 'Key Vault', 'Secrets + Managed ID', '#5B2D8E')
    azure_box(4.0, 2.2, 2.5, 0.6, 'Monitor + AI', 'Traces + Metrics + Logs', '#5B2D8E')
    azure_box(7.0, 2.2, 2.5, 0.6, 'Azure Policy', 'Compliance + Residency', '#5B2D8E')

    # Network
    rect2 = mpatches.FancyBboxPatch((1.0, 0.8), 8.5, 0.8, boxstyle='round,pad=0.08',
                                     facecolor='#E8F5E9', edgecolor=BRAND_GREEN, linewidth=1.2)
    ax.add_patch(rect2)
    ax.text(5.25, 1.2, 'Private Endpoints  |  Managed Identities  |  SQL RLS  |  Azure RBAC',
            ha='center', va='center', fontsize=9, fontweight='bold', color='#1B5E20')

    # Arrows
    ax.annotate('', xy=(6, 5.6), xytext=(6, 6.2),
                arrowprops=dict(arrowstyle='->', color=BRAND_GRAY, lw=1.5))

    return save(fig, 'fig5_azure')


# ══════════════════════════════════════════════════════════════════════════
# Figure 6: Azure Cost Projections
# ══════════════════════════════════════════════════════════════════════════
def fig6_costs():
    components = ['Compute', 'SQL DB', 'Storage/CDN', 'Identity', 'Monitoring',
                  'Networking', 'Email', 'Backup/DR']
    t10 = [50, 30, 5, 0, 10, 10, 0, 5]
    t100 = [300, 250, 30, 50, 50, 30, 20, 50]
    t1000 = [1800, 1500, 200, 500, 200, 100, 100, 300]

    x = np.arange(len(components))
    width = 0.25

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(x - width, t10, width, label='10 Tenants ($110/mo)', color=BRAND_GREEN)
    ax.bar(x, t100, width, label='100 Tenants ($780/mo)', color=BRAND_LIGHT)
    ax.bar(x + width, t1000, width, label='1,000 Tenants ($4,700/mo)', color=BRAND_BLUE)

    ax.set_xticks(x)
    ax.set_xticklabels(components, rotation=45, ha='right')
    ax.set_ylabel('Monthly Cost (USD)')
    ax.set_title('Estimated Monthly Azure Costs by Scaling Tier',
                 fontsize=14, fontweight='bold', color=BRAND_BLUE)
    ax.legend(fontsize=10)

    # Per-tenant annotation
    ax.annotate('$4.70/tenant/mo\nat scale', xy=(7, 300), fontsize=9,
                color=BRAND_BLUE, fontstyle='italic',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='#E8F4FD'))
    fig.tight_layout()
    return save(fig, 'fig6_costs')


# ══════════════════════════════════════════════════════════════════════════
# Figure 7: Technical Priority Roadmap
# ══════════════════════════════════════════════════════════════════════════
def fig7_roadmap():
    fig, ax = plt.subplots(figsize=(14, 7))

    tasks = [
        # (label, priority, start_month, duration, color)
        ('Security Remediation', 'P0', 1, 3, BRAND_RED),
        ('CI/CD Pipeline', 'P0', 1, 3, BRAND_RED),
        ('Automated Testing in CI', 'P0', 1, 3, BRAND_RED),
        ('Billing & Entitlements', 'P0', 1, 3, BRAND_RED),
        ('Multi-Tenant RLS', 'P1', 2, 5, BRAND_ORANGE),
        ('Containerization', 'P1', 2, 4, BRAND_ORANGE),
        ('Azure Deployment (IaC)', 'P1', 3, 4, BRAND_ORANGE),
        ('Compliance Foundations', 'P1', 3, 4, BRAND_ORANGE),
        ('API Auth (OAuth 2.0)', 'P1', 4, 3, BRAND_ORANGE),
        ('Tenant Self-Service', 'P1', 4, 3, BRAND_ORANGE),
        ('Localization (EN/FR)', 'P2', 5, 4, BRAND_YELLOW),
        ('Performance (Redis)', 'P2', 5, 4, BRAND_YELLOW),
        ('Documentation', 'P2', 6, 3, BRAND_YELLOW),
        ('Integration Expansion', 'P2', 6, 3, BRAND_YELLOW),
        ('Mobile/PWA', 'P3', 7, 4, BRAND_GREEN),
        ('AI/Automation', 'P3', 8, 4, BRAND_GREEN),
        ('Agent Red Integration', 'P3', 9, 4, BRAND_GREEN),
        ('SOC-2 Certification', 'P3', 10, 3, BRAND_GREEN),
    ]

    for i, (label, prio, start, dur, color) in enumerate(tasks):
        y = len(tasks) - 1 - i
        ax.barh(y, dur, left=start, height=0.6, color=color, edgecolor='white', linewidth=0.5)
        ax.text(start + dur/2, y, f'{label}', ha='center', va='center',
                fontsize=8, fontweight='bold', color='white')
        ax.text(start - 0.3, y, prio, ha='right', va='center', fontsize=8,
                fontweight='bold', color=color)

    ax.set_xlim(0.5, 13.5)
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels([f'M{m}' for m in range(1, 13)])
    ax.set_xlabel('Months')
    ax.set_yticks([])
    ax.set_title('Recommended Technical Priority Roadmap',
                 fontsize=14, fontweight='bold', color=BRAND_BLUE)

    legend_elements = [
        mpatches.Patch(facecolor=BRAND_RED, label='P0 Critical'),
        mpatches.Patch(facecolor=BRAND_ORANGE, label='P1 High'),
        mpatches.Patch(facecolor=BRAND_YELLOW, label='P2 Medium'),
        mpatches.Patch(facecolor=BRAND_GREEN, label='P3 Future'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9)
    fig.tight_layout()
    return save(fig, 'fig7_roadmap')


# ══════════════════════════════════════════════════════════════════════════
# Figure 8: OrbaTech vs Agent Red Comparison
# ══════════════════════════════════════════════════════════════════════════
def fig8_comparison():
    categories = ['Compute', 'Database', 'Identity', 'Tenant Isolation',
                  'CI/CD', 'Monitoring', 'Secrets', 'Email/SMS']
    orbatech = ['App Service\n(PaaS)', 'SQL Server', 'Entra ID B2C\n(recommended)',
                'App-level\n+ RLS (rec.)', 'None\n(to build)', 'None\n(to add)',
                'Key Vault\n(recommended)', 'MailKit\n(Windows svc)']
    agentred = ['Container Apps\n(8 containers)', 'Cosmos DB\n(partition keys)',
                'Custom\n(widget/API keys)', 'App-level\n+ partition keys',
                '13-phase\npipeline', 'App Insights\n+ custom', 'Key Vault\n(managed ID)',
                'ACS\n(Email + SMS)']

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, len(categories) + 1)
    ax.axis('off')

    # Headers
    ax.text(3, len(categories) + 0.5, 'OrbaTech CRM', ha='center', fontsize=12,
            fontweight='bold', color=BRAND_ORANGE)
    ax.text(6, len(categories) + 0.5, 'Dimension', ha='center', fontsize=12,
            fontweight='bold', color=BRAND_BLUE)
    ax.text(9, len(categories) + 0.5, 'Agent Red', ha='center', fontsize=12,
            fontweight='bold', color=BRAND_GREEN)

    for i, (cat, orb, ar) in enumerate(zip(categories, orbatech, agentred)):
        y = len(categories) - i - 0.5
        # Background stripe
        if i % 2 == 0:
            rect = mpatches.FancyBboxPatch((0.5, y - 0.4), 11, 0.8,
                                            boxstyle='round,pad=0.02',
                                            facecolor='#F0F4F8', edgecolor='none')
            ax.add_patch(rect)
        ax.text(3, y, orb, ha='center', va='center', fontsize=9, color='#2C3E50')
        ax.text(6, y, cat, ha='center', va='center', fontsize=10, fontweight='bold', color=BRAND_BLUE)
        ax.text(9, y, ar, ha='center', va='center', fontsize=9, color='#2C3E50')

    ax.set_title('OrbaTech vs Agent Red — Azure Deployment Comparison',
                 fontsize=14, fontweight='bold', color=BRAND_BLUE, pad=20)
    return save(fig, 'fig8_comparison')


# ══════════════════════════════════════════════════════════════════════════
# Figure 9: Integration Architecture
# ══════════════════════════════════════════════════════════════════════════
def fig9_integration():
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # OrbaTech box
    rect1 = mpatches.FancyBboxPatch((0.5, 1), 4.5, 4, boxstyle='round,pad=0.15',
                                     facecolor='#E8F4FD', edgecolor=BRAND_BLUE, linewidth=2)
    ax.add_patch(rect1)
    ax.text(2.75, 4.7, 'OrbaTech CRM', ha='center', fontsize=12, fontweight='bold', color=BRAND_BLUE)

    orb_items = ['Contacts & Profiles', 'Deal Pipeline', 'Email History',
                 'Activity Timeline', 'Custom Fields']
    for i, item in enumerate(orb_items):
        ax.text(2.75, 4.0 - i * 0.6, f'• {item}', ha='center', fontsize=9, color='#2C3E50')

    # Agent Red box
    rect2 = mpatches.FancyBboxPatch((7, 1), 4.5, 4, boxstyle='round,pad=0.15',
                                     facecolor='#E8F5E9', edgecolor=BRAND_GREEN, linewidth=2)
    ax.add_patch(rect2)
    ax.text(9.25, 4.7, 'Agent Red AI', ha='center', fontsize=12, fontweight='bold', color=BRAND_GREEN)

    ar_items = ['AI Conversations', 'Sentiment Analysis', 'Quality Scores',
                'Lead Qualification', 'Summaries']
    for i, item in enumerate(ar_items):
        ax.text(9.25, 4.0 - i * 0.6, f'• {item}', ha='center', fontsize=9, color='#2C3E50')

    # Arrows
    ax.annotate('', xy=(7, 3.8), xytext=(5, 3.8),
                arrowprops=dict(arrowstyle='->', color=BRAND_BLUE, lw=2.5))
    ax.text(6, 4.1, 'Contact Context\nOpportunity Status\nActivity History',
            ha='center', fontsize=8, color=BRAND_BLUE)

    ax.annotate('', xy=(5, 2.2), xytext=(7, 2.2),
                arrowprops=dict(arrowstyle='->', color=BRAND_GREEN, lw=2.5))
    ax.text(6, 1.6, 'Summaries\nSentiment\nQuality Metrics',
            ha='center', fontsize=8, color=BRAND_GREEN)

    # Integration layer
    rect3 = mpatches.FancyBboxPatch((4.5, 0.3), 3, 0.5, boxstyle='round,pad=0.08',
                                     facecolor='#FFF3CD', edgecolor=BRAND_ORANGE, linewidth=1.5)
    ax.add_patch(rect3)
    ax.text(6, 0.55, 'OAuth 2.0  |  REST  |  Webhooks', ha='center', fontsize=9,
            fontweight='bold', color='#856404')

    ax.set_title('OrbaTech + Agent Red — Bidirectional Integration',
                 fontsize=14, fontweight='bold', color=BRAND_BLUE, pad=10)
    return save(fig, 'fig9_integration')


# ══════════════════════════════════════════════════════════════════════════
# Figure 10: Summary Assessment Matrix (NEW for Section 8)
# ══════════════════════════════════════════════════════════════════════════
def fig10_summary_matrix():
    platforms = ['OrbaTech', 'Salesforce', 'HubSpot', 'Zoho', 'Pipedrive', 'Freshsales', 'Monday CRM']
    dimensions = ['Provisioning', 'Billing', 'Compliance', 'Integrations', 'Documentation', 'Arch Docs']
    scores = [
        [2, 1, 1, 1, 2, 1],  # OrbaTech
        [5, 5, 5, 5, 5, 5],  # Salesforce
        [5, 5, 4, 5, 5, 4],  # HubSpot
        [4, 5, 5, 4, 4, 3],  # Zoho
        [4, 4, 4, 4, 4, 3],  # Pipedrive
        [4, 4, 4, 4, 4, 3],  # Freshsales
        [4, 4, 4, 3, 3, 3],  # Monday CRM
    ]
    totals = [sum(s) for s in scores]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={'width_ratios': [3, 1]})

    # Heatmap
    data = np.array(scores)
    im = ax1.imshow(data, cmap='RdYlGn', aspect='auto', vmin=0, vmax=5)
    ax1.set_xticks(range(len(dimensions)))
    ax1.set_xticklabels(dimensions, rotation=45, ha='right', fontsize=9)
    ax1.set_yticks(range(len(platforms)))
    ax1.set_yticklabels(platforms, fontsize=10)

    for i in range(len(platforms)):
        for j in range(len(dimensions)):
            color = 'white' if data[i, j] <= 2 else 'black'
            ax1.text(j, i, str(data[i, j]), ha='center', va='center',
                    fontsize=11, fontweight='bold', color=color)

    ax1.set_title('Enterprise Readiness Scores (1-5)', fontsize=13,
                  fontweight='bold', color=BRAND_BLUE)

    # Total bar chart
    colors = [BRAND_RED] + [BRAND_LIGHT] * 6
    bars = ax2.barh(range(len(platforms)), totals, color=colors, edgecolor='white')
    ax2.set_yticks(range(len(platforms)))
    ax2.set_yticklabels(platforms, fontsize=10)
    ax2.set_xlabel('Total (out of 30)')
    ax2.set_xlim(0, 32)
    ax2.invert_yaxis()
    ax2.set_title('Total Score', fontsize=13, fontweight='bold', color=BRAND_BLUE)

    for bar, total in zip(bars, totals):
        ax2.text(bar.get_width() + 0.5, bar.get_y() + bar.get_height()/2,
                str(total), va='center', fontsize=11, fontweight='bold')

    fig.tight_layout()
    return save(fig, 'fig10_summary')


# ══════════════════════════════════════════════════════════════════════════
# Generate all
# ══════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    charts = {}
    for name, func in [
        ('fig1', fig1_radar),
        ('fig2', fig2_architecture),
        ('fig3', fig3_security),
        ('fig4', fig4_features),
        ('fig5', fig5_azure),
        ('fig6', fig6_costs),
        ('fig7', fig7_roadmap),
        ('fig8', fig8_comparison),
        ('fig9', fig9_integration),
        ('fig10', fig10_summary_matrix),
    ]:
        path = func()
        charts[name] = path
        print(f'  {name}: {path}')

    print(f'\nAll {len(charts)} charts generated in {CHART_DIR}')
