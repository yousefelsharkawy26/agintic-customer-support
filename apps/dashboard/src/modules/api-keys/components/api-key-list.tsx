"use client";

import {
  Table,
  TableHeader,
  TableColumn,
  TableBody,
  TableRow,
  TableCell,
  Chip,
  Button,
  Dropdown,
  DropdownTrigger,
  DropdownMenu,
  DropdownItem,
} from "@heroui/react";
import { Key, MoreVertical, Copy, Trash, Clock } from "lucide-react";
import type { ApiKey } from "../types/api-key";
import { formatDistanceToNow } from "date-fns";

export function ApiKeyList({ apiKeys }: { apiKeys: ApiKey[] }) {
  if (apiKeys.length === 0) {
    return (
      <div className="flex h-40 flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-default-200">
        <p className="text-default-500">No API keys generated yet.</p>
      </div>
    );
  }

  return (
    <Table aria-label="API Keys">
      <TableHeader>
        <TableColumn>NAME</TableColumn>
        <TableColumn>SECRET KEY</TableColumn>
        <TableColumn>CREATED</TableColumn>
        <TableColumn>LAST USED</TableColumn>
        <TableColumn>STATUS</TableColumn>
        <TableColumn aria-label="Actions" align="end">
          ACTIONS
        </TableColumn>
      </TableHeader>
      <TableBody>
        {apiKeys.map((apiKey) => (
          <TableRow key={apiKey.id}>
            <TableCell>
              <div className="flex items-center gap-2">
                <div className="p-1.5 bg-default-100 rounded-md">
                  <Key className="h-4 w-4 text-default-600" />
                </div>
                <span className="font-medium">{apiKey.name}</span>
              </div>
            </TableCell>
            <TableCell>
              <div className="flex items-center gap-2">
                <code className="px-2 py-1 bg-default-100 rounded text-xs font-mono text-default-600">
                  {apiKey.key_hint}
                </code>
                <Button isIconOnly size="sm" variant="light" aria-label="Copy key hint">
                  <Copy className="h-3 w-3 text-default-400" />
                </Button>
              </div>
            </TableCell>
            <TableCell>
              <span className="text-sm text-default-500">
                {new Date(apiKey.created_at).toLocaleDateString()}
              </span>
            </TableCell>
            <TableCell>
              {apiKey.last_used_at ? (
                <div className="flex items-center gap-1.5 text-sm text-default-500">
                  <Clock className="h-3 w-3" />
                  {formatDistanceToNow(new Date(apiKey.last_used_at), { addSuffix: true })}
                </div>
              ) : (
                <span className="text-sm text-default-400">Never</span>
              )}
            </TableCell>
            <TableCell>
              <Chip
                size="sm"
                variant="flat"
                color={apiKey.status === "active" ? "success" : "default"}
              >
                {apiKey.status}
              </Chip>
            </TableCell>
            <TableCell>
              <div className="flex justify-end">
                <Dropdown placement="bottom-end">
                  <DropdownTrigger>
                    <Button isIconOnly size="sm" variant="light">
                      <MoreVertical className="h-4 w-4 text-default-400" />
                    </Button>
                  </DropdownTrigger>
                  <DropdownMenu aria-label="API Key actions">
                    <DropdownItem key="edit">Edit Name</DropdownItem>
                    <DropdownItem
                      key="revoke"
                      className="text-danger"
                      color="danger"
                      startContent={<Trash className="h-4 w-4" />}
                    >
                      Revoke Key
                    </DropdownItem>
                  </DropdownMenu>
                </Dropdown>
              </div>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
