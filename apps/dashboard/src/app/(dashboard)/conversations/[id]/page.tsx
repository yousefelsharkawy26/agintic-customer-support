"use client";

import { use, useState, useEffect } from "react";
import Link from "next/link";
import { Button, Card, CardBody, CardHeader, Divider, User, Chip } from "@heroui/react";
import { ArrowLeft, Send, Hand, PhoneCall } from "lucide-react";
import { ChatInterface } from "@/modules/conversations/components/chat-interface";
import type {
  ConversationMessage,
  ConversationRow,
} from "@/modules/conversations/types/conversation";

interface ConversationRecord extends Omit<
  ConversationRow,
  "messages_count" | "last_message_at" | "created_at"
> {
  messages?: ConversationMessage[];
  last_message_at?: string;
  created_at?: string;
}

export default function ConversationDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [conversation, setConversation] = useState<ConversationRecord | null>(null);
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/conversations/${id}`)
      .then((res) => res.json())
      .then((data) => {
        if (!data.error) {
          setConversation(data as ConversationRecord);
          setMessages(Array.isArray(data.messages) ? data.messages : []);
        }
      })
      .finally(() => setIsLoading(false));
  }, [id]);

  if (isLoading) {
    return <div className="p-8 text-center text-default-500">Loading conversation...</div>;
  }

  if (!conversation) {
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center gap-4">
        <p className="text-default-500">Conversation not found.</p>
        <Button as={Link} href="/conversations" variant="flat">
          Back to Conversations
        </Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] gap-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            as={Link}
            href="/conversations"
            isIconOnly
            variant="flat"
            aria-label="Back to conversations"
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div className="flex items-center gap-3">
            <h1 className="text-xl font-bold">
              Conversation #{conversation.conversation_id.replace("conv_", "")}
            </h1>
            <Chip
              size="sm"
              variant="flat"
              color={conversation.status === "resolved" ? "success" : "primary"}
            >
              {conversation.status}
            </Chip>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="flat" color="warning" startContent={<Hand className="h-4 w-4" />}>
            Take Over
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-4 min-h-0 flex-1">
        {/* Main Chat Area */}
        <Card shadow="sm" className="lg:col-span-3 flex flex-col min-h-0">
          <div className="flex-1 overflow-y-auto">
            {messages.length > 0 ? (
              <ChatInterface messages={messages} />
            ) : (
              <div className="flex h-full items-center justify-center text-default-500">
                No messages yet.
              </div>
            )}
          </div>
          <Divider />
          <div className="p-4 bg-default-50 flex items-center gap-2">
            <div className="flex-1 rounded-xl border border-divider bg-content1 px-4 py-2 text-sm text-default-400">
              Only agents or humans who have taken over can reply here...
            </div>
            <Button isIconOnly color="primary" isDisabled>
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </Card>

        {/* Sidebar */}
        <div className="flex flex-col gap-4 overflow-y-auto">
          <Card shadow="sm">
            <CardHeader className="px-5 pt-5 pb-2">
              <h2 className="text-base font-semibold">Customer Details</h2>
            </CardHeader>
            <Divider />
            <CardBody className="p-5 flex flex-col gap-4">
              <User
                name={conversation.customer_name || "Unknown"}
                description={conversation.customer_email || "No email"}
                avatarProps={{ name: (conversation.customer_name || "?").charAt(0) }}
                className="justify-start"
              />
              <Button
                variant="bordered"
                startContent={<PhoneCall className="h-4 w-4" />}
                className="w-full"
              >
                Call Customer
              </Button>
            </CardBody>
          </Card>

          <Card shadow="sm">
            <CardHeader className="px-5 pt-5 pb-2">
              <h2 className="text-base font-semibold">Session Info</h2>
            </CardHeader>
            <Divider />
            <CardBody className="p-5 flex flex-col gap-3 text-sm">
              <div className="flex justify-between">
                <span className="text-default-500">Started</span>
                <span>
                  {messages.length
                    ? new Date(messages[0].created_at).toLocaleTimeString([], {
                        hour: "2-digit",
                        minute: "2-digit",
                      })
                    : "N/A"}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-default-500">Messages</span>
                <span>{messages.length}</span>
              </div>
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  );
}
