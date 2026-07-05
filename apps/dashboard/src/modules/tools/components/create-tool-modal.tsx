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
  Select,
  SelectItem,
} from "@heroui/react";

interface CreateToolModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: {
    name: string;
    description: string;
    type: string;
    endpoint_url: string;
  }) => void;
}

export function CreateToolModal({ isOpen, onClose, onSubmit }: CreateToolModalProps) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [type, setType] = useState("");
  const [endpointUrl, setEndpointUrl] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    if (!name.trim() || !type) return;
    setIsLoading(true);
    // Simulate API call
    await new Promise((r) => setTimeout(r, 500));
    onSubmit({
      name: name.trim(),
      description: description.trim(),
      type,
      endpoint_url: endpointUrl.trim(),
    });
    setIsLoading(false);
    setName("");
    setDescription("");
    setType("");
    setEndpointUrl("");
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="md">
      <ModalContent>
        <ModalHeader className="flex flex-col gap-1">
          <h2 className="text-lg font-semibold">Connect New Tool</h2>
          <p className="text-sm font-normal text-default-500">
            Give your agents new capabilities by connecting APIs or MCP servers.
          </p>
        </ModalHeader>
        <ModalBody className="gap-4">
          <Input
            label="Tool Name"
            placeholder="e.g. Weather API"
            variant="bordered"
            value={name}
            onValueChange={setName}
            isRequired
          />
          <Select
            label="Tool Type"
            variant="bordered"
            selectedKeys={type ? [type] : []}
            onSelectionChange={(keys) => setType(Array.from(keys)[0] as string)}
            isRequired
          >
            <SelectItem key="rest_api" value="rest_api">
              REST API
            </SelectItem>
            <SelectItem key="mcp_server" value="mcp_server">
              MCP Server
            </SelectItem>
            <SelectItem key="openapi_spec" value="openapi_spec">
              OpenAPI Spec
            </SelectItem>
            <SelectItem key="custom_function" value="custom_function">
              Custom Function
            </SelectItem>
          </Select>
          <Input
            label="Endpoint URL"
            placeholder="e.g. https://api.weather.com/v1"
            variant="bordered"
            value={endpointUrl}
            onValueChange={setEndpointUrl}
          />
          <Textarea
            label="Description"
            placeholder="What does this tool do? The agent will read this."
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
            isDisabled={!name.trim() || !type}
          >
            Connect Tool
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
}
