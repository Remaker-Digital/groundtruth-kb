// © 2026 Remaker Digital, a DBA of VanDusen & Palmeter, LLC. All rights reserved.
// Mock data for Agent Red Customer Experience Admin Dashboard Prototype

// ============================================================================
// TYPES
// ============================================================================

export interface Conversation {
  id: string;
  customerName: string;
  customerEmail: string;
  customerAvatar: string;
  subject: string;
  lastMessage: string;
  status: 'active' | 'waiting' | 'resolved' | 'escalated';
  channel: 'chat' | 'email';
  assignedTo: string | null;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  createdAt: string;
  updatedAt: string;
  messageCount: number;
  tags: string[];
  sentiment: 'positive' | 'neutral' | 'negative';
  memoryLayers: number[];
}

export interface Message {
  id: string;
  conversationId: string;
  sender: 'customer' | 'agent' | 'system';
  senderName: string;
  text: string;
  timestamp: string;
  agentConfidence?: number;
  knowledgeSources?: string[];
  memoryUsed?: boolean;
}

export interface Customer {
  id: string;
  name: string;
  email: string;
  avatar: string;
  location: string;
  totalOrders: number;
  totalSpent: number;
  lastOrder: string;
  segment: string;
  preferredLanguage: string;
  communicationStyle: string;
  conversationCount: number;
  satisfaction: number;
  tags: string[];
  memoryProfile: {
    purchaseHistory: boolean;
    productQuestions: boolean;
    geography: boolean;
    marketingSegments: boolean;
    jurisdictionCodes: boolean;
    cartData: boolean;
  };
}

export interface KnowledgeArticle {
  id: string;
  title: string;
  category: string;
  content: string;
  status: 'published' | 'draft' | 'archived';
  lastUpdated: string;
  author: string;
  usageCount: number;
  helpfulRate: number;
}

export interface TeamMember {
  id: string;
  name: string;
  email: string;
  role: 'owner' | 'admin' | 'agent' | 'viewer';
  avatar: string;
  status: 'active' | 'invited' | 'disabled';
  lastActive: string;
  assignedConversations: number;
}

export interface AnalyticsSummary {
  totalConversations: number;
  totalConversationsDelta: number;
  avgResponseTime: number;
  avgResponseTimeDelta: number;
  resolutionRate: number;
  resolutionRateDelta: number;
  customerSatisfaction: number;
  customerSatisfactionDelta: number;
  aiHandledRate: number;
  aiHandledRateDelta: number;
  escalationRate: number;
  escalationRateDelta: number;
}

export interface DailyVolume {
  date: string;
  total: number;
  billable: number;
  aiResolved: number;
  escalated: number;
}

export interface IntentBreakdown {
  intent: string;
  count: number;
  percentage: number;
  avgConfidence: number;
  trend: 'up' | 'down' | 'stable';
}

export interface UsageDashboard {
  currentPeriod: {
    included: number;
    used: number;
    packBalance: number;
    overage: number;
    percentUsed: number;
  };
  billing: {
    plan: string;
    monthlyBase: number;
    currentOverage: number;
    nextInvoice: string;
    status: 'active' | 'past_due' | 'trialing';
  };
  dailyUsage: DailyVolume[];
}

export interface WidgetConfig {
  // Visual
  primaryColor: string;
  headerGradientEnd: string;
  fontFamily: string;
  borderRadius: number;
  launcherSize: number;
  launcherIcon: 'chat' | 'headset' | 'help' | 'custom';
  position: 'bottom-right' | 'bottom-left';
  colorMode: 'light' | 'dark' | 'auto';
  zIndex: number;
  // Behavior
  autoOpen: boolean;
  autoOpenDelay: number;
  greetingEnabled: boolean;
  greetingMessage: string;
  preChatFormEnabled: boolean;
  preChatFields: string[];
  offlineFormEnabled: boolean;
  soundEnabled: boolean;
  // Content
  headerTitle: string;
  headerSubtitle: string;
  inputPlaceholder: string;
}

