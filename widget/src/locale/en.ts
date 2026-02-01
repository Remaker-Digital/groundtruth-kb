/**
 * English locale strings for the chat widget.
 *
 * All user-visible text is defined here so that:
 *   1. A translator can add new locale files without touching components
 *   2. Merchant overrides (widget_header_text, widget_input_placeholder)
 *      replace specific keys at runtime
 *   3. Content is cleanly separated from behavior and styling
 *
 * © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
 */

export interface Locale {
  headerTitle: string;
  inputPlaceholder: string;
  sendButton: string;
  offlineMessage: string;
  typingIndicator: string;
  connectionLost: string;
  connectionRestored: string;
  poweredBy: string;
  closeWidget: string;
  minimizeWidget: string;
  attachFile: string;
  ratingPrompt: string;
  ratingThankYou: string;
  ratingCommentPlaceholder: string;
  preChatTitle: string;
  preChatSubmit: string;
  offlineFormTitle: string;
  offlineFormSubmit: string;
  offlineFormSuccess: string;
  newConversation: string;
  endConversation: string;
  scrollToBottom: string;
  today: string;
  yesterday: string;
  fieldRequired: string;
  fieldInvalidEmail: string;
  fileTooLarge: string;
  fileUploading: string;
}

export const en: Locale = {
  headerTitle: 'Chat with us',
  inputPlaceholder: 'Type a message...',
  sendButton: 'Send',
  offlineMessage: 'Our team is currently offline. Our AI assistant is available to help you now.',
  typingIndicator: 'is typing',
  connectionLost: 'Connection lost. Reconnecting...',
  connectionRestored: 'Connected',
  poweredBy: 'Powered by Agent Red',
  closeWidget: 'Close chat',
  minimizeWidget: 'Minimize',
  attachFile: 'Attach file',
  ratingPrompt: 'Was this conversation helpful?',
  ratingThankYou: 'Thank you for your feedback!',
  ratingCommentPlaceholder: 'Any additional comments? (optional)',
  preChatTitle: 'Before we start',
  preChatSubmit: 'Start chat',
  offlineFormTitle: 'Leave us a message',
  offlineFormSubmit: 'Send message',
  offlineFormSuccess: 'Message sent! We\'ll get back to you soon.',
  newConversation: 'New conversation',
  endConversation: 'End conversation',
  scrollToBottom: 'Scroll to latest',
  today: 'Today',
  yesterday: 'Yesterday',
  fieldRequired: 'This field is required',
  fieldInvalidEmail: 'Please enter a valid email',
  fileTooLarge: 'File must be under 10MB',
  fileUploading: 'Uploading...',
};
