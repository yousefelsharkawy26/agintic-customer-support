"use client";

import { Card, CardBody, CardHeader, Divider, Button, Progress } from "@heroui/react";
import { CreditCard, Zap, Calendar, ExternalLink } from "lucide-react";
import { PlanCard } from "@/modules/billing/components/plan-card";
import { InvoiceTable } from "@/modules/billing/components/invoice-table";
import { AVAILABLE_PLANS, MOCK_SUBSCRIPTION, MOCK_INVOICES } from "@/modules/billing/api/mock-data";

export default function BillingPage() {
  const usagePercentage = (MOCK_SUBSCRIPTION.queries_used / MOCK_SUBSCRIPTION.queries_limit) * 100;

  return (
    <div className="flex flex-col gap-6 pb-12">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Billing & Usage</h1>
          <p className="text-default-500">
            Manage your subscription plan, payment methods, and monitor API usage.
          </p>
        </div>
        <Button variant="flat" startContent={<ExternalLink className="h-4 w-4" />}>
          Customer Portal
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Usage Overview */}
        <div className="flex flex-col gap-4 lg:col-span-2">
          <Card shadow="sm" className="bg-primary-50 dark:bg-primary-50/5 border-primary/20">
            <CardBody className="p-6">
              <div className="flex flex-col gap-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Zap className="h-5 w-5 text-primary" />
                    <h2 className="text-lg font-semibold text-primary-700 dark:text-primary-400">
                      Current Usage
                    </h2>
                  </div>
                  <span className="text-sm font-medium text-primary-600 dark:text-primary-500">
                    {MOCK_SUBSCRIPTION.queries_used.toLocaleString()} /{" "}
                    {MOCK_SUBSCRIPTION.queries_limit.toLocaleString()} queries
                  </span>
                </div>
                <Progress
                  value={usagePercentage}
                  color={
                    usagePercentage > 90 ? "danger" : usagePercentage > 75 ? "warning" : "primary"
                  }
                  className="h-2"
                />
                <p className="text-xs text-primary-600/70 dark:text-primary-500/70">
                  Your usage resets at the end of the billing period.
                </p>
              </div>
            </CardBody>
          </Card>

          <Card shadow="sm">
            <CardHeader className="px-6 pt-5 pb-4">
              <h2 className="text-base font-semibold">Invoice History</h2>
            </CardHeader>
            <Divider />
            <div className="p-0 border-none">
              <InvoiceTable invoices={MOCK_INVOICES} />
            </div>
          </Card>
        </div>

        {/* Subscription Info Sidebar */}
        <div className="flex flex-col gap-4">
          <Card shadow="sm">
            <CardHeader className="px-5 pt-5 pb-2">
              <h2 className="text-base font-semibold">Payment Method</h2>
            </CardHeader>
            <Divider />
            <CardBody className="p-5 flex flex-col gap-4">
              <div className="flex items-center gap-3 p-3 rounded-lg border border-divider bg-default-50">
                <div className="bg-white p-1.5 rounded shadow-sm border border-default-200">
                  <CreditCard className="h-5 w-5 text-default-700" />
                </div>
                <div className="flex flex-col flex-1">
                  <span className="text-sm font-semibold">•••• •••• •••• 4242</span>
                  <span className="text-xs text-default-500">Expires 12/28</span>
                </div>
              </div>
              <Button size="sm" variant="flat" className="w-full">
                Update Payment Method
              </Button>
            </CardBody>
          </Card>

          <Card shadow="sm">
            <CardHeader className="px-5 pt-5 pb-2">
              <h2 className="text-base font-semibold">Next Invoice</h2>
            </CardHeader>
            <Divider />
            <CardBody className="p-5 flex flex-col gap-4">
              <div className="flex items-center gap-2 text-sm text-default-600">
                <Calendar className="h-4 w-4" />
                <span>{new Date(MOCK_SUBSCRIPTION.current_period_end).toLocaleDateString()}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-default-500">Amount due</span>
                <span className="font-semibold">${MOCK_SUBSCRIPTION.plan.price.toFixed(2)}</span>
              </div>
            </CardBody>
          </Card>
        </div>
      </div>

      <div className="mt-6 flex flex-col gap-6">
        <div>
          <h2 className="text-xl font-bold">Available Plans</h2>
          <p className="text-sm text-default-500 mt-1">
            Upgrade or downgrade your plan at any time.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {AVAILABLE_PLANS.map((plan) => (
            <PlanCard
              key={plan.tier}
              plan={plan}
              isCurrentPlan={plan.tier === MOCK_SUBSCRIPTION.plan.tier}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