export interface TenantConfig {
  // Brand & Persona
  brandName: string;
  brandVoice: string;
  formality: 'casual' | 'professional' | 'formal';
  responseLength: 'concise' | 'moderate' | 'detailed';
  // Behavior
  maxTurns: number;
  idleTimeoutMinutes: number;
  escalationThreshold: number;
  autoEscalateTopics: string[];
  // Policies
  refundPolicy: string;
  shippingPolicy: string;
  returnWindow: number;
  customInstructions: string;
  // Language
  primaryLanguage: string;
  supportedLanguages: string[];
}

export interface OnboardingStep {
  id: number;
  title: string;
  description: string;
  completed: boolean;
  fields: { label: string; type: string; value: any; placeholder?: string; options?: string[] }[];
}

// ============================================================================
// MOCK DATA
// ============================================================================

const avatarColors = ['#C41E2A', '#2563EB', '#059669', '#D97706', '#7C3AED', '#DB2777'];
function getInitials(name: string): string {
  return name.split(' ').map(n => n[0]).join('').toUpperCase();
}

export const CONVERSATIONS: Conversation[] = [
  {
    id: 'conv-001',
    customerName: 'Sarah Chen',
    customerEmail: 'sarah.chen@example.com',
    customerAvatar: '',
    subject: 'Order #1847 - Wrong size delivered',
    lastMessage: 'I ordered a medium but received a large. Can I exchange it?',
    status: 'active',
    channel: 'chat',
    assignedTo: null,
    priority: 'high',
    createdAt: '2026-02-02T14:23:00Z',
    updatedAt: '2026-02-02T14:25:00Z',
    messageCount: 4,
    tags: ['exchange', 'sizing'],
    sentiment: 'negative',
    memoryLayers: [1, 2],
  },
  {
    id: 'conv-002',
    customerName: 'Marcus Johnson',
    customerEmail: 'marcus.j@example.com',
    customerAvatar: '',
    subject: 'Product recommendation needed',
    lastMessage: 'Thanks! The blue one sounds perfect. Adding to cart now.',
    status: 'resolved',
    channel: 'chat',
    assignedTo: null,
    priority: 'low',
    createdAt: '2026-02-02T11:05:00Z',
    updatedAt: '2026-02-02T11:18:00Z',
    messageCount: 6,
    tags: ['recommendation', 'upsell'],
    sentiment: 'positive',
    memoryLayers: [1, 2],
  },
  {
    id: 'conv-003',
    customerName: 'Emily Rodriguez',
    customerEmail: 'e.rodriguez@example.com',
    customerAvatar: '',
    subject: 'Shipping delay inquiry',
    lastMessage: 'When will my order arrive? It was supposed to be here yesterday.',
    status: 'waiting',
    channel: 'chat',
    assignedTo: 'Alex Kim',
    priority: 'medium',
    createdAt: '2026-02-01T16:42:00Z',
    updatedAt: '2026-02-02T09:15:00Z',
    messageCount: 8,
    tags: ['shipping', 'delay'],
    sentiment: 'negative',
    memoryLayers: [1],
  },
  {
    id: 'conv-004',
    customerName: 'James Wilson',
    customerEmail: 'jwilson@example.com',
    customerAvatar: '',
    subject: 'Bulk order pricing question',
    lastMessage: 'We need 500 units for our corporate event. What discount can you offer?',
    status: 'escalated',
    channel: 'chat',
    assignedTo: 'Dana Park',
    priority: 'urgent',
    createdAt: '2026-02-02T10:30:00Z',
    updatedAt: '2026-02-02T13:45:00Z',
    messageCount: 12,
    tags: ['bulk-order', 'pricing', 'corporate'],
    sentiment: 'neutral',
    memoryLayers: [1, 2],
  },
  {
    id: 'conv-005',
    customerName: 'Aisha Patel',
    customerEmail: 'aisha.p@example.com',
    customerAvatar: '',
    subject: 'Return request - Defective item',
    lastMessage: 'The zipper broke on first use. I want a full refund.',
    status: 'active',
    channel: 'chat',
    assignedTo: null,
    priority: 'high',
    createdAt: '2026-02-02T15:10:00Z',
    updatedAt: '2026-02-02T15:12:00Z',
    messageCount: 2,
    tags: ['return', 'defective', 'refund'],
    sentiment: 'negative',
    memoryLayers: [1, 2],
  },
  {
    id: 'conv-006',
    customerName: 'Tom Baker',
    customerEmail: 'tom.baker@example.com',
    customerAvatar: '',
    subject: 'How to track my order?',
    lastMessage: 'Got it, thanks for the tracking link!',
    status: 'resolved',
    channel: 'chat',
    assignedTo: null,
    priority: 'low',
    createdAt: '2026-02-02T08:20:00Z',
    updatedAt: '2026-02-02T08:24:00Z',
    messageCount: 3,
    tags: ['tracking'],
    sentiment: 'positive',
    memoryLayers: [1],
  },
  {
    id: 'conv-007',
    customerName: 'Lisa Chang',
    customerEmail: 'lisa.chang@example.com',
    customerAvatar: '',
    subject: 'Gift wrapping options',
    lastMessage: 'Do you offer premium gift wrapping for the holidays?',
    status: 'active',
    channel: 'chat',
    assignedTo: null,
    priority: 'low',
    createdAt: '2026-02-02T15:30:00Z',
    updatedAt: '2026-02-02T15:31:00Z',
    messageCount: 1,
    tags: ['gift-wrapping'],
    sentiment: 'neutral',
    memoryLayers: [1],
  },
  {
    id: 'conv-008',
    customerName: 'Robert Martinez',
    customerEmail: 'r.martinez@example.com',
    customerAvatar: '',
    subject: 'Account login issues',
    lastMessage: 'I keep getting locked out after 3 attempts. Please help.',
    status: 'escalated',
    channel: 'email',
    assignedTo: 'Alex Kim',
    priority: 'high',
    createdAt: '2026-02-01T22:15:00Z',
    updatedAt: '2026-02-02T10:00:00Z',
    messageCount: 5,
    tags: ['account', 'login', 'technical'],
    sentiment: 'negative',
    memoryLayers: [1],
  },
];

