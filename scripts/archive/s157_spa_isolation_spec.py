"""S157: Create SPA Console Isolation specification and related artifacts."""
# © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
import sys
sys.path.insert(0, 'tools/knowledge-db')
import db

kdb = db.KnowledgeDB()

# ---------------------------------------------------------------------------
# SPEC-1667: SPA Console Authentication Isolation
# ---------------------------------------------------------------------------
SPA_ISOLATION_SPEC = """\
The Service Provider Administrator (SPA) console MUST authenticate via a \
platform-level credential store that is completely isolated from all tenant \
team_members collections. The SPA has zero permissions to act within any \
tenancy and does not exist as a user for any tenancy.

## Architectural Boundary

1. **Complete isolation:** The SPA console MUST NOT authenticate by looking up \
credentials in any tenant's team_members collection. SPA credentials MUST be \
stored in a dedicated platform-level collection (e.g., `platform_admins`) that \
is not scoped to any tenant_id.

2. **No tenant affiliation:** When the SPA authenticates, the resulting context \
MUST NOT contain a tenant_id. The SPA is not a member of any tenancy. It exists \
above the tenant layer, not within it.

3. **Landlord/tenant analogy:** The landlord (SPA) can view which apartments \
(tenancies) exist, their status, and their metadata. The landlord CANNOT enter \
any apartment using landlord credentials. The ONLY way a human who is also the \
Service Provider Administrator can access a merchant's admin UI is if that \
tenant's superadmin creates a separate team member identity within the tenancy \
and assigns it to that human.

4. **No credential overlap:** SPA credentials and tenant team_member credentials \
MUST be stored in separate collections with separate lookup mechanisms. A key \
that authenticates an SPA MUST NOT resolve through team_members, and a key that \
authenticates a tenant team member MUST NOT grant SPA access.

5. **SUPERADMIN role scope:** The `superadmin` value in TeamMemberRole is a \
tenant-level role — the highest-privilege user WITHIN a single tenancy. It MUST \
NOT be conflated with the Service Provider Administrator, which operates OUTSIDE \
all tenancies.

## Current Violation

The current implementation stores SUPERADMIN credentials as team_member records \
inside a specific tenant's team_members collection. The `/api/superadmin/*` \
endpoints then silently discard the tenant context and perform cross-partition \
queries. This creates a false dependency between SPA authentication and a \
specific tenant's data, violating isolation.

## Required Changes

- Create a `platform_admins` Cosmos DB collection (or equivalent) for SPA \
credential storage
- SPA authentication middleware resolves credentials from platform_admins, \
NOT from team_members
- SPA authentication produces a PlatformContext (or equivalent), NOT a \
TenantContext with a tenant_id
- Remove auto_provision_superadmin() from tenant provisioning — SPA accounts \
are provisioned independently
- The `superadmin` TeamMemberRole remains for tenant-level use (highest tenant \
user), but is NOT the SPA identity

[Source: src/multi_tenant/superadmin_api.py]
"""

kdb.insert_spec(
    'SPEC-1667',
    'SPA Console Authentication MUST Be Isolated From All Tenant Collections',
    'specified',
    'Owner',
    'S157: Owner-directed specification — SPA console must not authenticate via tenant team_members. Corrects architectural drift where SUPERADMIN was stored inside a tenant.',
    description=SPA_ISOLATION_SPEC,
    priority='critical',
    scope='platform',
    section='authentication',
    tags=['spa-console', 'isolation', 'authentication', 'platform-admin', 'architecture'],
    assertions=[
        {
            'type': 'grep_absent',
            'file': 'src/multi_tenant/superadmin_api.py',
            'pattern': 'team_members',
            'description': 'SPA endpoints must not reference team_members collection'
        }
    ],
    type='requirement',
)
print('SPEC-1667 created: SPA Console Authentication Isolation')

# ---------------------------------------------------------------------------
# SPEC-1668: SUPERADMIN Role Is Tenant-Scoped Only
# ---------------------------------------------------------------------------
SUPERADMIN_SCOPE_SPEC = """\
The `superadmin` value in TeamMemberRole is a tenant-level role representing \
the highest-privilege user WITHIN a single tenancy. It MUST NOT be used to \
represent or authenticate the Service Provider Administrator (SPA).

## Rules

1. The `superadmin` role exists only within a tenant's team_members collection
2. A tenant superadmin can manage all aspects of their OWN tenancy
3. A tenant superadmin has ZERO access to other tenancies or the SPA console
4. The SPA console uses a separate identity system (see SPEC-1667)
5. The same human may hold BOTH a tenant superadmin role (within one tenancy) \
AND an SPA identity (at the platform level), but these are two separate \
credentials with separate storage

## Supersedes

This spec supersedes any prior interpretation where `superadmin` in \
TeamMemberRole was used to control SPA console access.

[Source: src/multi_tenant/cosmos_schema.py]
"""

