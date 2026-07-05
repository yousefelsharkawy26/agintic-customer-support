"use client";

import { useState, useEffect } from "react";
import { Input, Button } from "@heroui/react";
import { Search, Filter } from "lucide-react";
import type { ConversationRow } from "@/modules/conversations/types/conversation";
import { ConversationList } from "@/modules/conversations/components/conversation-list";

export default function ConversationsPage() {
  const [conversations, setConversations] = useState<ConversationRow[]>([]);
  const [search, setSearch] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetch("/api/conversations")
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setConversations(data as ConversationRow[]);
        }
      })
      .finally(() => setIsLoading(false));
  }, []);

  const filtered = conversations.filter(
    (c) =>
      c.customer_name?.toLowerCase().includes(search.toLowerCase()) ||
      c.customer_email?.toLowerCase().includes(search.toLowerCase())
  );

  if (isLoading) {
    return <div className="p-8 text-center text-default-500">Loading conversations...</div>;
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Conversations</h1>
          <p className="text-default-500">
            Monitor and intervene in active customer support sessions.
          </p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <Input
          placeholder="Search by name or email..."
          startContent={<Search className="h-4 w-4 text-default-400" />}
          value={search}
          onValueChange={setSearch}
          variant="bordered"
          className="max-w-xs"
        />
        <Button variant="flat" startContent={<Filter className="h-4 w-4" />}>
          Filter
        </Button>
      </div>

      <div className="rounded-xl border border-divider bg-card">
        <ConversationList conversations={filtered as ConversationRow[]} />
      </div>
    </div>
  );
}