export const MESSAGES: Record<string, Message[]> = {
  'conv-001': [
    {
      id: 'msg-001-1',
      conversationId: 'conv-001',
      sender: 'customer',
      senderName: 'Sarah Chen',
      text: 'Hi, I just received my order #1847 and the size is wrong. I ordered a medium but got a large.',
      timestamp: '2026-02-02T14:23:00Z',
    },
    {
      id: 'msg-001-2',
      conversationId: 'conv-001',
      sender: 'agent',
      senderName: 'Agent Red AI',
      text: "I'm sorry to hear about the sizing issue with your order, Sarah. I can see order #1847 in our system - a Classic Fit Polo in Medium. Let me help you with an exchange right away.\n\nI can offer you two options:\n1. **Free exchange** - We'll send you the correct Medium size and include a prepaid return label for the Large\n2. **Full refund** - If you'd prefer, I can process a complete refund\n\nWhich would you prefer?",
      timestamp: '2026-02-02T14:23:45Z',
      agentConfidence: 0.94,
      knowledgeSources: ['exchange-policy', 'order-lookup'],
      memoryUsed: true,
    },
    {
      id: 'msg-001-3',
      conversationId: 'conv-001',
      sender: 'customer',
      senderName: 'Sarah Chen',
      text: 'The exchange sounds great! Can I get the same color?',
      timestamp: '2026-02-02T14:24:30Z',
    },
    {
      id: 'msg-001-4',
      conversationId: 'conv-001',
      sender: 'agent',
      senderName: 'Agent Red AI',
      text: "Yes! The Navy Blue Classic Fit Polo in Medium is in stock. I've initiated the exchange - you'll receive a confirmation email with the prepaid return label within the next few minutes.\n\nThe replacement will ship as soon as we receive the return, typically within 2-3 business days of receipt. Is there anything else I can help you with?",
      timestamp: '2026-02-02T14:25:00Z',
      agentConfidence: 0.97,
      knowledgeSources: ['inventory-check', 'exchange-policy', 'shipping-times'],
      memoryUsed: true,
    },
  ],
  'conv-004': [
    {
      id: 'msg-004-1',
      conversationId: 'conv-004',
      sender: 'customer',
      senderName: 'James Wilson',
      text: "Hello, I'm the events coordinator at Meridian Corp. We're planning our annual company retreat and need to order 500 branded polo shirts.",
      timestamp: '2026-02-02T10:30:00Z',
    },
    {
      id: 'msg-004-2',
      conversationId: 'conv-004',
      sender: 'agent',
      senderName: 'Agent Red AI',
      text: "Welcome, James! That sounds like a great event. For bulk orders of 500+ units, we offer volume pricing. Let me get some details to provide an accurate quote:\n\n1. Which polo style are you interested in?\n2. Do you need custom embroidery or printing?\n3. What's your target delivery date?\n\nI should mention that for corporate orders of this size, I'll connect you with our enterprise sales team who can provide custom pricing and dedicated support.",
      timestamp: '2026-02-02T10:31:00Z',
      agentConfidence: 0.88,
      knowledgeSources: ['bulk-pricing-policy', 'corporate-orders-faq'],
      memoryUsed: false,
    },
    {
      id: 'msg-004-3',
      conversationId: 'conv-004',
      sender: 'customer',
      senderName: 'James Wilson',
      text: "We'd like the Performance Polo in company colors (navy and white), with our logo embroidered on the left chest. Event is March 15th.",
      timestamp: '2026-02-02T10:35:00Z',
    },
    {
      id: 'msg-004-4',
      conversationId: 'conv-004',
      sender: 'system',
      senderName: 'System',
      text: 'Conversation escalated to human agent. Reason: Bulk order pricing requires enterprise sales approval. Assigned to: Dana Park (Enterprise Sales)',
      timestamp: '2026-02-02T10:36:00Z',
    },
    {
      id: 'msg-004-5',
      conversationId: 'conv-004',
      sender: 'agent',
      senderName: 'Dana Park',
      text: "Hi James, Dana here from our enterprise team. I've reviewed your requirements. For 500 Performance Polos with custom embroidery, I can offer:\n\n- **Unit price:** $22.50 (retail $34.99 - 36% discount)\n- **Embroidery setup:** $150 one-time\n- **Total estimate:** $11,400\n- **Production time:** 10-12 business days\n\nShall I send a formal quote to your email?",
      timestamp: '2026-02-02T13:45:00Z',
    },
  ],
};

