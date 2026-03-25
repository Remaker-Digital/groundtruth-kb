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
// Config + Named Configs + Appearances + Activation
export { useConfig, useConfigSchema, useConfigVersions, useUpdateConfig, useRotateWidgetKey, useNamedConfigs, useSaveNamedConfig, useActivateNamedConfig, useDeleteNamedConfig, useWidgetAppearances, useSaveWidgetAppearance, useActivateWidgetAppearance, useDeleteWidgetAppearance, useActivationStatus, useDraftState, useActivateDraft, useDiscardDraft, useRestorePrevious, } from './useConfig';
// Inbox
export { useInboxConversations, useConversationMessages, useAssignConversation, useSearchConversations, useEscalateConversation, useResolveConversation, useArchiveConversation, useConversationTrace, } from './useInbox';
// Knowledge Base
export { useKnowledgeBase, useKBArticle, useSaveKBArticle, useUploadFile, useImportUrl, useExportCSV, useStalenessSummary, useStaleEntries, useVerifyEntry, useConflictScan, } from './useKnowledge';
// Analytics + Usage
export { useUsageDashboard, useDailyVolume, useConversationList, useAnalyticsSummary, useIntentBreakdown, useKnowledgeGaps, } from './useAnalytics';
// Avatar
export { useAvatarUpload, useDeleteAvatar } from './useAvatar';
// Team + Billing + Integrations
export { useTeamMembers, useInviteTeamMember, useBillingStatus, usePackBalance, useIntegrations, useIntegrationDetail, useActivateIntegration, useDeactivateIntegration, useDisconnectIntegration, } from './useAdmin';
// Ingestion (KA-7: Knowledge Automation)
export { useIngestionStatus, useTemplates, useStartIngestion, useCancelIngestion, useApplyTemplate, } from './useIngestion';
// Config Suggestions (KA-7: Knowledge Automation)
export { useConfigSuggestions } from './useSuggestions';
// Website Sources (automated website crawling)
export { useWebsiteSources, useCreateWebsiteSource, useUpdateWebsiteSource, useDeleteWebsiteSource, useTriggerCrawl, } from './useWebsiteSources';
// Auto-save draft (focusout-driven)
export { useAutoSaveDraft } from './useAutoSaveDraft';
//# sourceMappingURL=index.js.map