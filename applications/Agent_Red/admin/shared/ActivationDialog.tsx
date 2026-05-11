// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * ActivationDialog — Modal for validating and activating draft configuration.
 *
 * Triggered by the [Activate] button on ActivationBanner. Shows:
 *   1. Validation status — green checks / red X / yellow warnings
 *   2. Change summary grouped by category
 *   3. [Activate now] button (disabled if hard-block validation fails)
 *   4. [Cancel] button
 *
 * API endpoints consumed:
 *   GET  /api/config/draft          — Full draft state + diff
 *   POST /api/config/draft/activate — Execute activation
 *
 * Props:
 *   - apiFetch  — shell-provided fetch wrapper
 *   - onNotify  — shell toast callback
 *   - onClose   — close the dialog
 *   - onSuccess — called after successful activation (trigger banner refresh)
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import React, { useCallback, useEffect, useState } from 'react';
import { tokens, dialog, button } from './theme/styles';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface DraftState {
  has_pending_changes: boolean;
  active_version: number;
  active_activated_at: string | null;
  draft_version: number | null;
  changed_fields: string[];
  draft_config: Record<string, unknown>;
  active_config: Record<string, unknown>;
}

interface PreflightResult {
  can_activate: boolean;
  hard_errors: Array<{ field: string; message: string; page?: string }>;
  warnings: Array<{ field: string; message: string; page?: string }>;
}

interface ActivateResult {
  success: boolean;
  version: number;
  activated_at: string | null;
  errors: Array<{ field: string; message: string }>;
  warnings: Array<{ field: string; message: string }>;
}

interface ActivationDialogProps {
  apiFetch: (path: string, init?: RequestInit) => Promise<Response>;
  onNotify: (message: string, type: 'success' | 'error' | 'warning' | 'info') => void;
  onClose: () => void;
  onSuccess: () => void;
}

// ---------------------------------------------------------------------------
// Field grouping
// ---------------------------------------------------------------------------

