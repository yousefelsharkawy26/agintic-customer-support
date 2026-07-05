"use client";

import { Button } from "@heroui/react";
import { TerminalSquare, Plus } from "lucide-react";

interface EmptyPromptsProps {
  onCreateClick: () => void;
}

export function EmptyPrompts({ onCreateClick }: EmptyPromptsProps) {
  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center gap-4 rounded-xl border border-dashed border-default-200 p-12 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
        <TerminalSquare className="h-8 w-8 text-primary" />
      </div>
      <div>
        <h3 className="text-lg font-semibold">No prompt templates</h3>
        <p className="mt-1 max-w-sm text-sm text-default-500">
          Create system prompts and instructions to define how your AI agents behave and respond to
          users.
        </p>
      </div>
      <Button color="primary" startContent={<Plus className="h-4 w-4" />} onPress={onCreateClick}>
        Create Template
      </Button>
    </div>
  );
}