export const CUSTOMERS: Customer[] = [
  {
    id: 'cust-001',
    name: 'Sarah Chen',
    email: 'sarah.chen@example.com',
    avatar: '',
    location: 'San Francisco, CA',
    totalOrders: 12,
    totalSpent: 847.50,
    lastOrder: '2026-01-28',
    segment: 'Loyal Customer',
    preferredLanguage: 'English',
    communicationStyle: 'Direct, detail-oriented',
    conversationCount: 8,
    satisfaction: 4.5,
    tags: ['repeat-buyer', 'size-sensitive'],
    memoryProfile: {
      purchaseHistory: true,
      productQuestions: true,
      geography: true,
      marketingSegments: true,
      jurisdictionCodes: true,
      cartData: false,
    },
  },
  {
    id: 'cust-004',
    name: 'James Wilson',
    email: 'jwilson@example.com',
    avatar: '',
    location: 'Chicago, IL',
    totalOrders: 3,
    totalSpent: 2450.00,
    lastOrder: '2026-01-15',
    segment: 'Corporate Buyer',
    preferredLanguage: 'English',
    communicationStyle: 'Formal, efficiency-focused',
    conversationCount: 5,
    satisfaction: 4.0,
    tags: ['corporate', 'bulk-buyer', 'B2B'],
    memoryProfile: {
      purchaseHistory: true,
      productQuestions: false,
      geography: true,
      marketingSegments: true,
      jurisdictionCodes: true,
      cartData: false,
    },
  },
];

