"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Bot,
  BookOpen,
  Wrench,
  MessageSquare,
  TerminalSquare,
  Users,
  Activity,
  ActivitySquare,
  Settings,
  CreditCard,
  Key,
} from "lucide-react";
import { clsx } from "clsx";

const navigation = [
  { name: "Overview", href: "/", icon: LayoutDashboard },
  { name: "Agents", href: "/agents", icon: Bot },
  { name: "Knowledge Base", href: "/knowledge-base", icon: BookOpen },
  { name: "Tools", href: "/tools", icon: Wrench },
  { name: "Conversations", href: "/conversations", icon: MessageSquare },
  { name: "Prompts", href: "/prompts", icon: TerminalSquare },
  { name: "Users", href: "/users", icon: Users },
  { name: "Analytics", href: "/analytics", icon: Activity },
  { name: "Monitoring", href: "/monitoring", icon: ActivitySquare },
  { name: "Settings", href: "/settings", icon: Settings },
  { name: "Billing", href: "/billing", icon: CreditCard },
  { name: "API Keys", href: "/api-keys", icon: Key },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex h-full w-64 flex-col border-r border-divider bg-content1 px-3 py-4">
      <div className="mb-8 px-3">
        <h1 className="text-xl font-bold tracking-tight text-foreground">IntegraServeAI</h1>
      </div>
      <nav className="flex-1 space-y-1 overflow-y-auto">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={clsx(
                "group flex items-center rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-default-600 hover:bg-default-100 hover:text-foreground"
              )}
            >
              <item.icon
                className={clsx(
                  "mr-3 h-5 w-5 flex-shrink-0",
                  isActive ? "text-primary" : "text-default-400 group-hover:text-foreground"
                )}
                aria-hidden="true"
              />
              {item.name}
            </Link>
          );
        })}
      </nav>
      <div className="mt-auto px-3 pb-4">
        <div className="rounded-lg bg-default-100 p-4">
          <p className="text-xs font-semibold text-default-600">Pro Plan</p>
          <p className="mt-1 text-xs text-default-500">2,401 / 5,000 queries</p>
          <div className="mt-2 h-1.5 w-full rounded-full bg-default-200">
            <div className="h-1.5 w-[48%] rounded-full bg-primary" />
          </div>
        </div>
      </div>
    </div>
  );
}
