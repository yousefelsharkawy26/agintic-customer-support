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
import {
  MoreVertical,
  FileText,
  FileDown,
  Link as LinkIcon,
  RefreshCw,
  AlertCircle,
  Trash,
} from "lucide-react";
import type { KnowledgeDocument } from "../types/kb";

const getDocumentIcon = (type: KnowledgeDocument["type"]) => {
  switch (type) {
    case "pdf":
      return <FileDown className="h-4 w-4 text-danger" />;
    case "markdown":
      return <FileText className="h-4 w-4 text-primary" />;
    case "url":
      return <LinkIcon className="h-4 w-4 text-secondary" />;
    default:
      return <FileText className="h-4 w-4 text-default-500" />;
  }
};

const formatBytes = (bytes: number) => {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + " " + sizes[i];
};

export function DocumentList({ documents }: { documents: KnowledgeDocument[] }) {
  if (documents.length === 0) {
    return (
      <div className="flex h-40 flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-default-200">
        <p className="text-default-500">No documents in this collection yet.</p>
      </div>
    );
  }

  return (
    <Table aria-label="Documents in collection">
      <TableHeader>
        <TableColumn>NAME</TableColumn>
        <TableColumn>TYPE</TableColumn>
        <TableColumn>SIZE</TableColumn>
        <TableColumn>CHUNKS</TableColumn>
        <TableColumn>STATUS</TableColumn>
        <TableColumn>ADDED</TableColumn>
        <TableColumn aria-label="Actions">ACTIONS</TableColumn>
      </TableHeader>
      <TableBody>
        {documents.map((doc) => (
          <TableRow key={doc.id}>
            <TableCell>
              <div className="flex items-center gap-2">
                {getDocumentIcon(doc.type)}
                <span className="font-medium">{doc.title}</span>
              </div>
            </TableCell>
            <TableCell>
              <span className="uppercase text-default-500">{doc.type}</span>
            </TableCell>
            <TableCell>{formatBytes(doc.size_bytes)}</TableCell>
            <TableCell>{doc.chunk_count}</TableCell>
            <TableCell>
              {doc.status === "syncing" && (
                <Chip
                  size="sm"
                  color="primary"
                  variant="flat"
                  startContent={<RefreshCw className="h-3 w-3 animate-spin" />}
                >
                  Syncing
                </Chip>
              )}
              {doc.status === "failed" && (
                <Chip
                  size="sm"
                  color="danger"
                  variant="flat"
                  startContent={<AlertCircle className="h-3 w-3" />}
                >
                  Failed
                </Chip>
              )}
              {doc.status === "completed" && (
                <Chip size="sm" color="success" variant="flat">
                  Ready
                </Chip>
              )}
              {doc.status === "idle" && (
                <Chip size="sm" color="default" variant="flat">
                  Pending
                </Chip>
              )}
            </TableCell>
            <TableCell>{new Date(doc.created_at).toLocaleDateString()}</TableCell>
            <TableCell>
              <Dropdown>
                <DropdownTrigger>
                  <Button isIconOnly size="sm" variant="light">
                    <MoreVertical className="h-4 w-4 text-default-400" />
                  </Button>
                </DropdownTrigger>
                <DropdownMenu aria-label="Document actions">
                  <DropdownItem key="reindex" startContent={<RefreshCw className="h-4 w-4" />}>
                    Reindex Document
                  </DropdownItem>
                  <DropdownItem
                    key="delete"
                    className="text-danger"
                    color="danger"
                    startContent={<Trash className="h-4 w-4" />}
                  >
                    Delete
                  </DropdownItem>
                </DropdownMenu>
              </Dropdown>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
