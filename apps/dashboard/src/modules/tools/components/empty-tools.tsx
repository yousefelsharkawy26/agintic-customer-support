"use client";

import { Button } from "@heroui/react";
import { Wrench, Plus } from "lucide-react";

interface EmptyToolsProps {
  onCreateClick: () => void;
}

export function EmptyTools({ onCreateClick }: EmptyToolsProps) {
  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center gap-4 rounded-xl border border-dashed border-default-200 p-12 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
        <Wrench className="h-8 w-8 text-primary" />
      </div>
      <div>
        <h3 className="text-lg font-semibold">No tools connected</h3>
        <p className="mt-1 max-w-sm text-sm text-default-500">
          Connect your first custom tool, REST API, or MCP server to give your agents the ability to
          take actions.
        </p>
      </div>
      <Button color="primary" startContent={<Plus className="h-4 w-4" />} onPress={onCreateClick}>
        Connect Tool
      </Button>
    </div>
  );
}
