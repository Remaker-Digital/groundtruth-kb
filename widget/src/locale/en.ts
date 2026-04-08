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
  connectionFailed: string;
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
  preChatSkip: string;
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
  fieldInvalidPhone: string;
  fileTooLarge: string;
  fileUploading: string;
  reportIssue: string;
  issueReportTitle: string;
  issueReportDescription: string;
  issueTypeWrongInfo: string;
  issueTypeRudeResponse: string;
  issueTypeNotHelpful: string;
  issueTypeOther: string;
  issueDetailsPlaceholder: string;
  issueSubmit: string;
  issueSubmitting: string;
  issueSubmitSuccess: string;
  issueCancel: string;
  issueDone: string;
  otpPrompt: string;
  otpVerify: string;
  otpResend: string;
  otpSkip: string;
  otpInvalid: string;
  phoneOtpPrompt: string;
  phoneOtpResend: string;
  phoneOtpInvalid: string;
  consentPrompt: string;
  consentAccept: string;
  consentDecline: string;
  // Phase 2 (S254) — WCAG AA + locale completeness
  openChat: string;
  closeChat: string;
  chatImageAlt: string;
  logoAlt: string;
  headerSubtitleDefault: string;
  statusOnline: string;
  feedbackHelpful: string;
  feedbackNotHelpful: string;
  messageRevised: string;
  previousConversation: string;
  iframeTitleChat: string;
  conversationMessages: string;
  unreadMessages: string;
  defaultAgentName: string;
  poweredByPrefix: string;
  poweredByBrand: string;
  offlineFormName: string;
  offlineFormEmail: string;
  offlineFormMessage: string;
  errorStartConversation: string;
  errorSendMessage: string;
  errorGeneric: string;
  escalationNotice: string;
  waitForResponse: string;
  sseRetractFallback: string;
  sseErrorFallback: string;
  // Phase 3 (S256) — connection recovery + restore UX
  reconnectingAttempt: string;
  connectionFailedPermanent: string;
  retryConnection: string;
  dismissError: string;
  restoringConversation: string;
}

export const en: Locale = {
  headerTitle: 'Chat with us',
  inputPlaceholder: 'Type your message...',
  sendButton: 'Send',
  offlineMessage: 'Our team is currently offline. Our AI assistant is available to help you now.',
  typingIndicator: 'is typing',
  connectionLost: 'Connection lost. Reconnecting...',
  connectionFailed: 'Unable to connect. Please try again.',
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
  preChatSkip: 'Continue as guest',
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
  fieldInvalidPhone: 'Please enter a valid phone number (e.g. +15551234567)',
  fileTooLarge: 'File must be under 10MB',
  fileUploading: 'Uploading...',
  reportIssue: 'Report an issue',
  issueReportTitle: 'Report an Issue',
  issueReportDescription: 'Let us know if something went wrong with this conversation.',
  issueTypeWrongInfo: 'Wrong information',
  issueTypeRudeResponse: 'Rude response',
  issueTypeNotHelpful: 'Not helpful',
  issueTypeOther: 'Other',
  issueDetailsPlaceholder: 'Please describe the issue...',
  issueSubmit: 'Submit Report',
  issueSubmitting: 'Submitting...',
  issueSubmitSuccess: 'Thank you! Your report has been submitted.',
  issueCancel: 'Cancel',
  issueDone: 'Done',
  otpPrompt: 'Enter the code we sent to your email.',
  otpVerify: 'Verify',
  otpResend: 'Resend code',
  otpSkip: 'Continue without verifying',
  otpInvalid: 'Invalid code. Please try again.',
  phoneOtpPrompt: 'Enter the code we sent to your phone.',
  phoneOtpResend: 'Resend SMS code',
  phoneOtpInvalid: 'Invalid code. Please check your SMS and try again.',
  consentPrompt: 'We use your conversation history to provide personalized support. You can change this at any time.',
  consentAccept: 'Allow',
  consentDecline: 'No thanks',
  // Phase 2 (S254) — WCAG AA + locale completeness
  openChat: 'Open chat',
  closeChat: 'Close chat',
  chatImageAlt: 'Chat',
  logoAlt: 'Logo',
  headerSubtitleDefault: 'We typically reply within minutes',
  statusOnline: 'Online',
  feedbackHelpful: 'Helpful',
  feedbackNotHelpful: 'Not helpful',
  messageRevised: 'Message revised',
  previousConversation: 'Previous conversation',
  iframeTitleChat: 'Agent Red Chat',
  conversationMessages: 'Conversation messages',
  unreadMessages: 'unread messages',
  defaultAgentName: 'AI Assistant',
  poweredByPrefix: 'Powered by',
  poweredByBrand: 'Agent Red',
  offlineFormName: 'Name',
  offlineFormEmail: 'Email',
  offlineFormMessage: 'Message',
  errorStartConversation: 'Failed to start conversation',
  errorSendMessage: 'Failed to send message',
  errorGeneric: 'An error occurred',
  escalationNotice: 'This conversation has been transferred to a human agent. Please wait for a support team member to respond.',
  waitForResponse: 'Please wait for the current response to complete',
  sseRetractFallback: 'I apologize, but I need to rephrase my response. How else can I help you?',
  sseErrorFallback: 'An error occurred',
  // Phase 3 (S256) — connection recovery + restore UX
  reconnectingAttempt: 'Reconnecting... attempt {n}',
  connectionFailedPermanent: 'Unable to connect',
  retryConnection: 'Retry',
  dismissError: 'Dismiss',
  restoringConversation: 'Loading previous conversation...',
};
