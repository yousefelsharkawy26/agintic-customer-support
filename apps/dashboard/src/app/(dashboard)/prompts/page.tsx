"use client";

import { useState, useEffect } from "react";
import { Button, Input } from "@heroui/react";
import { Plus, Search } from "lucide-react";
import { PromptCard } from "@/modules/prompts/components/prompt-card";
import { EmptyPrompts } from "@/modules/prompts/components/empty-prompts";
import { CreatePromptModal } from "@/modules/prompts/components/create-prompt-modal";
import type { PromptTemplate } from "@/modules/prompts/types/prompt";

export default function PromptsPage() {
  const [prompts, setPrompts] = useState<PromptTemplate[]>([]);
  const [search, setSearch] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetch("/api/prompts")
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          const mapped = data.map((p) => ({
            id: p.id.toString(),
            name: p.name,
            description: p.description,
            content: p.content,
            version: p.version,
            status: p.status,
            variables: p.variables,
            created_at: p.created_at,
            updated_at: p.updated_at,
          }));
          setPrompts(mapped);
        }
      })
      .finally(() => setIsLoading(false));
  }, []);

  const filtered = prompts.filter(
    (p) =>
      p.name.toLowerCase().includes(search.toLowerCase()) ||
      p.description.toLowerCase().includes(search.toLowerCase())
  );

  const handleCreate = async (data: { name: string; description: string }) => {
    try {
      const res = await fetch("/api/prompts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: data.name,
          template: data.description || "Enter your prompt here...",
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
    return <div className="p-8 text-center text-default-500">Loading prompts...</div>;
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Prompt Management</h1>
          <p className="text-default-500">
            Design, version, and manage system instructions for your agents.
          </p>
        </div>
        <Button
          color="primary"
          startContent={<Plus className="h-4 w-4" />}
          onPress={() => setIsModalOpen(true)}
        >
          Create Template
        </Button>
      </div>

      {prompts.length > 0 && (
        <div className="flex items-center gap-3">
          <Input
            placeholder="Search prompts..."
            startContent={<Search className="h-4 w-4 text-default-400" />}
            value={search}
            onValueChange={setSearch}
            variant="bordered"
            className="max-w-xs"
          />
          <span className="text-sm text-default-400">
            {filtered.length} template{filtered.length !== 1 ? "s" : ""}
          </span>
        </div>
      )}

      {prompts.length === 0 ? (
        <EmptyPrompts onCreateClick={() => setIsModalOpen(true)} />
      ) : filtered.length === 0 ? (
        <div className="flex min-h-[200px] items-center justify-center">
          <p className="text-default-400">No prompts match &ldquo;{search}&rdquo;</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {filtered.map((prompt) => (
            <PromptCard key={prompt.id} prompt={prompt} />
          ))}
        </div>
      )}

      <CreatePromptModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreate}
      />
    </div>
  );
}
