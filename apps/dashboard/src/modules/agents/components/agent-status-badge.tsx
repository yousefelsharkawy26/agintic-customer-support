"use client";

import { Chip } from "@heroui/react";
import type { AgentStatus } from "../types/agent";

const statusConfig: Record<
  AgentStatus,
  { label: string; color: "success" | "default" | "warning" }
> = {
  active: { label: "Active", color: "success" },
  inactive: { label: "Inactive", color: "default" },
  draft: { label: "Draft", color: "warning" },
};

export function AgentStatusBadge({ status }: { status: AgentStatus }) {
  const { label, color } = statusConfig[status];
  return (
    <Chip size="sm" color={color} variant="flat">
      {label}
    </Chip>
  );
}
