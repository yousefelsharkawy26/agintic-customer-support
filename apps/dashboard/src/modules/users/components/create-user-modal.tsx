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
  Select,
  SelectItem,
} from "@heroui/react";

interface CreateUserModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: { name: string; email: string; role: string }) => void;
}

export function CreateUserModal({ isOpen, onClose, onSubmit }: CreateUserModalProps) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState("support_agent");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    if (!name.trim() || !email.trim() || !role) return;
    setIsLoading(true);
    // Simulate API call
    await new Promise((r) => setTimeout(r, 500));
    onSubmit({ name: name.trim(), email: email.trim(), role });
    setIsLoading(false);
    setName("");
    setEmail("");
    setRole("support_agent");
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="md">
      <ModalContent>
        <ModalHeader className="flex flex-col gap-1">
          <h2 className="text-lg font-semibold">Invite User</h2>
          <p className="text-sm font-normal text-default-500">
            Send an email invitation to add a new member to your workspace.
          </p>
        </ModalHeader>
        <ModalBody className="gap-4">
          <Input
            label="Full Name"
            placeholder="e.g. Jane Doe"
            variant="bordered"
            value={name}
            onValueChange={setName}
            isRequired
          />
          <Input
            label="Email Address"
            type="email"
            placeholder="jane@example.com"
            variant="bordered"
            value={email}
            onValueChange={setEmail}
            isRequired
          />
          <Select
            label="Role"
            variant="bordered"
            selectedKeys={[role]}
            onSelectionChange={(keys) => setRole(Array.from(keys)[0] as string)}
            isRequired
          >
            <SelectItem key="admin" value="admin">
              Administrator
            </SelectItem>
            <SelectItem key="manager" value="manager">
              Manager
            </SelectItem>
            <SelectItem key="support_agent" value="support_agent">
              Support Agent
            </SelectItem>
            <SelectItem key="viewer" value="viewer">
              Viewer
            </SelectItem>
          </Select>
        </ModalBody>
        <ModalFooter>
          <Button variant="flat" onPress={onClose}>
            Cancel
          </Button>
          <Button
            color="primary"
            onPress={handleSubmit}
            isLoading={isLoading}
            isDisabled={!name.trim() || !email.trim() || !role}
          >
            Send Invite
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
}