export const KNOWLEDGE_ARTICLES: KnowledgeArticle[] = [
  {
    id: 'kb-001',
    title: 'Return & Exchange Policy',
    category: 'Policies',
    content: 'We offer a 30-day return window for all unused items in original packaging. Exchanges are free for size/color changes. Defective items qualify for immediate replacement or full refund.',
    status: 'published',
    lastUpdated: '2026-01-15',
    author: 'Admin',
    usageCount: 342,
    helpfulRate: 94,
  },
  {
    id: 'kb-002',
    title: 'Shipping Information',
    category: 'Shipping',
    content: 'Standard shipping: 5-7 business days (free over $50). Express: 2-3 business days ($9.99). Overnight: next business day ($19.99). All orders include tracking.',
    status: 'published',
    lastUpdated: '2026-01-20',
    author: 'Admin',
    usageCount: 567,
    helpfulRate: 91,
  },
  {
    id: 'kb-003',
    title: 'Size Guide',
    category: 'Products',
    content: 'Detailed sizing chart for all clothing categories. Includes measurement instructions, fit recommendations, and size comparison between brands.',
    status: 'published',
    lastUpdated: '2026-01-10',
    author: 'Admin',
    usageCount: 891,
    helpfulRate: 87,
  },
  {
    id: 'kb-004',
    title: 'Bulk Order Pricing',
    category: 'Sales',
    content: 'Volume discounts available for orders of 50+ units. 10-19%: 50-99 units. 20-29%: 100-499 units. 30-40%: 500+ units. Custom embroidery and printing available.',
    status: 'published',
    lastUpdated: '2026-01-25',
    author: 'Dana Park',
    usageCount: 45,
    helpfulRate: 96,
  },
  {
    id: 'kb-005',
    title: 'Holiday Gift Wrapping',
    category: 'Services',
    content: 'Premium gift wrapping available for $4.99 per item. Includes branded tissue paper, gift box, and personalized message card.',
    status: 'draft',
    lastUpdated: '2026-02-01',
    author: 'Admin',
    usageCount: 0,
    helpfulRate: 0,
  },
  {
    id: 'kb-006',
    title: 'Warranty & Care Instructions',
    category: 'Products',
    content: 'All products come with a 1-year warranty against manufacturing defects. Care instructions vary by material - see individual product pages.',
    status: 'published',
    lastUpdated: '2026-01-05',
    author: 'Admin',
    usageCount: 234,
    helpfulRate: 89,
  },
  {
    id: 'kb-007',
    title: 'International Shipping Restrictions',
    category: 'Shipping',
    content: 'We ship to 45 countries. Restricted items vary by destination. Import duties are the customer responsibility. Estimated delivery: 10-21 business days.',
    status: 'archived',
    lastUpdated: '2025-11-15',
    author: 'Admin',
    usageCount: 78,
    helpfulRate: 72,
  },
];

export const TEAM_MEMBERS: TeamMember[] = [
  {
    id: 'team-001',
    name: 'Mike VanDusen',
    email: 'mike@remakerdigital.com',
    role: 'owner',
    avatar: '',
    status: 'active',
    lastActive: '2026-02-02T15:00:00Z',
    assignedConversations: 0,
  },
  {
    id: 'team-002',
    name: 'Alex Kim',
    email: 'alex.kim@example.com',
    role: 'admin',
    avatar: '',
    status: 'active',
    lastActive: '2026-02-02T14:45:00Z',
    assignedConversations: 3,
  },
  {
    id: 'team-003',
    name: 'Dana Park',
    email: 'dana.park@example.com',
    role: 'agent',
    avatar: '',
    status: 'active',
    lastActive: '2026-02-02T13:50:00Z',
    assignedConversations: 5,
  },
  {
    id: 'team-004',
    name: 'Jordan Lee',
    email: 'jordan.lee@example.com',
    role: 'viewer',
    avatar: '',
    status: 'invited',
    lastActive: '',
    assignedConversations: 0,
  },
];

export const ANALYTICS_SUMMARY: AnalyticsSummary = {
  totalConversations: 1247,
  totalConversationsDelta: 12.3,
  avgResponseTime: 1.4,
  avgResponseTimeDelta: -8.5,
  resolutionRate: 89.2,
  resolutionRateDelta: 3.1,
  customerSatisfaction: 4.3,
  customerSatisfactionDelta: 0.2,
  aiHandledRate: 78.5,
  aiHandledRateDelta: 5.7,
  escalationRate: 11.8,
  escalationRateDelta: -2.1,
};

