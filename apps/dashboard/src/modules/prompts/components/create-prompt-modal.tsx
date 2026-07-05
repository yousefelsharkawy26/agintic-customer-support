"use client";

import { useState } from "react";
import {
  Modal,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  Input,
  Textarea,
} from "@heroui/react";

interface CreatePromptModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { name: string; description: string }) => void;
}

export function CreatePromptModal({ isOpen, onClose, onSubmit }: CreatePromptModalProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    if (!name.trim()) return;
    setIsLoading(true);
    // Simulate API call
    await new Promise((r) => setTimeout(r, 500));
    onSubmit({ name: name.trim(), description: description.trim() });
    setIsLoading(false);
    setName("");
    setDescription("");
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="md">
      <ModalContent>
        <ModalHeader className="flex flex-col gap-1">
          <h2 className="text-lg font-semibold">Create Prompt Template</h2>
          <p className="text-sm font-normal text-default-500">
            Define system instructions for your AI agents.
          </p>
        </ModalHeader>
        <ModalBody className="gap-4">
          <Input
            label="Template Name"
            placeholder="e.g. Refund Specialist"
            variant="bordered"
            value={name}
            onValueChange={setName}
            isRequired
          />
          <Textarea
            label="Description"
            placeholder="Briefly describe what this prompt is used for."
            variant="bordered"
            value={description}
            onValueChange={setDescription}
            minRows={2}
          />
        </ModalBody>
        <ModalFooter>
          <Button variant="flat" onPress={onClose}>
            Cancel
          </Button>
          <Button
            color="primary"
            onPress={handleSubmit}
            isLoading={isLoading}
            isDisabled={!name.trim()}
          >
            Create Template
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
}
