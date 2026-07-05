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

interface CreateCollectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { name: string; description: string }) => void;
}

export function CreateCollectionModal({ isOpen, onClose, onSubmit }: CreateCollectionModalProps) {
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
          <h2 className="text-lg font-semibold">Create Knowledge Collection</h2>
          <p className="text-sm font-normal text-default-500">
            Group related documents together for your agents to search.
          </p>
        </ModalHeader>
        <ModalBody className="gap-4">
          <Input
            label="Collection Name"
            placeholder="e.g. Product Documentation"
            variant="bordered"
            value={name}
            onValueChange={setName}
            isRequired
          />
          <Textarea
            label="Description"
            placeholder="What kind of information is in this collection?"
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
            Create Collection
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
}
