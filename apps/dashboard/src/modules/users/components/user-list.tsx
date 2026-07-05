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
  Dropdown,
  DropdownTrigger,
  DropdownMenu,
  DropdownItem,
} from "@heroui/react";
import {
  MoreVertical,
  ShieldAlert,
  ShieldCheck,
  Mail,
  CheckCircle2,
  Clock,
  Ban,
} from "lucide-react";
import Link from "next/link";
import type { UserAccount } from "../types/user";
import { formatDistanceToNow } from "date-fns";

const getRoleChip = (role: UserAccount["role"]) => {
  switch (role) {
    case "admin":
      return (
        <Chip
          size="sm"
          color="danger"
          variant="flat"
          startContent={<ShieldAlert className="h-3 w-3" />}
        >
          Admin
        </Chip>
      );
    case "manager":
      return (
        <Chip
          size="sm"
          color="warning"
          variant="flat"
          startContent={<ShieldCheck className="h-3 w-3" />}
        >
          Manager
        </Chip>
      );
    case "support_agent":
      return (
        <Chip size="sm" color="primary" variant="flat">
          Support Agent
        </Chip>
      );
    default:
      return (
        <Chip size="sm" color="default" variant="flat">
          Viewer
        </Chip>
      );
  }
};

const getStatusDisplay = (status: UserAccount["status"]) => {
  switch (status) {
    case "active":
      return (
        <div className="flex items-center gap-1.5 text-success">
          <CheckCircle2 className="h-4 w-4" />
          <span className="text-sm font-medium">Active</span>
        </div>
      );
    case "invited":
      return (
        <div className="flex items-center gap-1.5 text-warning">
          <Mail className="h-4 w-4" />
          <span className="text-sm font-medium">Invited</span>
        </div>
      );
    case "suspended":
      return (
        <div className="flex items-center gap-1.5 text-danger">
          <Ban className="h-4 w-4" />
          <span className="text-sm font-medium">Suspended</span>
        </div>
      );
  }
};

export function UserList({ users }: { users: UserAccount[] }) {
  if (users.length === 0) {
    return (
      <div className="flex h-40 flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-default-200">
        <p className="text-default-500">No users found.</p>
      </div>
    );
  }

  return (
    <Table aria-label="Users directory">
      <TableHeader>
        <TableColumn>USER</TableColumn>
        <TableColumn>ROLE</TableColumn>
        <TableColumn>STATUS</TableColumn>
        <TableColumn>LAST LOGIN</TableColumn>
        <TableColumn aria-label="Actions" align="end">
          ACTIONS
        </TableColumn>
      </TableHeader>
      <TableBody>
        {users.map((user) => (
          <TableRow key={user.id}>
            <TableCell>
              <User
                name={user.name}
                description={user.email}
                avatarProps={{
                  name: user.name.charAt(0),
                }}
              />
            </TableCell>
            <TableCell>{getRoleChip(user.role)}</TableCell>
            <TableCell>{getStatusDisplay(user.status)}</TableCell>
            <TableCell>
              {user.last_login_at ? (
                <div className="flex items-center gap-1.5 text-sm text-default-500">
                  <Clock className="h-3 w-3" />
                  {formatDistanceToNow(new Date(user.last_login_at), { addSuffix: true })}
                </div>
              ) : (
                <span className="text-sm text-default-400">Never</span>
              )}
            </TableCell>
            <TableCell>
              <div className="flex items-center justify-end gap-2">
                <Button
                  as={Link}
                  href={`/users/${user.id}`}
                  size="sm"
                  variant="flat"
                  color="primary"
                >
                  Manage
                </Button>
                <Dropdown placement="bottom-end">
                  <DropdownTrigger>
                    <Button isIconOnly size="sm" variant="light">
                      <MoreVertical className="h-4 w-4 text-default-400" />
                    </Button>
                  </DropdownTrigger>
                  <DropdownMenu aria-label="User actions">
                    <DropdownItem key="reset">Reset Password</DropdownItem>
                    <DropdownItem key="roles">Change Role</DropdownItem>
                    <DropdownItem key="suspend" className="text-danger" color="danger">
                      {user.status === "suspended" ? "Unsuspend User" : "Suspend User"}
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