kdb.insert_spec(
    'SPEC-1668',
    'SUPERADMIN TeamMemberRole Is Tenant-Scoped — NOT the SPA Identity',
    'specified',
    'Owner',
    'S157: Owner-directed specification — clarifies that superadmin role is tenant-internal, not platform-level SPA identity',
    description=SUPERADMIN_SCOPE_SPEC,
    priority='critical',
    scope='platform',
    section='authentication',
    tags=['superadmin', 'role', 'tenant-scope', 'spa-isolation'],
    assertions=[
        {
            'type': 'grep',
            'file': 'src/multi_tenant/cosmos_schema.py',
            'pattern': 'SUPERADMIN',
            'description': 'SUPERADMIN role must exist in TeamMemberRole enum'
        }
    ],
    type='requirement',
)
print('SPEC-1668 created: SUPERADMIN Role Is Tenant-Scoped Only')

# ---------------------------------------------------------------------------
# Update SPEC-0360 to clarify role scope
# ---------------------------------------------------------------------------
kdb.update_spec(
    'SPEC-0360',
    'Claude',
    'S157: Clarify that the 4-role hierarchy is tenant-internal. SUPERADMIN is the highest tenant role, not the SPA identity (see SPEC-1667/1668).',
    description="""\
The 4-role architecture (superadmin, admin, escalation_agent, viewer) defines \
the permission hierarchy WITHIN a single tenancy. All 4 roles exist exclusively \
in the tenant's team_members collection. The superadmin is the highest-privilege \
user within that tenancy — it is NOT the Service Provider Administrator (SPA), \
which operates at the platform level outside all tenancies (see SPEC-1667).

[Source: src/multi_tenant/cosmos_schema.py]
""",
)
print('SPEC-0360 updated: Clarified 4-role hierarchy is tenant-internal')

# ---------------------------------------------------------------------------
# Work Items
# ---------------------------------------------------------------------------

# WI-1065: Create platform_admins collection
kdb.insert_work_item(
    'WI-1065',
    'Create platform_admins Cosmos DB collection for SPA credential storage',
    'defect',  # architectural defect, not new feature
    'infrastructure',
    'open',
    'Claude',
    'S157: SPEC-1667 requires SPA credentials stored separately from tenant team_members',
    description="""\
Create a new Cosmos DB collection `platform_admins` (or equivalent) in both \
production and staging databases. This collection stores SPA console credentials \
(email, api_key_hash, role=platform_admin, mfa settings) independently of any \
tenant. Partition key TBD (could be /email or /id since collection will be small).

Depends on: SPEC-1667
""",
    source_spec_id='SPEC-1667',
    priority='critical',
)
print('WI-1065 created: Create platform_admins collection')

# WI-1066: Refactor SPA auth middleware
kdb.insert_work_item(
    'WI-1066',
    'Refactor SPA console authentication to use platform_admins instead of team_members',
    'defect',
    'authentication',
    'open',
    'Claude',
    'S157: SPEC-1667 requires SPA auth isolated from tenant collections',
    description="""\
Refactor the authentication middleware chain so that:
1. SPA API keys (new prefix TBD, e.g. `ar_spa_*`) resolve via platform_admins collection
2. SPA authentication produces a PlatformContext (not TenantContext)
3. `/api/superadmin/*` endpoints accept PlatformContext instead of TenantContext
4. Tenant team_member API keys (`ar_user_*`) CANNOT access `/api/superadmin/*` endpoints
5. Remove the `require_role(TeamMemberRole.SUPERADMIN)` pattern from superadmin endpoints — \
replace with a `require_platform_admin()` dependency

Depends on: WI-1065, SPEC-1667, SPEC-1668
""",
    source_spec_id='SPEC-1667',
    priority='critical',
)
print('WI-1066 created: Refactor SPA auth middleware')

# WI-1067: Remove auto_provision_superadmin from tenant provisioning
kdb.insert_work_item(
    'WI-1067',
    'Remove auto_provision_superadmin() from tenant provisioning flow',
    'defect',
    'provisioning',
    'open',
    'Claude',
    'S157: SPEC-1667 — SPA accounts must not be created inside tenant team_members',
    description="""\
The current `auto_provision_superadmin()` in provisioning.py creates a \
SUPERADMIN-role team member inside the newly provisioned tenant. This must be \
removed or replaced:
1. SPA identity is provisioned independently in platform_admins (WI-1065)
2. Tenant provisioning should create an `admin`-role team member as the \
initial tenant owner (not superadmin, or keep superadmin as the highest \
tenant role — owner decision needed)
3. The raw API key for the tenant's initial admin is still emailed once

Depends on: WI-1065, WI-1066, SPEC-1667, SPEC-1668
""",
    source_spec_id='SPEC-1667',
    priority='high',
)
print('WI-1067 created: Remove auto_provision_superadmin from provisioning')

