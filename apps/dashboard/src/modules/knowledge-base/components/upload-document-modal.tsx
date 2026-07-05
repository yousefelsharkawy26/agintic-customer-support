"use client";

import { useState } from "react";
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  Tabs,
  Tab,
  Input,
  Textarea,
} from "@heroui/react";
import { UploadCloud, Link as LinkIcon, FileText } from "lucide-react";

interface UploadDocumentModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function UploadDocumentModal({ isOpen, onClose }: UploadDocumentModalProps) {
  const [selectedTab, setSelectedTab] = useState("file");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    setIsLoading(true);
    // Simulate API call
    await new Promise((r) => setTimeout(r, 1000));
    setIsLoading(false);
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalContent>
        <ModalHeader className="flex flex-col gap-1">
          <h2 className="text-lg font-semibold">Add to Knowledge Base</h2>
          <p className="text-sm font-normal text-default-500">
            Upload documents, add URLs, or paste raw text to expand this collection.
          </p>
        </ModalHeader>
        <ModalBody>
          <Tabs
            selectedKey={selectedTab}
            onSelectionChange={(key) => setSelectedTab(key as string)}
            variant="underlined"
            color="primary"
          >
            <Tab
              key="file"
              title={
                <div className="flex items-center gap-2">
                  <UploadCloud className="h-4 w-4" />
                  <span>File Upload</span>
                </div>
              }
            >
              <div className="flex flex-col items-center justify-center gap-4 rounded-lg border-2 border-dashed border-default-200 p-10 mt-4">
                <div className="rounded-full bg-primary/10 p-3">
                  <UploadCloud className="h-6 w-6 text-primary" />
                </div>
                <div className="text-center">
                  <p className="text-sm font-medium">Click to upload or drag and drop</p>
                  <p className="text-xs text-default-400 mt-1">PDF, Markdown, or TXT (max 10MB)</p>
                </div>
                <Button color="primary" variant="flat" size="sm">
                  Select Files
                </Button>
              </div>
            </Tab>
            <Tab
              key="url"
              title={
                <div className="flex items-center gap-2">
                  <LinkIcon className="h-4 w-4" />
                  <span>Web URL</span>
                </div>
              }
            >
              <div className="flex flex-col gap-4 mt-4">
                <Input
                  label="Website URL"
                  placeholder="https://docs.example.com/guide"
                  variant="bordered"
                  description="We will crawl this page and extract the main content."
                />
              </div>
            </Tab>
            <Tab
              key="text"
              title={
                <div className="flex items-center gap-2">
                  <FileText className="h-4 w-4" />
                  <span>Raw Text</span>
                </div>
              }
            >
              <div className="flex flex-col gap-4 mt-4">
                <Input label="Document Title" placeholder="e.g. Refund Policy" variant="bordered" />
                <Textarea
                  label="Content"
                  placeholder="Paste your text content here..."
                  variant="bordered"
                  minRows={6}
                />
              </div>
            </Tab>
          </Tabs>
        </ModalBody>
        <ModalFooter>
          <Button variant="flat" onPress={onClose}>
            Cancel
          </Button>
          <Button color="primary" onPress={handleSubmit} isLoading={isLoading}>
            Add Document
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
}
