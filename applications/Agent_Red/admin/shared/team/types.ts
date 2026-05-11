// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * TeamManager sub-component types.
 *
 * Shared interfaces for the extracted team management components.
 * Re-exports relevant types from the parent types module for convenience.
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

import type React from 'react';
import type { TeamMember, TeamRole } from '../types';

// Re-export for convenience so sub-components don't need double imports
export type { TeamMember, TeamRole };

// ---------------------------------------------------------------------------
// Theme palette — used by all sub-components for dark/light mode styling
// ---------------------------------------------------------------------------

export interface ThemePalette {
  surface: string;       // card / container background
  border: string;        // borders
  borderSubtle: string;  // subtle row separators
  textPrimary: string;   // primary text
  textSecondary: string; // secondary / muted text
  textTertiary: string;  // labels, column headers
  inputBg: string;       // form inputs
  inputBorder: string;   // form input borders
  hoverBg: string;       // hover backgrounds
  modalBg: string;       // modal background
  overlayBg: string;     // modal overlay
}

// ---------------------------------------------------------------------------
// Style map — return type of makeStyles()
// ---------------------------------------------------------------------------

export interface TeamStyles {
  container: React.CSSProperties;
  table: React.CSSProperties;
  th: React.CSSProperties;
  td: React.CSSProperties;
  tr: (isDisabled: boolean) => React.CSSProperties;
  memberInfo: React.CSSProperties;
  memberName: React.CSSProperties;
  memberEmail: React.CSSProperties;
  roleBadge: (role: string) => React.CSSProperties;
  statusDot: (color: string) => React.CSSProperties;
  dot: (color: string) => React.CSSProperties;
  dateText: React.CSSProperties;
  actionRow: React.CSSProperties;
  iconButton: React.CSSProperties;
  formRow: React.CSSProperties;
  formField: React.CSSProperties;
  formLabel: React.CSSProperties;
  input: React.CSSProperties;
  select: React.CSSProperties;
  inviteButton: React.CSSProperties;
  inviteButtonDisabled: React.CSSProperties;
  overlay: React.CSSProperties;
  modal: React.CSSProperties;
  modalTitle: React.CSSProperties;
  modalBody: React.CSSProperties;
  modalActions: React.CSSProperties;
  modalCancel: React.CSSProperties;
  modalConfirm: React.CSSProperties;
  editModal: React.CSSProperties;
  editSaveButton: React.CSSProperties;
  loadingContainer: React.CSSProperties;
  errorContainer: React.CSSProperties;
  retryButton: React.CSSProperties;
  emptyState: React.CSSProperties;
}

// ---------------------------------------------------------------------------
// Role definition
// ---------------------------------------------------------------------------

export interface RoleDef {
  value: TeamRole;
  label: string;
  description: string;
}

// ---------------------------------------------------------------------------
// Sub-component prop interfaces
// ---------------------------------------------------------------------------

export interface InviteFormProps {
  styles: TeamStyles;
  palette: ThemePalette;
  inviteEmail: string;
  inviteName: string;
  inviteRole: TeamRole;
  inviteDomainTags: string[];
  inviting: boolean;
  inviteError: string | null;
  onEmailChange: (value: string) => void;
  onNameChange: (value: string) => void;
  onRoleChange: (value: TeamRole) => void;
  onDomainTagsChange: (tags: string[]) => void;
  onInvite: () => void;
}

export interface TeamMemberRowProps {
  member: TeamMember;
  styles: TeamStyles;
  palette: ThemePalette;
  isDark: boolean;
  onRoleChange: (member: TeamMember, newRole: TeamRole) => void;
  onCategoryToggle: (member: TeamMember, categoryId: string) => void;
  /** WI #280: Toggle active/inactive status for a team member. */
  onToggleActive: (member: TeamMember) => void;
  /** Phase 4c: Open edit dialog for domain tags and other settings. */
  onEdit: (member: TeamMember) => void;
  onRemove: (member: TeamMember) => void;
}

export interface ConfirmRemoveDialogProps {
  member: TeamMember;
  styles: TeamStyles;
  actionLoading: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export interface EditMemberDialogProps {
  member: TeamMember;
  styles: TeamStyles;
  palette: ThemePalette;
  isDark: boolean;
  editRole: TeamRole;
  editCategories: string[];
  editDomainTags: string[];
  editLoading: boolean;
  onRoleChange: (value: TeamRole) => void;
  onCategoriesChange: (categories: string[]) => void;
  onDomainTagsChange: (tags: string[]) => void;
  onSave: () => void;
  onCancel: () => void;
}

export interface RoleTooltipProps {
  isDark: boolean;
  onMouseEnter: () => void;
  onMouseLeave: () => void;
}
