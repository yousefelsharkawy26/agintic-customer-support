"use client";

import { useTheme } from "next-themes";
import {
  Dropdown,
  DropdownTrigger,
  DropdownMenu,
  DropdownItem,
  Avatar,
  Button,
} from "@heroui/react";
import { Sun, Moon, Bell } from "lucide-react";
import { logout } from "@/modules/auth/actions/login";

export function Topbar() {
  const { theme, setTheme } = useTheme();

  return (
    <header className="sticky top-0 z-10 flex h-16 flex-shrink-0 items-center justify-between border-b border-divider bg-background px-6">
      <div className="flex items-center gap-4">{/* Breadcrumbs or Title could go here */}</div>

      <div className="flex items-center gap-4">
        <Button isIconOnly variant="light" aria-label="Notifications">
          <Bell className="h-5 w-5 text-default-500" />
        </Button>

        <Button
          isIconOnly
          variant="light"
          aria-label="Toggle theme"
          onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
        >
          {theme === "dark" ? (
            <Sun className="h-5 w-5 text-default-500" />
          ) : (
            <Moon className="h-5 w-5 text-default-500" />
          )}
        </Button>

        <Dropdown placement="bottom-end">
          <DropdownTrigger>
            <Avatar
              as="button"
              className="transition-transform"
              src="https://i.pravatar.cc/150?u=admin"
              size="sm"
            />
          </DropdownTrigger>
          <DropdownMenu aria-label="User Actions" variant="flat">
            <DropdownItem key="profile" className="h-14 gap-2">
              <p className="font-semibold">Signed in as</p>
              <p className="font-semibold text-default-500">admin@example.com</p>
            </DropdownItem>
            <DropdownItem key="settings" href="/settings">
              My Settings
            </DropdownItem>
            <DropdownItem key="help_and_feedback">Help & Feedback</DropdownItem>
            <DropdownItem key="logout" color="danger" onPress={() => logout()}>
              Log Out
            </DropdownItem>
          </DropdownMenu>
        </Dropdown>
      </div>
    </header>
  );
}
