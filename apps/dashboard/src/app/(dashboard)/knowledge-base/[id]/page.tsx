"use client";

import { use, useState } from "react";
import Link from "next/link";
import { Button, Card, CardBody, CardHeader, Divider, Input } from "@heroui/react";
import { ArrowLeft, BookOpen, Plus, Search, Settings } from "lucide-react";
import { MOCK_COLLECTIONS, MOCK_DOCUMENTS } from "@/modules/knowledge-base/api/mock-data";
import { DocumentList } from "@/modules/knowledge-base/components/document-list";
import { UploadDocumentModal } from "@/modules/knowledge-base/components/upload-document-modal";

export default function KnowledgeBaseDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const collection = MOCK_COLLECTIONS.find((c) => c.id === id);
  const documents = MOCK_DOCUMENTS.filter((d) => d.collection_id === id);

  const [search, setSearch] = useState("");
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);

  if (!collection) {
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center gap-4">
        <p className="text-default-500">Collection not found.</p>
        <Button as={Link} href="/knowledge-base" variant="flat">
          Back to Knowledge Base
        </Button>
      </div>
    );
  }

  const filteredDocs = documents.filter((d) =>
    d.title.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button
          as={Link}
          href="/knowledge-base"
          isIconOnly
          variant="flat"
          aria-label="Back to collections"
        >
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex flex-1 items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
            <BookOpen className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="text-xl font-bold">{collection.name}</h1>
            <p className="text-sm text-default-500">{collection.description}</p>
          </div>
        </div>
        <Button variant="bordered" startContent={<Settings className="h-4 w-4" />}>
          Settings
        </Button>
        <Button
          color="primary"
          startContent={<Plus className="h-4 w-4" />}
          onPress={() => setIsUploadModalOpen(true)}
        >
          Add Document
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-4">
        {/* Main Content: Document List */}
        <div className="flex flex-col gap-4 lg:col-span-3">
          <Card shadow="sm">
            <CardHeader className="flex justify-between px-6 pt-5 pb-4">
              <h2 className="text-base font-semibold">Documents</h2>
              <Input
                placeholder="Search documents..."
                startContent={<Search className="h-4 w-4 text-default-400" />}
                value={search}
                onValueChange={setSearch}
                size="sm"
                variant="bordered"
                className="w-64"
              />
            </CardHeader>
            <Divider />
            <DocumentList documents={filteredDocs} />
          </Card>
        </div>

        {/* Sidebar: Collection Stats & Test Search */}
        <div className="flex flex-col gap-4">
          <Card shadow="sm">
            <CardHeader className="px-5 pt-5 pb-2">
              <h2 className="text-base font-semibold">Status</h2>
            </CardHeader>
            <Divider />
            <CardBody className="flex flex-col gap-4 p-5 text-sm">
              <div className="flex justify-between">
                <span className="text-default-500">Documents</span>
                <span className="font-medium">{collection.document_count}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-default-500">Text Chunks</span>
                <span className="font-medium">{collection.chunk_count.toLocaleString()}</span>
              </div>
              <div className="flex flex-col gap-1 mt-2">
                <span className="text-default-500">Last Synced</span>
                <span>{new Date(collection.last_synced_at).toLocaleString()}</span>
              </div>
            </CardBody>
          </Card>

          <Card shadow="sm" className="bg-primary-50 dark:bg-primary-50/5">
            <CardHeader className="px-5 pt-5 pb-2">
              <h2 className="text-base font-semibold text-primary-700 dark:text-primary-400">
                Test Semantic Search
              </h2>
            </CardHeader>
            <CardBody className="p-5 pt-2 flex flex-col gap-3">
              <p className="text-xs text-primary-600 dark:text-primary-400/80">
                Test how well your agents can retrieve information from this collection.
              </p>
              <Input
                placeholder="Ask a question..."
                variant="bordered"
                size="sm"
                className="bg-white dark:bg-default-100"
              />
              <Button size="sm" color="primary" className="w-full">
                Test Search
              </Button>
            </CardBody>
          </Card>
        </div>
      </div>

      <UploadDocumentModal isOpen={isUploadModalOpen} onClose={() => setIsUploadModalOpen(false)} />
    </div>
  );
}
