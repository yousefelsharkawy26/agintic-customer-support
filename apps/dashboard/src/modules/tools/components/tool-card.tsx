"use client";

import { Card, CardBody, CardFooter, Button, Chip } from "@heroui/react";
import { Wrench, Globe, Server, Code, AlertCircle, PlayCircle } from "lucide-react";
import Link from "next/link";
import type { CustomTool } from "../types/tool";

export function ToolCard({ tool }: { tool: CustomTool }) {
  const getIcon = () => {
    switch (tool.type) {
      case "rest_api":
        return <Globe className="h-5 w-5 text-primary" />;
      case "mcp_server":
        return <Server className="h-5 w-5 text-secondary" />;
      case "openapi_spec":
        return <Code className="h-5 w-5 text-warning" />;
      default:
        return <Wrench className="h-5 w-5 text-default-500" />;
    }
  };

  const getStatusDisplay = () => {
    switch (tool.status) {
      case "active":
        return (
          <Chip size="sm" color="success" variant="flat">
            Active
          </Chip>
        );
      case "error":
        return (
          <Chip
            size="sm"
            color="danger"
            variant="flat"
            startContent={<AlertCircle className="h-3 w-3" />}
          >
            Error
          </Chip>
        );
      default:
        return (
          <Chip size="sm" color="default" variant="flat">
            Inactive
          </Chip>
        );
    }
  };

  return (
    <Card shadow="sm" className="group flex flex-col transition-shadow hover:shadow-md">
      <CardBody className="flex flex-col gap-4 p-5">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-default-100 dark:bg-default-50">
              {getIcon()}
            </div>
            <div>
              <p className="font-semibold leading-tight">{tool.name}</p>
              <p className="text-xs uppercase text-default-400">{tool.type.replace("_", " ")}</p>
            </div>
          </div>
          {getStatusDisplay()}
        </div>

        <p className="line-clamp-2 text-sm text-default-500">{tool.description}</p>

        {tool.endpoint_url && (
          <div className="mt-auto border-t border-divider pt-3 text-xs text-default-400 truncate">
            {tool.endpoint_url}
          </div>
        )}
      </CardBody>

      <CardFooter className="flex gap-2 px-5 pb-5 pt-0">
        <Button
          as={Link}
          href={`/tools/${tool.id}`}
          size="sm"
          variant="flat"
          color="primary"
          className="flex-1"
        >
          Configure
        </Button>
        <Button size="sm" isIconOnly variant="bordered" color="default" aria-label="Test tool">
          <PlayCircle className="h-4 w-4" />
        </Button>
      </CardFooter>
    </Card>
  );
}
