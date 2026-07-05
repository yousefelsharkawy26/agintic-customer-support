"use client";

import { Card, CardBody, CardFooter, Button, Tooltip } from "@heroui/react";
import { Bot, BookOpen, Wrench, MessageSquare, ArrowRight, MoreVertical } from "lucide-react";
import Link from "next/link";
import type { Agent } from "../types/agent";
import { AgentStatusBadge } from "./agent-status-badge";

const MODEL_LABELS: Record<string, string> = {
  "claude-3-5-sonnet": "Claude 3.5 Sonnet",
  "claude-3-opus": "Claude 3 Opus",
  "gpt-4o": "GPT-4o",
  "gpt-4o-mini": "GPT-4o Mini",
  "gemini-1-5-pro": "Gemini 1.5 Pro",
};

export function AgentCard({ agent }: { agent: Agent }) {
  return (
    <Card shadow="sm" className="group flex flex-col transition-shadow hover:shadow-md">
      <CardBody className="flex flex-col gap-4 p-5">
        {/* Header */}
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-primary/10">
              <Bot className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="font-semibold leading-tight">{agent.name}</p>
              <p className="text-xs text-default-400">{MODEL_LABELS[agent.model] ?? agent.model}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <AgentStatusBadge status={agent.status} />
            <Tooltip content="More options">
              <Button isIconOnly size="sm" variant="light">
                <MoreVertical className="h-4 w-4 text-default-400" />
              </Button>
            </Tooltip>
          </div>
        </div>

        {/* Description */}
        <p className="line-clamp-2 text-sm text-default-500">{agent.description}</p>

        {/* Stats */}
        <div className="flex items-center gap-5 border-t border-divider pt-3">
          <Tooltip content="Tools connected">
            <div className="flex items-center gap-1.5 text-xs text-default-500">
              <Wrench className="h-3.5 w-3.5" />
              <span>{agent.tools_count} tools</span>
            </div>
          </Tooltip>
          <Tooltip content="Knowledge bases linked">
            <div className="flex items-center gap-1.5 text-xs text-default-500">
              <BookOpen className="h-3.5 w-3.5" />
              <span>{agent.kb_count} KB</span>
            </div>
          </Tooltip>
          <Tooltip content="Total conversations">
            <div className="flex items-center gap-1.5 text-xs text-default-500">
              <MessageSquare className="h-3.5 w-3.5" />
              <span>{agent.conversations_count.toLocaleString()}</span>
            </div>
          </Tooltip>
        </div>
      </CardBody>

      <CardFooter className="px-5 pb-5 pt-0">
        <Button
          as={Link}
          href={`/agents/${agent.id}`}
          size="sm"
          variant="flat"
          color="primary"
          className="w-full"
          endContent={<ArrowRight className="h-4 w-4" />}
        >
          Configure
        </Button>
      </CardFooter>
    </Card>
  );
}
