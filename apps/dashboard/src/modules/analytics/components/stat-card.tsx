"use client";

import { Card, CardBody } from "@heroui/react";
import { ArrowUpRight, ArrowDownRight, type LucideIcon } from "lucide-react";

interface StatCardProps {
  title: string;
  value: string;
  trend: string;
  isPositive: boolean;
  icon: LucideIcon;
}

export function StatCard({ title, value, trend, isPositive, icon: Icon }: StatCardProps) {
  return (
    <Card shadow="sm">
      <CardBody className="p-5">
        <div className="flex items-center gap-3 mb-4 text-default-500">
          <div className="p-2 rounded-lg bg-default-100">
            <Icon className="h-4 w-4" />
          </div>
          <span className="text-sm font-medium">{title}</span>
        </div>
        <div className="flex items-end justify-between">
          <h3 className="text-3xl font-bold">{value}</h3>
          <div
            className={`flex items-center gap-1 text-sm ${isPositive ? "text-success" : "text-danger"}`}
          >
            {isPositive ? (
              <ArrowUpRight className="h-4 w-4" />
            ) : (
              <ArrowDownRight className="h-4 w-4" />
            )}
            <span>{trend}</span>
          </div>
        </div>
      </CardBody>
    </Card>
  );
}