/** Map page slugs from preflight validation to human-readable labels. */
function pageLabel(page: string): string {
  const map: Record<string, string> = {
    'agent-configuration': 'Agent configuration',
    'knowledge-base': 'Knowledge base',
    'quick-actions': 'Quick actions',
    'widget-configuration': 'Widget configuration',
    'system': 'System',
  };
  return map[page] ?? page.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

/** Map config field prefixes to human-readable group names. */
function groupField(field: string): string {
  if (field === 'kb_modified_at') return 'Knowledge base';
  if (field === 'qa_modified_at') return 'Quick actions';
  if (field.startsWith('widget_')) return 'Widget configuration';
  if (field.startsWith('retrieval_') || field.startsWith('intent_')) return 'Retrieval & intent';
  if (field.startsWith('escalation_')) return 'Escalation rules';
  if (['brand_name', 'brand_voice', 'brand_tagline', 'greeting_message',
       'greeting_follow_up'].includes(field)) return 'Brand & tone';
  if (['response_length', 'formality_level', 'use_emoji', 'cite_sources_in_response',
       'custom_instructions'].includes(field)) return 'Response style';
  if (field.startsWith('memory_') || field.startsWith('data_retention_')) return 'Memory & privacy';
  return 'Agent configuration';
}

/** Human-readable label for signal fields and config fields. */
function fieldLabel(field: string): string {
  if (field === 'kb_modified_at') return 'articles modified';
  if (field === 'qa_modified_at') return 'prompts or assignments modified';
  return field.replace(/_/g, ' ');
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function ActivationDialog({
  apiFetch,
  onNotify,
  onClose,
  onSuccess,
}: ActivationDialogProps) {
  const [draft, setDraft] = useState<DraftState | null>(null);
  const [preflight, setPreflight] = useState<PreflightResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [activating, setActivating] = useState(false);
  const [confirmed, setConfirmed] = useState(false);
  const [activateErrors, setActivateErrors] = useState<Array<{ field: string; message: string }>>([]);
  const [activateWarnings, setActivateWarnings] = useState<Array<{ field: string; message: string }>>([]);

  // Fetch draft state + preflight validation on mount (D35: show errors immediately)
  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const [draftRes, preflightRes] = await Promise.all([
          apiFetch('/api/config/draft'),
          apiFetch('/api/config/draft/preflight'),
        ]);
        if (!cancelled) {
          if (draftRes.ok) setDraft(await draftRes.json());
          if (preflightRes.ok) setPreflight(await preflightRes.json());
        }
      } catch {
        // handled
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [apiFetch]);

  // Activate handler
  const handleActivate = useCallback(async () => {
    setActivating(true);
    setActivateErrors([]);
    setActivateWarnings([]);
    try {
      const res = await apiFetch('/api/config/draft/activate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: '{}',
      });
      if (res.ok) {
        const result: ActivateResult = await res.json();
        if (result.warnings?.length) {
          setActivateWarnings(result.warnings);
        }
        onNotify(
          `Configuration activated (v${result.version})`,
          'success',
        );
        onSuccess();
        onClose();
      } else {
        const body = await res.json().catch(() => ({ detail: 'Activation failed' }));
        const errors = body.detail?.errors ?? [{ field: '_system', message: body.detail ?? 'Activation failed' }];
        setActivateErrors(errors);
        onNotify('Activation blocked — see errors below', 'error');
      }
    } catch {
      onNotify('Network error during activation', 'error');
    } finally {
      setActivating(false);
    }
  }, [apiFetch, onNotify, onClose, onSuccess]);

  // Group changed fields
  const groups: Record<string, string[]> = {};
  if (draft?.changed_fields) {
    for (const field of draft.changed_fields) {
      const group = groupField(field);
      if (!groups[group]) groups[group] = [];
      groups[group].push(field);
    }
  }

  return (
    <div style={dialog.overlay} onClick={onClose}>
      <div style={dialogPanel} onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div style={headerStyle}>
          <h2 style={dialog.title}>Activate configuration</h2>
          <button onClick={onClose} style={dialog.closeButton}>✕</button>
        </div>

        {/* Content */}
        <div style={bodyStyle}>
          {loading && <div style={mutedCentered}>Loading…</div>}

          {/* D35: Preflight hard errors — shown immediately on dialog open */}
          {!loading && preflight && preflight.hard_errors.length > 0 && (
            <div style={dialog.errorSection}>
              <h3 style={dialog.errorSectionTitle}>
                Required before activation
              </h3>
              <div style={{ ...summaryStyle, marginBottom: '12px' }}>
                The following fields must be configured before your AI assistant can be activated:
              </div>
              {preflight.hard_errors.map((e, i) => (
                <div key={i} style={dialog.errorText}>
                  <strong>{e.page ? pageLabel(e.page) : e.field}:</strong> {e.message}
                </div>
              ))}
            </div>
          )}

          {/* Preflight warnings */}
          {!loading && preflight && preflight.warnings.length > 0 && (
            <div style={warningSectionStyle}>
              <h3 style={dialog.warningSectionTitle}>
                Recommendations
              </h3>
              {preflight.warnings.map((w, i) => (
                <div key={i} style={warningItemStyle}>
                  <strong>{w.page ? pageLabel(w.page) : w.field}:</strong> {w.message}
                </div>
              ))}
            </div>
          )}

          {/* Change summary — only when there are pending changes AND no hard errors */}
          {!loading && draft?.has_pending_changes && preflight?.can_activate && (
            <div style={sectionStyle}>
              <h3 style={sectionTitleStyle}>Changes to activate</h3>
              <div style={summaryStyle}>
                {draft.changed_fields.length} field{draft.changed_fields.length !== 1 ? 's' : ''} changed
                {draft.draft_version != null && ` (draft v${draft.draft_version})`}
              </div>

              {Object.entries(groups).map(([group, fields]) => (
                <div key={group} style={groupStyle}>
                  <div style={groupLabelStyle}>{group}</div>
                  <div style={fieldListStyle}>
                    {fields.map(f => (
                      <span key={f} style={fieldChipStyle}>
                        {fieldLabel(f)}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Post-activate errors (from actual activation attempt) */}
          {activateErrors.length > 0 && (
            <div style={dialog.errorSection}>
              <h3 style={dialog.errorSectionTitle}>
                Activation blocked
              </h3>
              {activateErrors.map((e, i) => (
                <div key={i} style={dialog.errorText}>
                  <strong>{e.field}:</strong> {e.message}
                </div>
              ))}
            </div>
          )}

          {/* No changes and no errors */}
          {!loading && !draft?.has_pending_changes && preflight?.can_activate && (
            <div style={mutedCentered}>Draft configuration is ready to activate.</div>
          )}

          {/* Confirmation step */}
          {confirmed && preflight?.can_activate && activateErrors.length === 0 && (
            <div style={confirmSectionStyle}>
              Are you sure you want to activate these changes? This will make them live immediately.
            </div>
          )}
        </div>

        {/* Footer */}
        <div style={footerStyle}>
          <button onClick={onClose} style={dialog.cancelButton}>
            {preflight && !preflight.can_activate ? 'Close' : 'Cancel'}
          </button>
          {preflight?.can_activate && !confirmed ? (
            <button
              onClick={() => setConfirmed(true)}
              disabled={loading}
              style={{
                ...button.activate,
                ...(loading ? button.disabled : {}),
              }}
            >
              Activate now
            </button>
          ) : preflight?.can_activate && confirmed ? (
            <button
              onClick={handleActivate}
              disabled={activating}
              style={{
                ...button.activate,
                ...(activating ? button.disabled : {}),
              }}
            >
              {activating ? 'Activating…' : 'Yes, activate'}
            </button>
          ) : null}
        </div>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Local style overrides
// ---------------------------------------------------------------------------

const dialogPanel: React.CSSProperties = {
  ...dialog.panel(560),
  maxHeight: '80vh',
  display: 'flex',
  flexDirection: 'column',
};

const headerStyle: React.CSSProperties = {
  ...dialog.header,
  padding: '20px 24px 16px',
};

const bodyStyle: React.CSSProperties = {
  padding: '16px 24px',
  overflowY: 'auto',
  flex: 1,
};

const mutedCentered: React.CSSProperties = {
  color: tokens.textMuted,
  textAlign: 'center',
  padding: '24px',
};

const sectionStyle: React.CSSProperties = { marginBottom: '16px' };

const sectionTitleStyle: React.CSSProperties = {
  color: tokens.textSecondary,
  fontSize: '14px',
  fontWeight: 600,
  marginBottom: '8px',
};

const summaryStyle: React.CSSProperties = {
  color: tokens.textMuted,
  fontSize: '13px',
  marginBottom: '12px',
};

const groupStyle: React.CSSProperties = { marginBottom: '10px' };

const groupLabelStyle: React.CSSProperties = {
  color: tokens.textMuted,
  fontSize: '12px',
  fontWeight: 600,
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
  marginBottom: '6px',
};

const fieldListStyle: React.CSSProperties = {
  display: 'flex',
  flexWrap: 'wrap',
  gap: '4px',
};

const fieldChipStyle: React.CSSProperties = {
  backgroundColor: tokens.border,
  color: tokens.textSecondary,
  fontSize: '12px',
  padding: '2px 8px',
  borderRadius: '4px',
};

const warningSectionStyle: React.CSSProperties = {
  ...dialog.warningBox,
  borderRadius: '8px',
  padding: '12px 16px',
  marginBottom: '12px',
};

const warningItemStyle: React.CSSProperties = {
  color: '#ffcc66',
  fontSize: '13px',
  marginTop: '4px',
};

const footerStyle: React.CSSProperties = {
  ...dialog.footer,
  padding: '16px 24px',
};

const confirmSectionStyle: React.CSSProperties = {
  backgroundColor: 'rgba(43, 138, 62, 0.1)',
  borderRadius: '8px',
  padding: '12px 16px',
  marginTop: '12px',
  color: '#a0d0b0',
  fontSize: '14px',
  lineHeight: '1.5',
};
