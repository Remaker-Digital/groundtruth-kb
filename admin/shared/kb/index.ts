/**
 * Knowledge Base sub-components barrel export.
 *
 * Re-exports all extracted presentational components, style constants,
 * and utility functions used by KnowledgeBaseManager.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

// Style constants & helpers
export {
  BRAND_PRIMARY,
  COLOR_SUCCESS,
  COLOR_DANGER,
  COLOR_GRAY,
  COLOR_LIGHT_GRAY,
  COLOR_BORDER,
  COLOR_WHITE,
  COLOR_TEXT,
  COLOR_TEXT_SECONDARY,
  COLOR_WARNING,
  FONT_FAMILY,
  BORDER_RADIUS,
  STATUS_BADGE_STYLES,
  STALENESS_BADGE_STYLES,
  inputStyle,
  buttonStyle,
} from './styles';

// Utilities
export { formatDate, extractCategories } from './utils';

// Components
export { KBStatusBadge } from './KBStatusBadge';
export type { KBStatusBadgeProps } from './KBStatusBadge';

export { KBStalenessBadge } from './KBStalenessBadge';
export type { KBStalenessBadgeProps } from './KBStalenessBadge';

export { FileUploadZone } from './FileUploadZone';
export type { FileUploadZoneProps } from './FileUploadZone';

export { URLImportForm } from './URLImportForm';
export type { URLImportFormProps } from './URLImportForm';

export { UploadResultDisplay } from './UploadResultDisplay';
export type { UploadResultDisplayProps } from './UploadResultDisplay';

export { ArticleEditor } from './ArticleEditor';
export type { ArticleEditorProps } from './ArticleEditor';

export { ArticleRow } from './ArticleRow';
export type { ArticleRowProps } from './ArticleRow';

export { LoadingSpinner } from './LoadingSpinner';
export type { LoadingSpinnerProps } from './LoadingSpinner';

export { EmptyState } from './EmptyState';
export type { EmptyStateProps } from './EmptyState';

export { ErrorBanner } from './ErrorBanner';
export type { ErrorBannerProps } from './ErrorBanner';

export { WebsiteSourcesPanel } from './WebsiteSourcesPanel';
export type { WebsiteSourcesPanelProps } from './WebsiteSourcesPanel';
