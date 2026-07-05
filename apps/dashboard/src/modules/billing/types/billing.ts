export type PlanTier = "free" | "pro" | "enterprise";
export type InvoiceStatus = "paid" | "pending" | "failed";

export interface SubscriptionPlan {
  tier: PlanTier;
  name: string;
  price: number;
  interval: "month" | "year";
  features: string[];
}

export interface CurrentSubscription {
  plan: SubscriptionPlan;
  status: "active" | "past_due" | "canceled";
  current_period_end: string;
  cancel_at_period_end: boolean;
  queries_used: number;
  queries_limit: number;
}

export interface Invoice {
  id: string;
  amount: number;
  status: InvoiceStatus;
  date: string;
  download_url: string;
}
