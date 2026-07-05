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
  User,
} from "@heroui/react";
import { ArrowRight, AlertTriangle, Bot, CheckCircle2 } from "lucide-react";
import Link from "next/link";
import type {
  ConversationRow,
  ConversationStatus,
} from "@/modules/conversations/types/conversation";
import { formatDistanceToNow } from "date-fns";

const getStatusChip = (status: ConversationStatus) => {
  switch (status) {
    case "bot_handling":
      return (
        <Chip size="sm" color="primary" variant="flat" startContent={<Bot className="h-3 w-3" />}>
          Bot Handling
        </Chip>
      );
    case "human_escalated":
      return (
        <Chip
          size="sm"
          color="warning"
          variant="flat"
          startContent={<AlertTriangle className="h-3 w-3" />}
        >
          Escalated
        </Chip>
      );
    case "resolved":
      return (
        <Chip
          size="sm"
          color="success"
          variant="flat"
          startContent={<CheckCircle2 className="h-3 w-3" />}
        >
          Resolved
        </Chip>
      );
    default:
      return (
        <Chip size="sm" color="default" variant="flat">
          {status}
        </Chip>
      );
  }
};

export function ConversationList({ conversations }: { conversations: ConversationRow[] }) {
  if (conversations.length === 0) {
    return (
      <div className="flex h-40 flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-default-200">
        <p className="text-default-500">No conversations found.</p>
      </div>
    );
  }

  return (
    <Table aria-label="Recent Conversations">
      <TableHeader>
        <TableColumn>CUSTOMER</TableColumn>
        <TableColumn>STATUS</TableColumn>
        <TableColumn>LAST MESSAGE</TableColumn>
        <TableColumn>TIME</TableColumn>
        <TableColumn aria-label="Actions">ACTIONS</TableColumn>
      </TableHeader>
      <TableBody>
        {conversations.map((conv) => (
          <TableRow key={conv.conversation_id}>
            <TableCell>
              <User
                name={conv.customer_name}
                description={conv.customer_email}
                avatarProps={{
                  size: "sm",
                  name: conv.customer_name.charAt(0),
                }}
              />
            </TableCell>
            <TableCell>{getStatusChip(conv.status)}</TableCell>
            <TableCell>
              <div className="max-w-[300px] truncate text-sm text-default-500">
                {conv.last_message_preview}
              </div>
            </TableCell>
            <TableCell>
              <span className="text-sm text-default-500 whitespace-nowrap">
                {formatDistanceToNow(new Date(conv.last_message_at), { addSuffix: true })}
              </span>
            </TableCell>
            <TableCell>
              <Button
                as={Link}
                href={`/conversations/${conv.conversation_id}`}
                size="sm"
                variant="flat"
                color="default"
                endContent={<ArrowRight className="h-4 w-4" />}
              >
                View
              </Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
