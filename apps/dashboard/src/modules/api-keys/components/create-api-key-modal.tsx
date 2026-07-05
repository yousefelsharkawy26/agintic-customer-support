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
} from "@heroui/react";

interface CreateApiKeyModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { name: string }) => void;
}

export function CreateApiKeyModal({ isOpen, onClose, onSubmit }: CreateApiKeyModalProps) {
  const [name, setName] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    if (!name.trim()) return;
    setIsLoading(true);
    // Simulate API call
    await new Promise((r) => setTimeout(r, 500));
    onSubmit({ name: name.trim() });
    setIsLoading(false);
    setName("");
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="md">
      <ModalContent>
        <ModalHeader className="flex flex-col gap-1">
          <h2 className="text-lg font-semibold">Create new secret key</h2>
          <p className="text-sm font-normal text-default-500">
            This key will allow external applications to authenticate with your workspace APIs.
          </p>
        </ModalHeader>
        <ModalBody className="gap-4">
          <Input
            label="Key Name"
            placeholder="e.g. My Next.js App"
            variant="bordered"
            value={name}
            onValueChange={setName}
            autoFocus
            isRequired
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
            Create secret key
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
}
