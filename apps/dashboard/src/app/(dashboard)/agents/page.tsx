"use client";

import { useState, useEffect } from "react";
import { Button, Input } from "@heroui/react";
import { Plus, Search } from "lucide-react";
import { AgentCard } from "@/modules/agents/components/agent-card";
import { EmptyAgents } from "@/modules/agents/components/empty-agents";
import { CreateAgentModal } from "@/modules/agents/components/create-agent-modal";
import type { Agent } from "@/modules/agents/types/agent";

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);

  useEffect(() => {
    fetch("/api/agents")
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          const mapped: Agent[] = data.map((a) => ({
            id: a.id,
            name: a.name,
            description: a.description,
            model: a.model,
            status: a.status,
            system_prompt: a.system_prompt,
            temperature: a.temperature,
            max_tokens: a.max_tokens,
            enabled_tool_ids: a.enabled_tool_ids ?? [],
            knowledge_collection_ids: a.knowledge_collection_ids ?? [],
            tools_count: a.enabled_tool_ids?.length ?? 0,
            kb_count: a.knowledge_collection_ids?.length ?? 0,
            conversations_count: 0,
            created_at: a.created_at,
            updated_at: a.updated_at,
          }));
          setAgents(mapped);
        }
      })
      .finally(() => setIsLoading(false));
  }, []);

  const filtered = agents.filter(
    (a) =>
      a.name.toLowerCase().includes(search.toLowerCase()) ||
      a.description.toLowerCase().includes(search.toLowerCase())
  );

  const handleCreate = (newAgent: Agent) => {
    setAgents((prev) => [newAgent, ...prev]);
  };

  if (isLoading) {
    return <div className="p-8 text-center text-default-500">Loading agents...</div>;
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Page Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Agents</h1>
          <p className="text-default-500">Manage your AI agents and their capabilities.</p>
        </div>
        <Button
          color="primary"
          startContent={<Plus className="h-4 w-4" />}
          onPress={() => setIsModalOpen(true)}
        >
          New Agent
        </Button>
      </div>

      {/* Search & Filters */}
      {agents.length > 0 && (
        <div className="flex items-center gap-3">
          <Input
            placeholder="Search agents..."
            startContent={<Search className="h-4 w-4 text-default-400" />}
            value={search}
            onValueChange={setSearch}
            variant="bordered"
            className="max-w-xs"
          />
          <span className="text-sm text-default-400">
            {filtered.length} agent{filtered.length !== 1 ? "s" : ""}
          </span>
        </div>
      )}

      {/* Agent Grid or Empty State */}
      {agents.length === 0 ? (
        <EmptyAgents onCreateClick={() => setIsModalOpen(true)} />
      ) : filtered.length === 0 ? (
        <div className="flex min-h-[200px] items-center justify-center">
          <p className="text-default-400">No agents match &ldquo;{search}&rdquo;</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((agent) => (
            <AgentCard key={agent.id} agent={agent} />
          ))}
        </div>
      )}

      {/* Create Modal */}
      <CreateAgentModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreate}
      />
    </div>
  );
}
