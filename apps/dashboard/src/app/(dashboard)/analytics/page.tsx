"use client";

import { useState, useEffect } from "react";
import { Card, CardBody, CardHeader, Divider } from "@heroui/react";
import { MessageSquare, AlertTriangle, DollarSign, Activity } from "lucide-react";
import { StatCard } from "@/modules/analytics/components/stat-card";
import { MOCK_ANALYTICS } from "@/modules/analytics/api/mock-data";

type AnalyticsPayload = Record<string, unknown>;

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsPayload | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetch("/api/analytics?type=summary")
      .then((res) => res.json())
      .then((d: AnalyticsPayload) => {
        if (!("error" in d && d.error)) {
          setData(d);
        }
      })
      .finally(() => setIsLoading(false));
  }, []);

  const maxValue = Math.max(...MOCK_ANALYTICS.queriesByDay.map((d) => d.value));

  if (isLoading) {
    return <div className="p-8 text-center text-default-500">Loading analytics...</div>;
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Analytics Dashboard</h1>
          <p className="text-default-500">
            Monitor agent performance, system usage metrics, and costs.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Requests (Period)"
          value={
            data && "request_count" in data ? `${Number(data.request_count).toLocaleString()}` : "0"
          }
          trend="+5%"
          isPositive={true}
          icon={Activity}
        />
        <StatCard
          title="Total Tokens"
          value={
            data && "token_count" in data ? `${(Number(data.token_count) / 1000).toFixed(1)}k` : "0"
          }
          trend="+12%"
          isPositive={true}
          icon={MessageSquare}
        />
        <StatCard
          title="Total Cost (USD)"
          value={
            data && "total_cost_usd" in data
              ? `$${Number(data.total_cost_usd).toFixed(2)}`
              : "$0.00"
          }
          trend="-2%"
          isPositive={true}
          icon={DollarSign}
        />
        <StatCard
          title="Escalation Rate"
          value={MOCK_ANALYTICS.escalationRate.value}
          trend={MOCK_ANALYTICS.escalationRate.trend}
          isPositive={MOCK_ANALYTICS.escalationRate.isPositive}
          icon={AlertTriangle}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <Card shadow="sm" className="lg:col-span-2">
          <CardHeader className="px-6 pt-5 pb-4">
            <h2 className="text-base font-semibold">Queries Over Time (Mock)</h2>
          </CardHeader>
          <Divider />
          <CardBody className="p-6">
            <div className="h-64 flex items-end justify-between gap-2">
              {MOCK_ANALYTICS.queriesByDay.map((day) => {
                const heightPercentage = (day.value / maxValue) * 100;
                return (
                  <div key={day.name} className="flex flex-col items-center gap-2 flex-1 group">
                    <div className="relative w-full h-full flex items-end justify-center">
                      <div
                        className="w-full max-w-[40px] bg-primary/20 hover:bg-primary transition-all rounded-t-sm"
                        style={{ height: `${heightPercentage}%` }}
                      >
                        <div className="opacity-0 group-hover:opacity-100 absolute -top-8 left-1/2 -translate-x-1/2 bg-foreground text-background text-xs px-2 py-1 rounded transition-opacity whitespace-nowrap z-10 pointer-events-none">
                          {day.value.toLocaleString()}
                        </div>
                      </div>
                    </div>
                    <span className="text-xs text-default-500 font-medium">{day.name}</span>
                  </div>
                );
              })}
            </div>
          </CardBody>
        </Card>

        <Card shadow="sm">
          <CardHeader className="px-6 pt-5 pb-4">
            <h2 className="text-base font-semibold">Top Agents (Mock)</h2>
          </CardHeader>
          <Divider />
          <CardBody className="p-0">
            <div className="flex flex-col divide-y divide-divider">
              {MOCK_ANALYTICS.topAgents.map((agent) => (
                <div key={agent.name} className="p-4 flex flex-col gap-2">
                  <div className="flex justify-between text-sm">
                    <span className="font-medium truncate">{agent.name}</span>
                    <span className="text-default-500">{agent.queries.toLocaleString()}</span>
                  </div>
                  <div className="w-full h-1.5 bg-default-100 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-primary rounded-full"
                      style={{ width: `${(agent.queries / 15420) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