export const DAILY_VOLUMES: DailyVolume[] = Array.from({ length: 30 }, (_, i) => {
  const date = new Date('2026-01-04');
  date.setDate(date.getDate() + i);
  const base = 35 + Math.floor(Math.random() * 20);
  const weekday = date.getDay();
  const multiplier = (weekday === 0 || weekday === 6) ? 0.6 : 1;
  const total = Math.floor(base * multiplier);
  return {
    date: date.toISOString().split('T')[0],
    total,
    billable: Math.floor(total * 0.85),
    aiResolved: Math.floor(total * 0.72),
    escalated: Math.floor(total * 0.12),
  };
});

export const INTENT_BREAKDOWN: IntentBreakdown[] = [
  { intent: 'Order Status', count: 312, percentage: 25.0, avgConfidence: 0.96, trend: 'stable' },
  { intent: 'Product Information', count: 237, percentage: 19.0, avgConfidence: 0.93, trend: 'up' },
  { intent: 'Return/Exchange', count: 187, percentage: 15.0, avgConfidence: 0.94, trend: 'down' },
  { intent: 'Shipping Inquiry', count: 162, percentage: 13.0, avgConfidence: 0.95, trend: 'stable' },
  { intent: 'Pricing Question', count: 112, percentage: 9.0, avgConfidence: 0.91, trend: 'up' },
  { intent: 'Account Issues', count: 87, percentage: 7.0, avgConfidence: 0.89, trend: 'stable' },
  { intent: 'Complaint', count: 62, percentage: 5.0, avgConfidence: 0.92, trend: 'down' },
  { intent: 'General Inquiry', count: 50, percentage: 4.0, avgConfidence: 0.87, trend: 'stable' },
  { intent: 'Bulk/Corporate', count: 38, percentage: 3.0, avgConfidence: 0.85, trend: 'up' },
];

export const USAGE_DASHBOARD: UsageDashboard = {
  currentPeriod: {
    included: 5000,
    used: 3847,
    packBalance: 1200,
    overage: 0,
    percentUsed: 76.9,
  },
  billing: {
    plan: 'Professional',
    monthlyBase: 399,
    currentOverage: 0,
    nextInvoice: '2026-03-01',
    status: 'active',
  },
  dailyUsage: DAILY_VOLUMES,
};

export const DEFAULT_WIDGET_CONFIG: WidgetConfig = {
  primaryColor: '#C41E2A',
  headerGradientEnd: '#8B1520',
  fontFamily: 'Inter, system-ui, sans-serif',
  borderRadius: 16,
  launcherSize: 60,
  launcherIcon: 'chat',
  position: 'bottom-right',
  colorMode: 'light',
  zIndex: 9999,
  autoOpen: false,
  autoOpenDelay: 5,
  greetingEnabled: true,
  greetingMessage: 'Hi there! How can we help you today?',
  preChatFormEnabled: true,
  preChatFields: ['name', 'email'],
  offlineFormEnabled: true,
  soundEnabled: true,
  headerTitle: 'Support',
  headerSubtitle: 'We typically reply within minutes',
  inputPlaceholder: 'Type your message...',
};

export const DEFAULT_TENANT_CONFIG: TenantConfig = {
  brandName: 'Acme Outfitters',
  brandVoice: 'Friendly, helpful outdoor gear experts who genuinely care about our customers\' adventures.',
  formality: 'professional',
  responseLength: 'moderate',
  maxTurns: 50,
  idleTimeoutMinutes: 30,
  escalationThreshold: 0.7,
  autoEscalateTopics: ['refund-dispute', 'legal-complaint', 'safety-concern'],
  refundPolicy: 'Full refund within 30 days of purchase for unused items in original packaging. Defective items eligible for immediate replacement.',
  shippingPolicy: 'Free standard shipping on orders over $50. Express and overnight options available at checkout.',
  returnWindow: 30,
  customInstructions: 'Always mention our loyalty program for repeat customers. If the customer seems interested in hiking gear, mention our upcoming Spring Trail Collection launching March 1st.',
  primaryLanguage: 'en',
  supportedLanguages: ['en', 'es', 'fr'],
};

