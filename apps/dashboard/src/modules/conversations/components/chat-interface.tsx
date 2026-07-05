"use client";

import { Avatar } from "@heroui/react";
import { Bot, User, Wrench } from "lucide-react";
import type { ConversationMessage } from "../types/conversation";
import { clsx } from "clsx";

export function ChatInterface({ messages }: { messages: ConversationMessage[] }) {
  return (
    <div className="flex flex-col gap-4 p-4">
      {messages.map((msg) => {
        const isUser = msg.role === "user";
        const isSystem = msg.role === "system";

        if (isSystem) {
          return (
            <div key={msg.id} className="flex justify-center my-2">
              <div className="flex items-center gap-2 rounded-full bg-default-100 px-3 py-1 text-xs text-default-500">
                <Wrench className="h-3 w-3" />
                {msg.content}
              </div>
            </div>
          );
        }

        return (
          <div
            key={msg.id}
            className={clsx("flex w-full gap-3", isUser ? "flex-row-reverse" : "flex-row")}
          >
            <Avatar
              icon={isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
              classNames={{
                base: isUser ? "bg-primary text-white" : "bg-secondary text-white",
              }}
              size="sm"
            />
            <div
              className={clsx(
                "flex max-w-[75%] flex-col gap-1 rounded-2xl px-4 py-3 text-sm",
                isUser
                  ? "bg-primary text-white rounded-tr-sm"
                  : "bg-default-100 text-foreground rounded-tl-sm"
              )}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
              <span
                className={clsx(
                  "text-[10px] mt-1",
                  isUser ? "text-primary-100 text-right" : "text-default-400"
                )}
              >
                {new Date(msg.created_at).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
