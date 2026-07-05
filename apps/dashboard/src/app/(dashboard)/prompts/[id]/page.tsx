"use client";

import { use, useState, useEffect } from "react";
import Link from "next/link";
import { Button, Card, CardBody, CardHeader, Divider, Input, Textarea, Chip } from "@heroui/react";
import { ArrowLeft, TerminalSquare, Save, PlayCircle, History } from "lucide-react";
import type { PromptTemplate } from "@/modules/prompts/types/prompt";

export default function PromptDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [prompt, setPrompt] = useState<PromptTemplate | null>(null);
  const [content, setContent] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/prompts/${id}`)
      .then((res) => res.json())
      .then((data) => {
        if (!data.error) {
          const mapped: PromptTemplate = {
            id: data.id.toString(),
            name: data.name,
            description: `Version: v${data.version}`,
            content: data.template,
            version: `v${data.version}`,
            status: data.is_active ? "active" : "draft",
            variables: [], // We don't parse variables from template yet
            created_at: data.created_at,
            updated_at: data.created_at,
          };
          setPrompt(mapped);
          setContent(data.template || "");
        }
      })
      .finally(() => setIsLoading(false));
  }, [id]);

  if (isLoading) {
    return <div className="p-8 text-center text-default-500">Loading prompt...</div>;
  }

  if (!prompt) {
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center gap-4">
        <p className="text-default-500">Prompt not found.</p>
        <Button as={Link} href="/prompts" variant="flat">
          Back to Prompts
        </Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6 h-[calc(100vh-8rem)]">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button as={Link} href="/prompts" isIconOnly variant="flat" aria-label="Back to prompts">
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex flex-1 items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
            <TerminalSquare className="h-5 w-5 text-primary" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold">{prompt.name}</h1>
              <Chip
                size="sm"
                variant="flat"
                color={
                  prompt.status === "active"
                    ? "success"
                    : prompt.status === "draft"
                      ? "warning"
                      : "default"
                }
              >
                {prompt.status}
              </Chip>
            </div>
            <p className="text-sm text-default-500">{prompt.description}</p>
          </div>
        </div>
        <Button variant="bordered" startContent={<History className="h-4 w-4" />}>
          History
        </Button>
        <Button color="primary" startContent={<Save className="h-4 w-4" />}>
          Save Version
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-4 min-h-0 flex-1">
        {/* Editor Area */}
        <div className="flex flex-col gap-4 lg:col-span-3 min-h-0">
          <Card shadow="sm" className="flex-1 flex flex-col min-h-0">
            <CardHeader className="px-6 pt-5 pb-4 flex justify-between items-center">
              <div className="flex items-center gap-2">
                <h2 className="text-base font-semibold">Prompt Content</h2>
                <Chip size="sm" variant="faded">
                  {prompt.version}
                </Chip>
              </div>
            </CardHeader>
            <Divider />
            <CardBody className="p-0 flex-1 flex flex-col min-h-0">
              <Textarea
                placeholder="Write your system prompt here. Use {{variable_name}} to inject dynamic data."
                value={content}
                onValueChange={setContent}
                classNames={{
                  base: "flex-1 min-h-0 h-full",
                  inputWrapper:
                    "h-full min-h-0 rounded-none border-0 shadow-none bg-transparent hover:bg-transparent focus-within:bg-transparent",
                  input: "h-full font-mono text-sm leading-relaxed resize-none",
                }}
              />
            </CardBody>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="flex flex-col gap-4 overflow-y-auto">
          <Card shadow="sm">
            <CardHeader className="px-5 pt-5 pb-2">
              <h2 className="text-base font-semibold">Variables</h2>
            </CardHeader>
            <Divider />
            <CardBody className="p-5 flex flex-col gap-4">
              {prompt.variables && prompt.variables.length > 0 ? (
                prompt.variables.map((v) => (
                  <div key={v.name}>
                    <Chip size="sm" variant="flat" color="primary" className="mb-1">
                      {`{{${v.name}}}`}
                    </Chip>
                    <p className="text-xs text-default-500 leading-tight">{v.description}</p>
                  </div>
                ))
              ) : (
                <p className="text-sm text-default-500">No variables defined.</p>
              )}
            </CardBody>
          </Card>

          <Card shadow="sm" className="bg-primary-50 dark:bg-primary-50/5">
            <CardHeader className="px-5 pt-5 pb-2">
              <h2 className="text-base font-semibold text-primary-700 dark:text-primary-400">
                Playground
              </h2>
            </CardHeader>
            <CardBody className="p-5 pt-2 flex flex-col gap-3">
              <p className="text-xs text-primary-600 dark:text-primary-400/80">
                Test this prompt by filling in the variables below.
              </p>
              {prompt.variables &&
                prompt.variables.map((v) => (
                  <Input
                    key={v.name}
                    placeholder={`Value for ${v.name}`}
                    size="sm"
                    variant="bordered"
                    className="bg-white dark:bg-default-100"
                  />
                ))}
              <Button
                size="sm"
                color="primary"
                className="w-full mt-2"
                startContent={<PlayCircle className="h-4 w-4" />}
              >
                Test Execution
              </Button>
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  );
}
