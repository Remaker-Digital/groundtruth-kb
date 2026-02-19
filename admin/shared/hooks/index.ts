/**
 * Shared React hooks — re-export barrel.
 *
 * All hooks now live in domain-specific files under this directory.
 * This file re-exports every public name so that existing imports like:
 *
 *   import { useConfig } from '../../shared/hooks/index';
 *
 * continue to work without modification.
 *
 * For new code, prefer importing from the domain file directly:
 *
 *   import { useConfig } from '../../shared/hooks/useConfig';
 *
 * R6 refactoring — session 34.
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

// Core
export { useApi, usePolling } from './useApi';
export type { ApiFetch, UseApiResult } from './useApi';

// Config + Named Configs + Appearances + Activation
export {
  useConfig,
  useConfigSchema,
  useConfigVersions,
  useUpdateConfig,
  useNamedConfigs,
  useSaveNamedConfig,
  useActivateNamedConfig,
  useDeleteNamedConfig,
  useWidgetAppearances,
  useSaveWidgetAppearance,
  useActivateWidgetAppearance,
  useDeleteWidgetAppearance,
  useActivationStatus,
  useDraftState,
  useActivateDraft,
  useDiscardDraft,
  useRestorePrevious,
} from './useConfig';
export type {
  NamedConfigSummary,
  ActivationStatus,
  DraftState,
} from './useConfig';

// Inbox
export {
  useInboxConversations,
  useConversationMessages,
  useAssignConversation,
  useSearchConversations,
  useEscalateConversation,
  useResolveConversation,
  useArchiveConversation,
} from './useInbox';
export type { SearchResult } from './useInbox';

// Knowledge Base
export {
  useKnowledgeBase,
  useKBArticle,
  useSaveKBArticle,
  useUploadFile,
  useImportUrl,
  useExportCSV,
  useStalenessSummary,
  useStaleEntries,
  useVerifyEntry,
  useConflictScan,
} from './useKnowledge';
export type {
  StalenessSummary,
  StalenessScore,
  ConflictPair,
  ScanResult,
} from './useKnowledge';

// Analytics + Usage
export {
  useUsageDashboard,
  useDailyVolume,
  useConversationList,
  useAnalyticsSummary,
  useIntentBreakdown,
  useKnowledgeGaps,
} from './useAnalytics';
export type { TestModeFilter, AnalyticsPeriod } from './useAnalytics';

// Avatar
export { useAvatarUpload, useDeleteAvatar } from './useAvatar';
export type { AvatarUploadResult, AvatarDeleteResult } from './useAvatar';

// Team + Billing + Integrations
export {
  useTeamMembers,
  useInviteTeamMember,
  useBillingStatus,
  usePackBalance,
  useIntegrations,
  useIntegrationDetail,
  useActivateIntegration,
  useDeactivateIntegration,
  useDisconnectIntegration,
} from './useAdmin';
