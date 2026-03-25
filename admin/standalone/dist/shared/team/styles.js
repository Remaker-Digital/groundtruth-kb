/**
 * TeamManager styles — theme-aware style factory.
 *
 * Extracted from TeamManager.tsx. Produces a complete style map from a
 * ThemePalette + dark flag, consumed by all team sub-components.
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */
import { getRoleColors } from './constants';
import { tokens } from '../theme/styles';
// ---------------------------------------------------------------------------
// Style factory
// ---------------------------------------------------------------------------
export function makeStyles(p, dark = false) {
    const ROLE_COLORS = getRoleColors(dark);
    return {
        container: {
            fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
        },
        // Table
        table: {
            width: '100%',
            borderCollapse: 'collapse',
        },
        th: {
            textAlign: 'left',
            fontSize: 12,
            fontWeight: 600,
            color: p.textSecondary,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            padding: '8px 12px',
            borderBottom: `2px solid ${p.border}`,
        },
        td: {
            padding: '12px',
            borderBottom: `1px solid ${p.borderSubtle}`,
            fontSize: 14,
            color: p.textPrimary,
            verticalAlign: 'middle',
        },
        tr: (isDisabled) => ({
            opacity: isDisabled ? 0.55 : 1,
        }),
        // Member info
        memberInfo: {
            display: 'flex',
            flexDirection: 'column',
            gap: 2,
        },
        memberName: {
            fontSize: 14,
            fontWeight: 600,
            color: p.textPrimary,
        },
        memberEmail: {
            fontSize: 13,
            color: p.textSecondary,
        },
        // Badges
        roleBadge: (role) => ({
            display: 'inline-block',
            padding: '2px 10px',
            borderRadius: 12,
            fontSize: 12,
            fontWeight: 600,
            background: (ROLE_COLORS[role] || ROLE_COLORS.viewer).bg,
            color: (ROLE_COLORS[role] || ROLE_COLORS.viewer).text,
        }),
        statusDot: (_color) => ({
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6,
            fontSize: 13,
            color: p.textTertiary,
        }),
        dot: (color) => ({
            width: 8,
            height: 8,
            borderRadius: '50%',
            background: color,
            flexShrink: 0,
        }),
        // Dates
        dateText: {
            fontSize: 13,
            color: p.textSecondary,
        },
        // Actions
        actionRow: {
            display: 'flex',
            gap: 6,
        },
        iconButton: {
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: 28,
            height: 28,
            borderRadius: 6,
            border: `1px solid ${p.border}`,
            background: p.hoverBg,
            color: p.textSecondary,
            cursor: 'pointer',
            outline: 'none',
            transition: 'all 0.15s ease',
        },
        // Invite form
        formRow: {
            display: 'flex',
            gap: 12,
            alignItems: 'flex-end',
            flexWrap: 'wrap',
        },
        formField: {
            display: 'flex',
            flexDirection: 'column',
            gap: 4,
            flex: 1,
            minWidth: 180,
        },
        formLabel: {
            fontSize: 13,
            fontWeight: 600,
            color: p.textTertiary,
        },
        input: {
            padding: '8px 12px',
            fontSize: 14,
            border: `1px solid ${p.inputBorder}`,
            borderRadius: 6,
            color: p.textPrimary,
            background: p.inputBg,
            outline: 'none',
            boxSizing: 'border-box',
            width: '100%',
        },
        select: {
            padding: '8px 12px',
            fontSize: 14,
            border: `1px solid ${p.inputBorder}`,
            borderRadius: 6,
            color: p.textPrimary,
            background: p.inputBg,
            outline: 'none',
            boxSizing: 'border-box',
            width: '100%',
            cursor: 'pointer',
        },
        inviteButton: {
            padding: '8px 20px',
            fontSize: 14,
            fontWeight: 600,
            borderRadius: 6,
            whiteSpace: 'nowrap',
            height: 38,
        },
        inviteButtonDisabled: {
            opacity: 0.5,
            cursor: 'not-allowed',
        },
        // Confirmation modal
        overlay: {
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: p.overlayBg,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 10000,
        },
        modal: {
            background: p.modalBg,
            borderRadius: 12,
            padding: 24,
            width: 420,
            maxWidth: '90vw',
            boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
            border: `1px solid ${p.border}`,
        },
        modalTitle: {
            fontSize: 16,
            fontWeight: 600,
            color: p.textPrimary,
            margin: '0 0 8px 0',
        },
        modalBody: {
            fontSize: 14,
            color: p.textTertiary,
            lineHeight: 1.5,
            margin: '0 0 20px 0',
        },
        modalActions: {
            display: 'flex',
            justifyContent: 'flex-end',
            gap: 8,
        },
        modalCancel: {
            padding: '8px 16px',
            fontSize: 14,
            fontWeight: 500,
            background: p.hoverBg,
            color: p.textTertiary,
            border: `1px solid ${p.border}`,
            borderRadius: 6,
            cursor: 'pointer',
        },
        modalConfirm: {
            padding: '8px 16px',
            fontSize: 14,
            fontWeight: 600,
            background: tokens.danger,
            color: tokens.white,
            border: 'none',
            borderRadius: 6,
            cursor: 'pointer',
        },
        // Edit modal
        editModal: {
            background: p.modalBg,
            borderRadius: 12,
            padding: 24,
            width: 460,
            maxWidth: '90vw',
            boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
            border: `1px solid ${p.border}`,
        },
        editSaveButton: {
            padding: '8px 20px',
            fontSize: 14,
            fontWeight: 600,
            background: tokens.action,
            color: tokens.white,
            border: 'none',
            borderRadius: 6,
            cursor: 'pointer',
        },
        // Empty & loading
        loadingContainer: {
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: 48,
            color: p.textSecondary,
            fontSize: 14,
        },
        errorContainer: {
            padding: 24,
            background: dark ? '#371520' : '#FEF2F2',
            border: `1px solid ${dark ? '#5C2030' : '#FECACA'}`,
            borderRadius: 8,
            color: dark ? '#FCA5A5' : '#991B1B',
            fontSize: 14,
            textAlign: 'center',
        },
        retryButton: {
            marginTop: 12,
            padding: '6px 16px',
            background: dark ? '#B91C1C' : '#DC2626',
            color: tokens.white,
            border: 'none',
            borderRadius: 4,
            fontSize: 13,
            fontWeight: 600,
            cursor: 'pointer',
        },
        emptyState: {
            padding: 48,
            textAlign: 'center',
            color: p.textSecondary,
            fontSize: 14,
        },
    };
}
//# sourceMappingURL=styles.js.map