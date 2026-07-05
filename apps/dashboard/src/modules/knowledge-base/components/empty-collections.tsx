"use client";

import { Button } from "@heroui/react";
import { BookOpen, Plus } from "lucide-react";

interface EmptyCollectionsProps {
  onCreateClick: () => void;
}

export function EmptyCollections({ onCreateClick }: EmptyCollectionsProps) {
  return (
    <div className="flex min-h-[400px] flex-col items-center justify-center gap-4 rounded-xl border border-dashed border-default-200 p-12 text-center">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
        <BookOpen className="h-8 w-8 text-primary" />
      </div>
      <div>
        <h3 className="text-lg font-semibold">No knowledge collections</h3>
        <p className="mt-1 max-w-sm text-sm text-default-500">
          Create a collection to upload documents, URLs, and text. Your agents can then use this
          knowledge base to answer questions accurately.
        </p>
      </div>
      <Button color="primary" startContent={<Plus className="h-4 w-4" />} onPress={onCreateClick}>
        Create Collection
      </Button>
    </div>
  );
}
