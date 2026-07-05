"use client";

import { Card, CardBody, CardFooter, Button, Chip } from "@heroui/react";
import { BookOpen, FileText, LayoutGrid, ArrowRight, RefreshCw, AlertCircle } from "lucide-react";
import Link from "next/link";
import type { KnowledgeCollection } from "../types/kb";

export function CollectionCard({ collection }: { collection: KnowledgeCollection }) {
  const getStatusDisplay = () => {
    switch (collection.status) {
      case "syncing":
        return (
          <Chip
            size="sm"
            color="primary"
            variant="flat"
            startContent={<RefreshCw className="h-3 w-3 animate-spin" />}
          >
            Syncing
          </Chip>
        );
      case "failed":
        return (
          <Chip
            size="sm"
            color="danger"
            variant="flat"
            startContent={<AlertCircle className="h-3 w-3" />}
          >
            Failed
          </Chip>
        );
      case "completed":
        return (
          <Chip size="sm" color="success" variant="flat">
            Ready
          </Chip>
        );
      default:
        return (
          <Chip size="sm" color="default" variant="flat">
            Idle
          </Chip>
        );
    }
  };

  return (
    <Card shadow="sm" className="group flex flex-col transition-shadow hover:shadow-md">
      <CardBody className="flex flex-col gap-4 p-5">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-primary/10">
              <BookOpen className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="font-semibold leading-tight">{collection.name}</p>
              <p className="text-xs text-default-400">
                Last synced: {new Date(collection.last_synced_at).toLocaleDateString()}
              </p>
            </div>
          </div>
          {getStatusDisplay()}
        </div>

        <p className="line-clamp-2 text-sm text-default-500">{collection.description}</p>

        <div className="flex items-center gap-5 border-t border-divider pt-3">
          <div className="flex items-center gap-1.5 text-xs text-default-500">
            <FileText className="h-3.5 w-3.5" />
            <span>{collection.document_count} docs</span>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-default-500">
            <LayoutGrid className="h-3.5 w-3.5" />
            <span>{collection.chunk_count.toLocaleString()} chunks</span>
          </div>
        </div>
      </CardBody>

      <CardFooter className="px-5 pb-5 pt-0">
        <Button
          as={Link}
          href={`/knowledge-base/${collection.id}`}
          size="sm"
          variant="flat"
          color="primary"
          className="w-full"
          endContent={<ArrowRight className="h-4 w-4" />}
        >
          Manage
        </Button>
      </CardFooter>
    </Card>
  );
}
