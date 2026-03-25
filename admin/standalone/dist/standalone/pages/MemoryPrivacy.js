import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
/**
 * Memory & Privacy page — Standalone admin (WI #290).
 *
 * Provides configuration for:
 *   - Customer memory layer settings (Layers 1-4)
 *   - Data retention policies
 *   - GDPR consent management
 *   - PII scrubbing rules
 *
 * Uses the config API to read/write tenant configuration values.
 */
import { useState, useCallback, useEffect } from 'react';
import { Paper, Stack, Title, Text, Switch, Select, Slider, Button, Group, Accordion, Alert, Badge, SegmentedControl, NumberInput, } from '@mantine/core';
import { useAppContext } from '../layouts/StandaloneLayout';
import { useConfig, useUpdateConfig, useAutoSaveDraft } from '../../shared/hooks/index';
import { AutoSaveIndicator } from '../../shared/components/AutoSaveIndicator';
import { HelpTooltip } from '../../shared/HelpTooltip';
import { LoadingState } from '../../shared/LoadingState';
import { tokens } from '../../shared/theme/styles';
// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------
const ACTION_BLUE = tokens.action;
const RETENTION_OPTIONS = [
    { value: '30', label: '30 days' },
    { value: '90', label: '90 days' },
    { value: '180', label: '180 days' },
    { value: '365', label: '1 year' },
    { value: '730', label: '2 years' },
];
// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------
export const MemoryPrivacyPage = () => {
    const { apiFetch, onNotify, tenantContext, refreshActivationStatus } = useAppContext();
    const { data: fullConfig, loading, error } = useConfig(apiFetch);
    const { updateConfig, loading: saving } = useUpdateConfig(apiFetch);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const config = fullConfig?.config ?? {};
    // Local state for form values
    const [memoryEnabled, setMemoryEnabled] = useState(false);
    const [conversationMemory, setConversationMemory] = useState(true);
    const [crossSessionLearning, setCrossSessionLearning] = useState(false);
    const [retentionDays, setRetentionDays] = useState('90');
    const [piiScrubbing, setPiiScrubbing] = useState(true);
    const [consentRequired, setConsentRequired] = useState(true);
    const [autoDeleteOnRequest, setAutoDeleteOnRequest] = useState(true);
    const [patternDecayDays, setPatternDecayDays] = useState(90);
    const [identificationMode, setIdentificationMode] = useState('standard');
    // Sync from config when loaded (field names match backend config registry)
    useEffect(() => {
        if (config) {
            setMemoryEnabled(config.memory_enabled === true);
            setConversationMemory(config.conversation_memory !== false);
            setCrossSessionLearning(config.pattern_learning_enabled === true);
            setRetentionDays(String(config.data_retention_days ?? '90'));
            setPiiScrubbing(config.pii_scrubbing !== false);
            setConsentRequired(config.consent_collection_enabled !== false);
            setAutoDeleteOnRequest(config.auto_delete_on_request !== false);
            setPatternDecayDays(Number(config.pattern_decay_days ?? 90));
            setIdentificationMode(String(config.customer_identification_mode ?? 'standard'));
        }
    }, [config]);
    const tier = tenantContext?.tier ?? 'starter';
    const isProOrHigher = tier === 'professional' || tier === 'enterprise';
    const isEnterprise = tier === 'enterprise';
    // Fine-tuning inline config updates (Enterprise only, PCM Layer 4)
    const handleConfigChange = useCallback(async (key, value) => {
        const result = await updateConfig({ [key]: value });
        if (result?.success) {
            onNotify(`${key} updated.`, 'success');
        }
    }, [updateConfig, onNotify]);
    const handleSave = useCallback(async () => {
        // Field names must match backend config field registry.
        // Only include tier-gated fields when the tenant meets the gate.
        const updates = {
            memory_enabled: memoryEnabled,
            data_retention_days: parseInt(retentionDays, 10),
            pii_scrubbing: piiScrubbing,
            consent_collection_enabled: consentRequired,
            customer_identification_mode: identificationMode,
        };
        // Pro+ fields — only send when the tenant tier allows it
        if (isProOrHigher) {
            updates.pattern_learning_enabled = crossSessionLearning;
        }
        const result = await updateConfig(updates);
        if (result?.success) {
            refreshActivationStatus();
            return true;
        }
        else {
            // Surface the actual validation error from the hook, not a generic fallback
            const detail = result?.message
                || error
                || 'Failed to save settings. Please check your plan tier and try again.';
            onNotify(detail, 'error');
            return false;
        }
    }, [
        memoryEnabled, conversationMemory, crossSessionLearning, retentionDays,
        piiScrubbing, consentRequired, autoDeleteOnRequest, patternDecayDays,
        identificationMode, isProOrHigher, updateConfig, error, onNotify,
        refreshActivationStatus,
    ]);
    const { onBlur: autoSaveOnBlur, saveCount } = useAutoSaveDraft({ save: handleSave });
    // Loading state
    if (loading && !fullConfig) {
        return _jsx(LoadingState, { text: "Loading memory settings" });
    }
    // Error state
    if (error && !fullConfig) {
        return (_jsxs(Stack, { gap: "lg", children: [_jsx(Title, { order: 2, children: "Memory & privacy" }), _jsx(Alert, { color: "red", title: "Failed to load settings", children: error })] }));
    }
    return (_jsxs(Stack, { gap: "lg", onBlur: autoSaveOnBlur, children: [_jsxs("div", { children: [_jsxs(Group, { justify: "space-between", align: "center", children: [_jsx(Title, { order: 2, children: "Memory & privacy" }), _jsx(AutoSaveIndicator, { saveCount: saveCount })] }), _jsx(Text, { c: "dimmed", size: "sm", children: "Configure how your AI remembers customers and handles their data" })] }), !isProOrHigher && (_jsx(Alert, { color: "blue", variant: "light", title: "Unlock advanced memory features", children: _jsx(Text, { size: "sm", children: "Cross-session learning and dedicated model training are available on the Professional plan and above. Upgrade your plan to enable AI that learns and adapts to each customer over time." }) })), _jsxs(Paper, { radius: "md", withBorder: true, p: "lg", children: [_jsxs(Group, { justify: "space-between", mb: "md", children: [_jsxs(Group, { gap: "xs", children: [_jsx(Text, { fw: 600, size: "md", children: "Customer context" }), _jsx(Badge, { variant: "light", color: "green", size: "xs", children: "All tiers" })] }), _jsx(Switch, { checked: memoryEnabled, onChange: (e) => setMemoryEnabled(e.currentTarget.checked), color: ACTION_BLUE, label: memoryEnabled ? 'Enabled' : 'Disabled', labelPosition: "left" })] }), _jsx(Text, { c: "dimmed", size: "sm", mb: "xs", children: "Structured customer profiles (preferences, account state, interaction history) are injected into every conversation." }), _jsx(HelpTooltip, { text: "Customer context provides the AI with information about each customer's previous interactions, preferences, and account status. This enables personalized responses without customers having to repeat themselves.", docLink: "https://agentredcx.com/docs/admin-guide/customer-memory#how-the-layers-work" })] }), _jsxs(Paper, { radius: "md", withBorder: true, p: "lg", children: [_jsxs(Group, { justify: "space-between", mb: "md", children: [_jsxs(Group, { gap: "xs", children: [_jsx(Text, { fw: 600, size: "md", children: "Conversation memory" }), _jsx(Badge, { variant: "light", color: "green", size: "xs", children: "All tiers" })] }), _jsx(Switch, { checked: conversationMemory, onChange: (e) => setConversationMemory(e.currentTarget.checked), color: ACTION_BLUE, label: conversationMemory ? 'Enabled' : 'Disabled', labelPosition: "left", disabled: !memoryEnabled })] }), _jsx(Text, { c: "dimmed", size: "sm", mb: "xs", children: "Vectorized conversation transcripts enable semantic search across a customer's full interaction history." }), _jsx(HelpTooltip, { text: "Conversation memory stores previous chat transcripts as vector embeddings, allowing the AI to find and reference relevant past conversations. This helps provide consistent support across sessions.", docLink: "https://agentredcx.com/docs/admin-guide/customer-memory#memory-enabled" })] }), _jsxs(Paper, { radius: "md", withBorder: true, p: "lg", children: [_jsxs(Group, { justify: "space-between", mb: "md", children: [_jsxs(Group, { gap: "xs", children: [_jsx(Text, { fw: 600, size: "md", children: "Cross-session learning" }), isProOrHigher ? (_jsx(Badge, { variant: "light", color: "blue", size: "xs", children: "Professional+" })) : (_jsx(Badge, { variant: "light", color: "gray", size: "xs", children: "Professional+ required" }))] }), _jsx(Switch, { checked: crossSessionLearning, onChange: (e) => setCrossSessionLearning(e.currentTarget.checked), color: ACTION_BLUE, label: crossSessionLearning ? 'Enabled' : 'Disabled', labelPosition: "left", disabled: !memoryEnabled || !isProOrHigher })] }), _jsx(Text, { c: "dimmed", size: "sm", mb: "xs", children: "The AI extracts and persists behavioral patterns, communication preferences, and interaction styles across sessions." }), _jsx(HelpTooltip, { text: "Cross-session learning observes how each customer communicates over time \u2014 tone, vocabulary, topic patterns \u2014 and adapts future responses to match. Learned patterns decay gradually so the AI stays responsive to changing behavior.", docLink: "https://agentredcx.com/docs/admin-guide/customer-memory#pattern-learning" }), isProOrHigher && crossSessionLearning && (_jsxs("div", { style: { marginTop: 12 }, children: [_jsx(Text, { size: "sm", fw: 500, mb: 4, children: "Pattern decay (days)" }), _jsx(Slider, { value: patternDecayDays, onChange: setPatternDecayDays, min: 30, max: 365, step: 30, marks: [
                                    { value: 30, label: '30' },
                                    { value: 90, label: '90' },
                                    { value: 180, label: '180' },
                                    { value: 365, label: '365' },
                                ], color: ACTION_BLUE, mb: "md", disabled: !memoryEnabled }), _jsx(HelpTooltip, { text: "How long learned patterns remain active before decaying. Shorter values keep the AI more responsive to behavior changes; longer values provide more stable personalization.", docLink: "https://agentredcx.com/docs/admin-guide/customer-memory#pattern-learning" })] }))] }), _jsxs(Paper, { radius: "md", withBorder: true, p: "lg", children: [_jsxs(Group, { justify: "space-between", mb: "md", children: [_jsxs(Group, { gap: "xs", children: [_jsx(Text, { fw: 600, size: "md", children: "Dedicated model training" }), isEnterprise ? (_jsx(Badge, { variant: "light", color: "grape", size: "xs", children: "Enterprise add-on" })) : (_jsx(Badge, { variant: "light", color: "gray", size: "xs", children: "Enterprise required" }))] }), isEnterprise && (_jsx(Switch, { label: "Enable fine-tuning", checked: config?.fineTuningEnabled ?? false, onChange: (e) => handleConfigChange('fineTuningEnabled', e.currentTarget.checked), color: ACTION_BLUE }))] }), _jsx(Text, { c: "dimmed", size: "sm", mb: "xs", children: "Per-customer AI fine-tuning on 1,000+ historical interactions for maximum personalization. Available as an Enterprise add-on ($299/month)." }), _jsx(HelpTooltip, { text: "Dedicated model training creates a custom AI model for each customer using their historical interactions. This provides the highest level of personalization but requires a large conversation history (1,000+ interactions) and is billed as a separate Enterprise add-on.", docLink: "https://agentredcx.com/docs/admin-guide/customer-memory#dedicated-model-training" }), !isEnterprise && (_jsx(Alert, { color: "blue", variant: "light", mt: "md", children: _jsx(Text, { size: "sm", children: "Upgrade to Enterprise tier to access dedicated model training." }) })), isEnterprise && config?.fineTuningEnabled && (_jsxs(Stack, { mt: "md", gap: "md", children: [_jsx(SegmentedControl, { value: config?.fineTuningSchedule ?? 'monthly', onChange: (val) => handleConfigChange('fineTuningSchedule', val), fullWidth: true, data: [
                                    { value: 'monthly', label: 'Monthly' },
                                    { value: 'weekly', label: 'Weekly' },
                                    { value: 'manual', label: 'Manual only' },
                                ], color: ACTION_BLUE }), _jsx(Text, { size: "xs", c: "dimmed", children: "Training schedule \u2014 how often the pipeline runs automatically." }), _jsx(NumberInput, { label: "Minimum conversations", description: "Minimum conversation count before training is eligible", value: config?.fineTuningMinConversations ?? 1000, onChange: (val) => handleConfigChange('fineTuningMinConversations', val), min: 100, max: 10000, step: 100 }), _jsx(Button, { variant: "light", color: ACTION_BLUE, onClick: () => {
                                    apiFetch('/api/admin/fine-tuning/trigger', { method: 'POST' })
                                        .then((r) => r.json())
                                        .then(() => onNotify('Fine-tuning pipeline started.', 'success'))
                                        .catch(() => onNotify('Failed to trigger training.', 'error'));
                                }, children: "Trigger training now" }), config?.fineTuningActiveModelId && (_jsx(Alert, { color: "green", variant: "light", children: _jsxs(Text, { size: "sm", children: ["Active model: ", config.fineTuningActiveModelId, " (v", config.fineTuningActiveModelVersion, ")"] }) }))] }))] }), _jsxs(Paper, { radius: "md", withBorder: true, p: "lg", children: [_jsx(Group, { justify: "space-between", mb: "md", children: _jsxs(Group, { gap: "xs", children: [_jsx(Text, { fw: 600, size: "md", children: "Customer identification" }), _jsx(Badge, { variant: "light", color: "green", size: "xs", children: "All tiers" })] }) }), _jsx(Text, { c: "dimmed", size: "sm", mb: "md", children: "Controls how aggressively the AI prompts anonymous visitors to identify themselves (log in or provide an email). Identified customers get richer memory and personalization." }), _jsx(SegmentedControl, { value: identificationMode, onChange: setIdentificationMode, fullWidth: true, data: [
                            { value: 'off', label: 'Off' },
                            { value: 'gentle', label: 'Gentle' },
                            { value: 'standard', label: 'Standard' },
                            { value: 'aggressive', label: 'Aggressive' },
                        ], color: ACTION_BLUE, mb: "sm", disabled: !memoryEnabled }), _jsxs(Text, { size: "xs", c: "dimmed", children: [identificationMode === 'off' && 'No identification prompt. The AI will not ask visitors to log in or provide contact information.', identificationMode === 'gentle' && 'Casual mention. The AI may casually note that logging in helps with personalization, but will not push.', identificationMode === 'standard' && 'Standard prompt. The AI\'s first response suggests logging in or providing an email to access order history and personalized support.', identificationMode === 'aggressive' && 'Strong prompt. The AI\'s first response includes a clear authentication suggestion and asks probing questions about interests and recent orders.'] }), !memoryEnabled && (_jsx(Alert, { color: "yellow", variant: "light", mt: "sm", children: _jsx(Text, { size: "xs", children: "Enable customer context above to use identification prompts." }) })), _jsx(HelpTooltip, { text: "Customer identification helps your AI build richer memory profiles. When customers identify themselves, the AI can access their order history, preferences, and past interactions \u2014 enabling more personalized and effective support.", docLink: "https://agentredcx.com/docs/admin-guide/customer-memory#identification" })] }), _jsx(Accordion, { variant: "separated", radius: "md", defaultValue: "privacy", children: _jsxs(Accordion.Item, { value: "privacy", children: [_jsx(Accordion.Control, { children: _jsxs(Group, { gap: "xs", children: [_jsx(Text, { fw: 600, size: "md", children: "Data retention & privacy" }), _jsx(HelpTooltip, { text: "Controls how long customer conversation data is stored, whether personally identifiable information is automatically redacted, and how GDPR data requests are handled. These settings apply to all customers on your account.", docLink: "https://agentredcx.com/docs/admin-guide/data-retention" })] }) }), _jsx(Accordion.Panel, { children: _jsxs(Stack, { gap: "md", children: [_jsx(Select, { label: "Data retention period", description: "How long conversation data is retained before automatic deletion.", value: retentionDays, onChange: (val) => setRetentionDays(val ?? '90'), data: RETENTION_OPTIONS, allowDeselect: false }), _jsx(Switch, { label: "PII scrubbing", description: "Automatically detect and redact personally identifiable information (emails, phone numbers, addresses) from stored conversations.", checked: piiScrubbing, onChange: (e) => setPiiScrubbing(e.currentTarget.checked), color: ACTION_BLUE }), _jsx(Switch, { label: "Consent required", description: "Require explicit customer consent before storing conversation data. A consent prompt appears at the start of each conversation.", checked: consentRequired, onChange: (e) => setConsentRequired(e.currentTarget.checked), color: ACTION_BLUE }), _jsx(Switch, { label: "Automatic deletion on request", description: "Automatically delete all customer data when a GDPR deletion request is received.", checked: autoDeleteOnRequest, onChange: (e) => setAutoDeleteOnRequest(e.currentTarget.checked), color: ACTION_BLUE })] }) })] }) })] }));
};
//# sourceMappingURL=MemoryPrivacy.js.map