export const ONBOARDING_STEPS: OnboardingStep[] = [
  {
    id: 1,
    title: 'Business Info',
    description: 'Tell us about your business',
    completed: true,
    fields: [
      { label: 'Business Name', type: 'text', value: 'Acme Outfitters', placeholder: 'Your store name' },
      { label: 'Industry', type: 'select', value: 'retail', options: ['retail', 'saas', 'ecommerce', 'services', 'other'] },
      { label: 'Website', type: 'url', value: 'https://acmeoutfitters.com', placeholder: 'https://' },
    ],
  },
  {
    id: 2,
    title: 'AI Persona',
    description: 'Define how your AI agent speaks',
    completed: true,
    fields: [
      { label: 'Brand Voice', type: 'textarea', value: 'Friendly, helpful outdoor gear experts who genuinely care about our customers\' adventures.', placeholder: 'Describe the personality and tone...' },
      { label: 'Formality', type: 'select', value: 'professional', options: ['casual', 'professional', 'formal'] },
      { label: 'Response Length', type: 'select', value: 'moderate', options: ['concise', 'moderate', 'detailed'] },
    ],
  },
  {
    id: 3,
    title: 'Policies',
    description: 'Set your business policies',
    completed: true,
    fields: [
      { label: 'Return Window (days)', type: 'number', value: 30 },
      { label: 'Refund Policy', type: 'textarea', value: 'Full refund within 30 days of purchase for unused items in original packaging.' },
      { label: 'Shipping Policy', type: 'textarea', value: 'Free standard shipping on orders over $50.' },
    ],
  },
  {
    id: 4,
    title: 'Escalation',
    description: 'Configure when to escalate to humans',
    completed: false,
    fields: [
      { label: 'Escalation Sensitivity', type: 'select', value: 'balanced', options: ['conservative', 'balanced', 'aggressive'] },
      { label: 'Auto-Escalate Topics', type: 'multiselect', value: ['refund-dispute', 'legal-complaint'], options: ['refund-dispute', 'legal-complaint', 'safety-concern', 'billing-issue', 'account-deletion'] },
      { label: 'Business Hours', type: 'text', value: '9:00 AM - 6:00 PM EST', placeholder: 'e.g., 9-5 EST' },
    ],
  },
  {
    id: 5,
    title: 'Knowledge Base',
    description: 'Import your support content',
    completed: false,
    fields: [
      { label: 'Import Source', type: 'select', value: '', options: ['manual', 'url-crawl', 'csv-upload', 'zendesk-import'] },
      { label: 'FAQ URL', type: 'url', value: '', placeholder: 'https://yoursite.com/faq' },
    ],
  },
  {
    id: 6,
    title: 'Integrations',
    description: 'Connect your tools',
    completed: false,
    fields: [
      { label: 'Shopify Store', type: 'text', value: 'acmeoutfitters.myshopify.com', placeholder: 'yourstore.myshopify.com' },
      { label: 'Zendesk Subdomain', type: 'text', value: '', placeholder: 'yourcompany.zendesk.com' },
    ],
  },
  {
    id: 7,
    title: 'Team',
    description: 'Invite your support team',
    completed: false,
    fields: [
      { label: 'Team Email', type: 'email', value: '', placeholder: 'colleague@yourcompany.com' },
      { label: 'Role', type: 'select', value: 'agent', options: ['admin', 'agent', 'viewer'] },
    ],
  },
  {
    id: 8,
    title: 'Widget',
    description: 'Customize the chat widget',
    completed: false,
    fields: [
      { label: 'Primary Color', type: 'color', value: '#C41E2A' },
      { label: 'Position', type: 'select', value: 'bottom-right', options: ['bottom-right', 'bottom-left'] },
      { label: 'Greeting Message', type: 'textarea', value: 'Hi there! How can we help you today?' },
    ],
  },
  {
    id: 9,
    title: 'Go Live',
    description: 'Review and activate',
    completed: false,
    fields: [],
  },
];

// ============================================================================
// DEFENSIVE CONFIG ROLLOUT MOCK DATA
// ============================================================================

