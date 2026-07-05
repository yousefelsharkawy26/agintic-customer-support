"use client";

import { Card, CardBody, CardHeader, CardFooter, Button, Divider } from "@heroui/react";
import { Check } from "lucide-react";
import type { SubscriptionPlan } from "../types/billing";

interface PlanCardProps {
  plan: SubscriptionPlan;
  isCurrentPlan: boolean;
}

export function PlanCard({ plan, isCurrentPlan }: PlanCardProps) {
  return (
    <Card
      shadow={isCurrentPlan ? "md" : "sm"}
      className={isCurrentPlan ? "border-primary border-2" : "border border-divider"}
    >
      <CardHeader className="flex flex-col items-start px-6 pt-6 pb-4">
        {isCurrentPlan && (
          <span className="text-[10px] font-bold uppercase tracking-wider text-primary mb-2">
            Current Plan
          </span>
        )}
        <h3 className="text-xl font-bold">{plan.name}</h3>
        <div className="flex items-baseline gap-1 mt-2">
          <span className="text-3xl font-extrabold">${plan.price}</span>
          <span className="text-sm text-default-500">/ {plan.interval}</span>
        </div>
      </CardHeader>
      <Divider />
      <CardBody className="px-6 py-6">
        <ul className="flex flex-col gap-3">
          {plan.features.map((feature, i) => (
            <li key={i} className="flex items-center gap-2 text-sm text-default-600">
              <Check className="h-4 w-4 text-success flex-shrink-0" />
              <span>{feature}</span>
            </li>
          ))}
        </ul>
      </CardBody>
      <CardFooter className="px-6 pb-6 pt-0">
        <Button
          color={isCurrentPlan ? "default" : "primary"}
          variant={isCurrentPlan ? "flat" : "solid"}
          className="w-full"
          isDisabled={isCurrentPlan}
        >
          {isCurrentPlan ? "Active" : "Upgrade to " + plan.name}
        </Button>
      </CardFooter>
    </Card>
  );
}
