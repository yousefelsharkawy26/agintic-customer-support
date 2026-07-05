"use client";

import { Card, CardBody, CardHeader, Divider } from "@heroui/react";
import {
  MessageSquare,
  Bot,
  BookOpen,
  Activity,
  AlertTriangle,
  ArrowUpRight,
  ArrowDownRight,
  DollarSign,
  Zap,
} from "lucide-react";

const metrics = [
  {
    title: "Today's Conversations",
    value: "1,248",
    change: "+12.5%",
    trend: "up",
    icon: MessageSquare,
    color: "text-blue-500",
  },
  {
    title: "Active Agents",
    value: "4",
    change: "0%",
    trend: "neutral",
    icon: Bot,
    color: "text-purple-500",
  },
  {
    title: "Knowledge Base",
    value: "98.2%",
    change: "Hit Rate",
    trend: "neutral",
    icon: BookOpen,
    color: "text-green-500",
  },
  {
    title: "Response Latency",
    value: "1.2s",
    change: "-0.3s",
    trend: "down",
    icon: Zap,
    color: "text-amber-500",
  },
  {
    title: "Success Rate",
    value: "96.5%",
    change: "+2.1%",
    trend: "up",
    icon: Activity,
    color: "text-emerald-500",
  },
  {
    title: "Est. Cost (Today)",
    value: "$42.50",
    change: "+$5.20",
    trend: "up",
    icon: DollarSign,
    color: "text-rose-500",
  },
];

export default function OverviewPage() {
  return (
    <div className="flex flex-col gap-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Overview</h1>
        <p className="text-default-500">Executive summary of your tenant&apos;s AI performance.</p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {metrics.map((metric) => (
          <Card key={metric.title} shadow="sm">
            <CardBody className="flex flex-row items-center justify-between p-5">
              <div className="flex flex-col gap-1">
                <p className="text-sm font-medium text-default-500">{metric.title}</p>
                <div className="flex items-center gap-2">
                  <h3 className="text-2xl font-semibold">{metric.value}</h3>
                  <span
                    className={`flex items-center text-xs font-medium ${
                      metric.trend === "up"
                        ? "text-success"
                        : metric.trend === "down"
                          ? "text-success" // Down is good for latency
                          : "text-default-400"
                    }`}
                  >
                    {metric.trend === "up" && <ArrowUpRight className="h-3 w-3" />}
                    {metric.trend === "down" && <ArrowDownRight className="h-3 w-3" />}
                    {metric.change}
                  </span>
                </div>
              </div>
              <div className={`rounded-lg bg-default-100 p-2 ${metric.color}`}>
                <metric.icon className="h-5 w-5" />
              </div>
            </CardBody>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* System Health */}
        <Card className="lg:col-span-2" shadow="sm">
          <CardHeader className="flex gap-3 pb-2 pt-5 px-6">
            <div className="flex flex-col">
              <p className="text-md font-semibold">Recent Activity</p>
              <p className="text-small text-default-500">Latest conversation trends</p>
            </div>
          </CardHeader>
          <Divider />
          <CardBody className="min-h-[300px] items-center justify-center">
            <p className="text-default-400">Chart Placeholder</p>
            {/* TODO: Add Recharts or similar library for charts */}
          </CardBody>
        </Card>

        {/* Alerts */}
        <Card shadow="sm">
          <CardHeader className="flex gap-3 pb-2 pt-5 px-6">
            <div className="flex flex-col">
              <p className="text-md font-semibold">Active Alerts</p>
              <p className="text-small text-default-500">System health issues</p>
            </div>
          </CardHeader>
          <Divider />
          <CardBody className="flex flex-col gap-4 p-6">
            <div className="flex items-start gap-3 rounded-lg border border-warning-200 bg-warning-50 p-3 dark:bg-warning-50/10">
              <AlertTriangle className="mt-0.5 h-5 w-5 text-warning" />
              <div className="flex flex-col">
                <p className="text-sm font-medium text-warning-700 dark:text-warning-500">
                  Elevated Latency
                </p>
                <p className="text-xs text-warning-600 dark:text-warning-400">
                  Claude 3.5 Sonnet is experiencing high latency (p95 &gt; 2.5s)
                </p>
              </div>
            </div>
            <div className="flex items-center justify-center p-4">
              <p className="text-sm text-default-400">No other active alerts</p>
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  );
}
