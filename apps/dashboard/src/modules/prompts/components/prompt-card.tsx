"use client";

import { Card, CardBody, CardFooter, Button, Chip } from "@heroui/react";
import { TerminalSquare, ArrowRight, GitBranch } from "lucide-react";
import Link from "next/link";
import type { PromptTemplate } from "../types/prompt";

export function PromptCard({ prompt }: { prompt: PromptTemplate }) {
  const getStatusDisplay = () => {
    switch (prompt.status) {
      case "active":
        return (
          <Chip size="sm" color="success" variant="flat">
            Active
          </Chip>
        );
      case "draft":
        return (
          <Chip size="sm" color="warning" variant="flat">
            Draft
          </Chip>
        );
      default:
        return (
          <Chip size="sm" color="default" variant="flat">
            Archived
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
              <TerminalSquare className="h-5 w-5 text-primary" />
            </div>
            <div>
              <p className="font-semibold leading-tight">{prompt.name}</p>
              <div className="flex items-center gap-2 mt-1">
                <GitBranch className="h-3 w-3 text-default-400" />
                <p className="text-xs text-default-400">{prompt.version}</p>
              </div>
            </div>
          </div>
          {getStatusDisplay()}
        </div>

        <p className="line-clamp-2 text-sm text-default-500">{prompt.description}</p>

        <div className="mt-auto border-t border-divider pt-3 flex flex-wrap gap-1">
          {prompt.variables.length > 0 ? (
            prompt.variables.map((v) => (
              <Chip key={v.name} size="sm" variant="faded" className="text-[10px]">
                {`{{${v.name}}}`}
              </Chip>
            ))
          ) : (
            <span className="text-xs text-default-400">No variables</span>
          )}
        </div>
      </CardBody>

      <CardFooter className="px-5 pb-5 pt-0">
        <Button
          as={Link}
          href={`/prompts/${prompt.id}`}
          size="sm"
          variant="flat"
          color="primary"
          className="w-full"
          endContent={<ArrowRight className="h-4 w-4" />}
        >
          Edit Prompt
        </Button>
      </CardFooter>
    </Card>
  );
}
