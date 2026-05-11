/**
 * Team sub-component barrel — re-exports all extracted TeamManager pieces.
 *
 * (c) 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

// Types
export type {
  ThemePalette,
  TeamStyles,
  RoleDef,
  InviteFormProps,
  TeamMemberRowProps,
  ConfirmRemoveDialogProps,
  EditMemberDialogProps,
  RoleTooltipProps,
} from './types';

// Constants
export {
  ROLES,
  INVITABLE_ROLES,
  ROLE_COLORS_LIGHT,
  ROLE_COLORS_DARK,
  getRoleColors,
  STATUS_DISPLAY,
  LIGHT_PALETTE,
  DARK_PALETTE,
  getPalette,
  getRoleLabel,
} from './constants';

// Utils & hooks
export { formatDate, formatRelativeDate, useIsDark } from './utils';

// Styles
export { makeStyles } from './styles';

// Components
export { InviteForm } from './InviteForm';
export { TeamMemberRow } from './TeamMemberRow';
export { ConfirmRemoveDialog } from './ConfirmRemoveDialog';
export { EditMemberDialog } from './EditMemberDialog';
export { RoleTooltip } from './RoleTooltip';