# WI-1068: Seed SPA credentials in production + staging
kdb.insert_work_item(
    'WI-1068',
    'Seed SPA platform_admin credentials in production and staging Cosmos',
    'new',
    'infrastructure',
    'open',
    'Claude',
    'S157: After WI-1065 creates the collection, seed the owner SPA credentials',
    description="""\
Once platform_admins collection exists (WI-1065), seed the owner's SPA \
credentials:
1. Generate SPA API key (new prefix, e.g. `ar_spa_*`)
2. Hash and store in platform_admins
3. Store raw key in Key Vault
4. Verify SPA console login works on both environments

Depends on: WI-1065, WI-1066
""",
    source_spec_id='SPEC-1667',
    priority='high',
)
print('WI-1068 created: Seed SPA credentials')

# ---------------------------------------------------------------------------
# Test Artifacts
# ---------------------------------------------------------------------------

# TEST-8799: SPA credentials not in team_members
kdb.insert_test(
    'TEST-8799',
    'SPA credentials MUST NOT exist in any tenant team_members collection',
    'SPEC-1667',
    'architectural',
    'PASS: No team_member document with SPA-level platform access exists in team_members',
    'Claude',
    'S157: Verify SPA isolation from tenant collections',
    description='Query all team_members across all tenants. Verify no document has a role or flag that grants cross-tenant SPA access. SPA credentials must only exist in platform_admins.',
)
print('TEST-8799 created')

# TEST-8800: SPA auth resolves from platform_admins
kdb.insert_test(
    'TEST-8800',
    'SPA console authentication MUST resolve credentials from platform_admins collection only',
    'SPEC-1667',
    'architectural',
    'PASS: SPA API key lookup uses platform_admins, not team_members',
    'Claude',
    'S157: Verify SPA auth pathway is isolated',
    description='Authenticate with an SPA API key. Verify the middleware resolves it via platform_admins collection. Verify no team_members query is executed during SPA auth.',
)
print('TEST-8800 created')

# TEST-8801: SPA auth does NOT produce TenantContext
kdb.insert_test(
    'TEST-8801',
    'SPA authentication MUST NOT produce a tenant-scoped context',
    'SPEC-1667',
    'architectural',
    'PASS: SPA auth produces PlatformContext (no tenant_id)',
    'Claude',
    'S157: Verify SPA context is not tenant-scoped',
    description='Authenticate as SPA. Verify the resulting context object has no tenant_id field. Verify it cannot be used to access tenant-scoped endpoints (/api/admin/*).',
)
print('TEST-8801 created')

# TEST-8802: Tenant superadmin cannot access SPA endpoints
kdb.insert_test(
    'TEST-8802',
    'Tenant superadmin API key MUST NOT grant access to /api/superadmin/* endpoints',
    'SPEC-1668',
    'security',
    'PASS: Tenant superadmin key returns 403 on /api/superadmin/* endpoints',
    'Claude',
    'S157: Verify tenant superadmin role does not grant SPA access',
    description='Use a tenant superadmin API key (ar_user_*) to call /api/superadmin/tenants/summary. Verify it returns 403 Forbidden. Only SPA platform_admin credentials should access these endpoints.',
)
print('TEST-8802 created')

# TEST-8803: SPA key cannot access tenant-scoped endpoints
kdb.insert_test(
    'TEST-8803',
    'SPA API key MUST NOT grant access to tenant-scoped /api/admin/* endpoints',
    'SPEC-1667',
    'security',
    'PASS: SPA key returns 403 on /api/admin/* endpoints',
    'Claude',
    'S157: Verify SPA cannot enter tenant environments',
    description='Use an SPA API key (ar_spa_*) to call /api/admin/dashboard. Verify it returns 403 Forbidden. The SPA has no permissions within any tenancy.',
)
print('TEST-8803 created')

# TEST-8804: Human dual-identity requires separate credentials
kdb.insert_test(
    'TEST-8804',
    'A human who is both SPA and tenant admin MUST use separate credentials for each',
    'SPEC-1668',
    'security',
    'PASS: Same human uses ar_spa_* for SPA console and ar_user_* for tenant admin',
    'Claude',
    'S157: Verify dual-identity requires separate credential stores',
    description='The same human may be both an SPA (platform_admins) and a tenant admin (team_members). Verify these are two separate records in two separate collections with two separate API keys. One key cannot be used to access both contexts.',
)
print('TEST-8804 created')

print()
print('=== Summary ===')
print('Specs created: SPEC-1667, SPEC-1668')
print('Spec updated: SPEC-0360 (clarified tenant-internal scope)')
print('Work items created: WI-1065, WI-1066, WI-1067, WI-1068')
print('Tests created: TEST-8799, TEST-8800, TEST-8801, TEST-8802, TEST-8803, TEST-8804')

kdb.close()
