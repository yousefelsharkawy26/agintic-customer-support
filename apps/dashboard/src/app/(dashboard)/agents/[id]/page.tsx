"use client";

import { use } from "react";
import Link from "next/link";
import {
  Button,
  Card,
  CardBody,
  CardHeader,
  Divider,
  Input,
  Select,
  SelectItem,
  Slider,
  Textarea,
  Chip,
} from "@heroui/react";
import { ArrowLeft, Bot, BookOpen, Wrench, MessageSquare, Save } from "lucide-react";
import { MOCK_AGENTS } from "@/modules/agents/api/mock-data";
import { AgentStatusBadge } from "@/modules/agents/components/agent-status-badge";

const LLM_MODELS = [
  { key: "claude-3-5-sonnet", label: "Claude 3.5 Sonnet" },
  { key: "claude-3-opus", label: "Claude 3 Opus" },
  { key: "gpt-4o", label: "GPT-4o" },
  { key: "gpt-4o-mini", label: "GPT-4o Mini" },
  { key: "gemini-1-5-pro", label: "Gemini 1.5 Pro" },
];

export default function AgentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const agent = MOCK_AGENTS.find((a) => a.id === id);

  if (!agent) {
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center gap-4">
        <p className="text-default-500">Agent not found.</p>
        <Button as={Link} href="/agents" variant="flat">
          Back to Agents
        </Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button as={Link} href="/agents" isIconOnly variant="flat" aria-label="Back to agents">
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex flex-1 items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
            <Bot className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="text-xl font-bold">{agent.name}</h1>
            <p className="text-sm text-default-500">{agent.description}</p>
          </div>
        </div>
        <AgentStatusBadge status={agent.status} />
        <Button color="primary" startContent={<Save className="h-4 w-4" />}>
          Save Changes
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Main Config */}
        <div className="flex flex-col gap-6 lg:col-span-2">
          {/* Identity */}
          <Card shadow="sm">
            <CardHeader className="px-6 pt-5 pb-2">
              <h2 className="text-base font-semibold">Identity</h2>
            </CardHeader>
            <Divider />
            <CardBody className="flex flex-col gap-4 p-6">
              <Input label="Agent Name" defaultValue={agent.name} variant="bordered" />
              <Textarea
                label="Description"
                defaultValue={agent.description}
                variant="bordered"
                minRows={2}
              />
            </CardBody>
          </Card>

          {/* LLM Configuration */}
          <Card shadow="sm">
            <CardHeader className="px-6 pt-5 pb-2">
              <h2 className="text-base font-semibold">LLM Configuration</h2>
            </CardHeader>
            <Divider />
            <CardBody className="flex flex-col gap-5 p-6">
              <Select label="Model" defaultSelectedKeys={[agent.model]} variant="bordered">
                {LLM_MODELS.map((m) => (
                  <SelectItem key={m.key}>{m.label}</SelectItem>
                ))}
              </Select>
              <div className="flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Temperature</span>
                  <Chip size="sm" variant="flat">
                    {agent.temperature}
                  </Chip>
                </div>
                <Slider
                  minValue={0}
                  maxValue={1}
                  step={0.1}
                  defaultValue={agent.temperature}
                  size="sm"
                  color="primary"
                  className="max-w-full"
                />
                <p className="text-xs text-default-400">
                  Lower = more focused. Higher = more creative.
                </p>
              </div>
              <div className="flex flex-col gap-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm">Max Tokens</span>
                  <Chip size="sm" variant="flat">
                    {agent.max_tokens.toLocaleString()}
                  </Chip>
                </div>
                <Slider
                  minValue={256}
                  maxValue={16384}
                  step={256}
                  defaultValue={agent.max_tokens}
                  size="sm"
                  color="primary"
                />
              </div>
            </CardBody>
          </Card>

          {/* System Prompt */}
          <Card shadow="sm">
            <CardHeader className="px-6 pt-5 pb-2">
              <h2 className="text-base font-semibold">System Prompt</h2>
            </CardHeader>
            <Divider />
            <CardBody className="p-6">
              <Textarea
                placeholder="You are a helpful customer support agent for Acme Corp..."
                defaultValue={agent.system_prompt}
                variant="bordered"
                minRows={6}
                description="Define the agent's persona, behavior, and constraints."
              />
            </CardBody>
          </Card>
        </div>

        {/* Sidebar stats */}
        <div className="flex flex-col gap-4">
          <Card shadow="sm">
            <CardHeader className="px-5 pt-5 pb-2">
              <h2 className="text-base font-semibold">Capabilities</h2>
            </CardHeader>
            <Divider />
            <CardBody className="flex flex-col gap-3 p-5">
              <Link href={`/tools?agent=${agent.id}`} className="group">
                <div className="flex items-center justify-between rounded-lg border border-default-200 p-3 transition-colors hover:border-primary/30 hover:bg-primary/5">
                  <div className="flex items-center gap-3">
                    <Wrench className="h-4 w-4 text-default-500" />
                    <span className="text-sm font-medium">Tools</span>
                  </div>
                  <Chip size="sm" variant="flat">
                    {agent.tools_count}
                  </Chip>
                </div>
              </Link>
              <Link href={`/knowledge-base?agent=${agent.id}`} className="group">
                <div className="flex items-center justify-between rounded-lg border border-default-200 p-3 transition-colors hover:border-primary/30 hover:bg-primary/5">
                  <div className="flex items-center gap-3">
                    <BookOpen className="h-4 w-4 text-default-500" />
                    <span className="text-sm font-medium">Knowledge Bases</span>
                  </div>
                  <Chip size="sm" variant="flat">
                    {agent.kb_count}
                  </Chip>
                </div>
              </Link>
              <Link href={`/conversations?agent=${agent.id}`}>
                <div className="flex items-center justify-between rounded-lg border border-default-200 p-3 transition-colors hover:border-primary/30 hover:bg-primary/5">
                  <div className="flex items-center gap-3">
                    <MessageSquare className="h-4 w-4 text-default-500" />
                    <span className="text-sm font-medium">Conversations</span>
                  </div>
                  <Chip size="sm" variant="flat">
                    {agent.conversations_count.toLocaleString()}
                  </Chip>
                </div>
              </Link>
            </CardBody>
          </Card>

          <Card shadow="sm">
            <CardHeader className="px-5 pt-5 pb-2">
              <h2 className="text-base font-semibold">Metadata</h2>
            </CardHeader>
            <Divider />
            <CardBody className="flex flex-col gap-2 p-5 text-sm text-default-500">
              <div className="flex justify-between">
                <span>Agent ID</span>
                <span className="font-mono text-xs">{agent.id}</span>
              </div>
              <div className="flex justify-between">
                <span>Created</span>
                <span>{new Date(agent.created_at).toLocaleDateString()}</span>
              </div>
              <div className="flex justify-between">
                <span>Updated</span>
                <span>{new Date(agent.updated_at).toLocaleDateString()}</span>
              </div>
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  );
}
