"use client";

import { useState, useEffect } from "react";
import { Button, Input } from "@heroui/react";
import { Plus, Search } from "lucide-react";
import { ToolCard } from "@/modules/tools/components/tool-card";
import { EmptyTools } from "@/modules/tools/components/empty-tools";
import { CreateToolModal } from "@/modules/tools/components/create-tool-modal";
import type { CustomTool } from "@/modules/tools/types/tool";

export default function ToolsPage() {
  const [tools, setTools] = useState<CustomTool[]>([]);
  const [search, setSearch] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetch("/api/tools")
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          const mapped = data.map((d) => ({
            id: d.id,
            name: d.name,
            description: `Server: ${d.server_url}`,
            type: "mcp_server" as CustomTool["type"],
            endpoint_url: d.server_url,
            status: (d.is_active ? "active" : "error") as CustomTool["status"],
            created_at: new Date().toISOString(),
          }));
          setTools(mapped);
        }
      })
      .finally(() => setIsLoading(false));
  }, []);

  const filtered = tools.filter(
    (t) =>
      t.name.toLowerCase().includes(search.toLowerCase()) ||
      t.description.toLowerCase().includes(search.toLowerCase())
  );

  const handleCreate = async (data: {
    name: string;
    description: string;
    type: string;
    endpoint_url: string;
  }) => {
    try {
      const res = await fetch("/api/tools", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: data.name,
          server_url: data.endpoint_url,
          transport: "http",
        }),
      });
      if (res.ok) {
        window.location.reload();
      }
    } catch (e) {
      console.error(e);
    }
  };

  if (isLoading) {
    return <div className="p-8 text-center text-default-500">Loading tools...</div>;
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Tools & Capabilities</h1>
          <p className="text-default-500">
            Connect APIs, MCP servers, and custom logic for your agents to use.
          </p>
        </div>
        <Button
          color="primary"
          startContent={<Plus className="h-4 w-4" />}
          onPress={() => setIsModalOpen(true)}
        >
          Connect Tool
        </Button>
      </div>

      {tools.length > 0 && (
        <div className="flex items-center gap-3">
          <Input
            placeholder="Search tools..."
            startContent={<Search className="h-4 w-4 text-default-400" />}
            value={search}
            onValueChange={setSearch}
            variant="bordered"
            className="max-w-xs"
          />
          <span className="text-sm text-default-400">
            {filtered.length} tool{filtered.length !== 1 ? "s" : ""}
          </span>
        </div>
      )}

      {tools.length === 0 ? (
        <EmptyTools onCreateClick={() => setIsModalOpen(true)} />
      ) : filtered.length === 0 ? (
        <div className="flex min-h-[200px] items-center justify-center">
          <p className="text-default-400">No tools match &ldquo;{search}&rdquo;</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((tool) => (
            <ToolCard key={tool.id} tool={tool} />
          ))}
        </div>
      )}

      <CreateToolModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreate}
      />
    </div>
  );
}