export interface ConfigRollout {
  id: string;
  name: string;
  status: 'draft' | 'active' | 'completed' | 'reverted';
  trafficSplit: number; // percentage to B group
  selectionMethod: 'round-robin' | 'geography' | 'campaign-tag';
  selectionCriteria?: string;
  changes: { field: string; currentValue: any; newValue: any }[];
  metrics: {
    groupA: { conversations: number; satisfaction: number; resolutionRate: number; escalationRate: number };
    groupB: { conversations: number; satisfaction: number; resolutionRate: number; escalationRate: number };
  };
  autoRevert: {
    enabled: boolean;
    thresholds: { metric: string; degradation: number }[];
    reverted: boolean;
    revertReason?: string;
  };
  createdAt: string;
  startedAt?: string;
  completedAt?: string;
}

export const CONFIG_ROLLOUTS: ConfigRollout[] = [
  {
    id: 'rollout-001',
    name: 'Casual tone experiment',
    status: 'active',
    trafficSplit: 10,
    selectionMethod: 'round-robin',
    changes: [
      { field: 'formality', currentValue: 'professional', newValue: 'casual' },
      { field: 'responseLength', currentValue: 'moderate', newValue: 'concise' },
    ],
    metrics: {
      groupA: { conversations: 1123, satisfaction: 4.3, resolutionRate: 89.2, escalationRate: 11.8 },
      groupB: { conversations: 124, satisfaction: 4.1, resolutionRate: 87.5, escalationRate: 13.2 },
    },
    autoRevert: {
      enabled: true,
      thresholds: [
        { metric: 'satisfaction', degradation: 10 },
        { metric: 'resolutionRate', degradation: 15 },
        { metric: 'escalationRate', degradation: 25 },
      ],
      reverted: false,
    },
    createdAt: '2026-02-01T10:00:00Z',
    startedAt: '2026-02-01T12:00:00Z',
  },
  {
    id: 'rollout-002',
    name: 'Aggressive escalation threshold',
    status: 'reverted',
    trafficSplit: 20,
    selectionMethod: 'round-robin',
    changes: [
      { field: 'escalationThreshold', currentValue: 0.7, newValue: 0.5 },
    ],
    metrics: {
      groupA: { conversations: 890, satisfaction: 4.3, resolutionRate: 89.2, escalationRate: 11.8 },
      groupB: { conversations: 210, satisfaction: 4.4, resolutionRate: 82.1, escalationRate: 28.5 },
    },
    autoRevert: {
      enabled: true,
      thresholds: [
        { metric: 'escalationRate', degradation: 25 },
      ],
      reverted: true,
      revertReason: 'Escalation rate exceeded threshold: 28.5% vs 11.8% baseline (141% increase, threshold: 25%)',
    },
    createdAt: '2026-01-28T09:00:00Z',
    startedAt: '2026-01-28T10:00:00Z',
    completedAt: '2026-01-29T14:30:00Z',
  },
];

// ============================================================================
// INVOICE MOCK DATA
// ============================================================================

export interface Invoice {
  id: string;
  date: string;
  amount: number;
  status: 'paid' | 'pending' | 'failed';
  description: string;
  pdfUrl: string;
}

export const INVOICES: Invoice[] = [
  { id: 'inv-006', date: '2026-02-01', amount: 399.00, status: 'paid', description: 'Professional Plan - February 2026', pdfUrl: '#' },
  { id: 'inv-005', date: '2026-01-01', amount: 399.00, status: 'paid', description: 'Professional Plan - January 2026', pdfUrl: '#' },
  { id: 'inv-004', date: '2025-12-01', amount: 448.75, status: 'paid', description: 'Professional Plan + Overage (199 conv @ $0.025)', pdfUrl: '#' },
  { id: 'inv-003', date: '2025-11-01', amount: 399.00, status: 'paid', description: 'Professional Plan - November 2025', pdfUrl: '#' },
  { id: 'inv-002', date: '2025-10-01', amount: 399.00, status: 'paid', description: 'Professional Plan - October 2025', pdfUrl: '#' },
  { id: 'inv-001', date: '2025-09-01', amount: 149.00, status: 'paid', description: 'Starter Plan - September 2025 (upgraded mid-month)', pdfUrl: '#' },
];
