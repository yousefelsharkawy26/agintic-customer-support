import type { CurrentSubscription, Invoice, SubscriptionPlan } from "../types/billing";

export const AVAILABLE_PLANS: SubscriptionPlan[] = [
  {
    tier: "free",
    name: "Starter",
    price: 0,
    interval: "month",
    features: ["1 AI Agent", "1,000 queries/mo", "Community Support", "Basic Analytics"],
  },
  {
    tier: "pro",
    name: "Pro",
    price: 49,
    interval: "month",
    features: [
      "5 AI Agents",
      "10,000 queries/mo",
      "Priority Support",
      "Advanced Analytics",
      "Custom MCP Tools",
    ],
  },
  {
    tier: "enterprise",
    name: "Enterprise",
    price: 299,
    interval: "month",
    features: [
      "Unlimited AI Agents",
      "Custom query limits",
      "Dedicated Account Manager",
      "White-labeling",
      "SSO/SAML",
    ],
  },
];

export const MOCK_SUBSCRIPTION: CurrentSubscription = {
  plan: AVAILABLE_PLANS[1], // Pro Plan
  status: "active",
  current_period_end: new Date(Date.now() + 1000 * 60 * 60 * 24 * 15).toISOString(), // 15 days from now
  cancel_at_period_end: false,
  queries_used: 2401,
  queries_limit: 10000,
};

export const MOCK_INVOICES: Invoice[] = [
  {
    id: "inv_001",
    amount: 49.0,
    status: "paid",
    date: new Date(Date.now() - 1000 * 60 * 60 * 24 * 15).toISOString(),
    download_url: "#",
  },
  {
    id: "inv_002",
    amount: 49.0,
    status: "paid",
    date: new Date(Date.now() - 1000 * 60 * 60 * 24 * 45).toISOString(),
    download_url: "#",
  },
  {
    id: "inv_003",
    amount: 0.0,
    status: "paid",
    date: new Date(Date.now() - 1000 * 60 * 60 * 24 * 75).toISOString(),
    download_url: "#",
  },
];
