"use client";

import { use } from "react";
import Link from "next/link";
import { Button, Card, CardBody, CardHeader, Divider, Input, Chip } from "@heroui/react";
import { ArrowLeft, Wrench, Settings, PlayCircle, Globe, Server, Code } from "lucide-react";
import { MOCK_TOOLS } from "@/modules/tools/api/mock-data";

export default function ToolDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const tool = MOCK_TOOLS.find((t) => t.id === id);

  if (!tool) {
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center gap-4">
        <p className="text-default-500">Tool not found.</p>
        <Button as={Link} href="/tools" variant="flat">
          Back to Tools
        </Button>
      </div>
    );
  }

  const getIcon = () => {
    switch (tool.type) {
      case "rest_api":
        return <Globe className="h-5 w-5 text-primary" />;
      case "mcp_server":
        return <Server className="h-5 w-5 text-secondary" />;
      case "openapi_spec":
        return <Code className="h-5 w-5 text-warning" />;
      default:
        return <Wrench className="h-5 w-5 text-primary" />;
    }
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-4">
        <Button as={Link} href="/tools" isIconOnly variant="flat" aria-label="Back to tools">
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex flex-1 items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-default-100 dark:bg-default-50">
            {getIcon()}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold">{tool.name}</h1>
              <Chip size="sm" variant="flat" className="uppercase text-[10px]">
                {tool.type.replace("_", " ")}
              </Chip>
            </div>
            <p className="text-sm text-default-500">
              {tool.endpoint_url || "No endpoint URL configured"}
            </p>
          </div>
        </div>
        <Button variant="bordered" startContent={<Settings className="h-4 w-4" />}>
          Settings
        </Button>
        <Button color="primary" startContent={<PlayCircle className="h-4 w-4" />}>
          Test Tool
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="flex flex-col gap-4 lg:col-span-2">
          <Card shadow="sm">
            <CardHeader className="px-6 pt-5 pb-4">
              <h2 className="text-base font-semibold">Configuration</h2>
            </CardHeader>
            <Divider />
            <CardBody className="gap-4 p-6">
              <Input label="Tool Name" defaultValue={tool.name} variant="bordered" />
              <Input label="Description" defaultValue={tool.description} variant="bordered" />
              <Input label="Endpoint URL" defaultValue={tool.endpoint_url} variant="bordered" />
            </CardBody>
          </Card>

          <Card shadow="sm">
            <CardHeader className="px-6 pt-5 pb-4 flex justify-between">
              <h2 className="text-base font-semibold">Arguments Schema</h2>
              <Button size="sm" variant="flat">
                Add Argument
              </Button>
            </CardHeader>
            <Divider />
            <CardBody className="p-0">
              {tool.arguments && tool.arguments.length > 0 ? (
                <div className="flex flex-col">
                  {tool.arguments.map((arg, i) => (
                    <div
                      key={i}
                      className="flex items-start justify-between border-b border-divider p-4 last:border-0"
                    >
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="font-mono text-sm font-semibold">{arg.name}</span>
                          <Chip
                            size="sm"
                            variant="flat"
                            color={arg.required ? "danger" : "default"}
                          >
                            {arg.required ? "required" : "optional"}
                          </Chip>
                          <span className="text-xs text-default-400">{arg.type}</span>
                        </div>
                        <p className="mt-1 text-sm text-default-500">{arg.description}</p>
                      </div>
                      <Button size="sm" isIconOnly variant="light">
                        <Settings className="h-4 w-4 text-default-400" />
                      </Button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-6 text-center text-default-500">
                  No arguments defined for this tool.
                </div>
              )}
            </CardBody>
          </Card>
        </div>

        <div className="flex flex-col gap-4">
          <Card shadow="sm">
            <CardHeader className="px-5 pt-5 pb-2">
              <h2 className="text-base font-semibold">Usage Info</h2>
            </CardHeader>
            <Divider />
            <CardBody className="flex flex-col gap-4 p-5 text-sm">
              <div className="flex justify-between">
                <span className="text-default-500">Status</span>
                <Chip
                  size="sm"
                  color={
                    tool.status === "active"
                      ? "success"
                      : tool.status === "error"
                        ? "danger"
                        : "default"
                  }
                  variant="flat"
                >
                  {tool.status}
                </Chip>
              </div>
              <div className="flex justify-between">
                <span className="text-default-500">Last Used</span>
                <span>
                  {tool.last_used_at ? new Date(tool.last_used_at).toLocaleString() : "Never"}
                </span>
              </div>
              <div className="flex flex-col gap-1 mt-2">
                <span className="text-default-500">Created At</span>
                <span>{new Date(tool.created_at).toLocaleString()}</span>
              </div>
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  );
}
