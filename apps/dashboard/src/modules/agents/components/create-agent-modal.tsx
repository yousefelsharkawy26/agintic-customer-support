"use client";

import { useState } from "react";
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  Input,
  Textarea,
  Select,
  SelectItem,
} from "@heroui/react";
import type { Agent } from "@/modules/agents/types/agent";

const LLM_MODELS = [
  { key: "gpt-4o", label: "GPT-4o" },
  { key: "gpt-4o-mini", label: "GPT-4o Mini" },
  { key: "claude-3-5-sonnet", label: "Claude 3.5 Sonnet" },
  { key: "claude-3-opus", label: "Claude 3 Opus" },
  { key: "gemini-1-5-pro", label: "Gemini 1.5 Pro" },
];

interface CreateAgentModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (agent: Agent) => void;
}

export function CreateAgentModal({ isOpen, onClose, onSubmit }: CreateAgentModalProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [model, setModel] = useState<string>("gpt-4o");
  const [systemPrompt, setSystemPrompt] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!name.trim()) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/agents", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: name.trim(),
          description: description.trim(),
          model,
          system_prompt: systemPrompt.trim(),
          status: "draft",
        }),
      });
      if (!res.ok) {
        const err = await res.json();
        setError(err.message || "Failed to create agent.");
        return;
      }
      const created = await res.json();
      const agent: Agent = {
        ...created,
        tools_count: created.enabled_tool_ids?.length ?? 0,
        kb_count: created.knowledge_collection_ids?.length ?? 0,
        conversations_count: 0,
      };
      onSubmit(agent);
      setName("");
      setDescription("");
      setModel("gpt-4o");
      setSystemPrompt("");
      onClose();
    } catch {
      setError("An unexpected error occurred.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalContent>
        <ModalHeader className="flex flex-col gap-1">
          <h2 className="text-lg font-semibold">Create New Agent</h2>
          <p className="text-sm font-normal text-default-500">
            Configure the core settings for your AI agent.
          </p>
        </ModalHeader>
        <ModalBody className="gap-4">
          {error && (
            <p className="text-sm text-danger bg-danger-50 dark:bg-danger-50/10 rounded-lg px-4 py-2">
              {error}
            </p>
          )}
          <Input
            label="Agent Name"
            placeholder="e.g. Billing Support Agent"
            variant="bordered"
            value={name}
            onValueChange={setName}
            isRequired
          />
          <Textarea
            label="Description"
            placeholder="What does this agent specialise in?"
            variant="bordered"
            value={description}
            onValueChange={setDescription}
            minRows={2}
          />
          <Select
            label="LLM Model"
            variant="bordered"
            selectedKeys={[model]}
            onSelectionChange={(keys) => setModel(Array.from(keys)[0] as string)}
          >
            {LLM_MODELS.map((m) => (
              <SelectItem key={m.key}>{m.label}</SelectItem>
            ))}
          </Select>
          <Textarea
            label="System Prompt"
            placeholder="You are a helpful billing support agent for Acme Corp. You help customers with invoices, payment issues, and subscription changes..."
            variant="bordered"
            value={systemPrompt}
            onValueChange={setSystemPrompt}
            minRows={4}
            description="Defines how the agent behaves. You can edit this in detail after creation."
          />
        </ModalBody>
        <ModalFooter>
          <Button variant="flat" onPress={onClose}>
            Cancel
          </Button>
          <Button
            color="primary"
            onPress={handleSubmit}
            isLoading={isLoading}
            isDisabled={!name.trim()}
          >
            Create Agent
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
}
