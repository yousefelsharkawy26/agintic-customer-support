"use client";

import { useState } from "react";
import { Button, Input } from "@heroui/react";
import { UserPlus, Search } from "lucide-react";
import { UserList } from "@/modules/users/components/user-list";
import { CreateUserModal } from "@/modules/users/components/create-user-modal";
import { MOCK_USERS } from "@/modules/users/api/mock-data";
import type { UserAccount, UserRole } from "@/modules/users/types/user";

export default function UsersPage() {
  const [users, setUsers] = useState<UserAccount[]>(MOCK_USERS);
  const [search, setSearch] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);

  const filtered = users.filter(
    (u) =>
      u.name.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase())
  );

  const handleCreate = (data: { name: string; email: string; role: string }) => {
    const newUser: UserAccount = {
      id: `usr_${Date.now()}`,
      name: data.name,
      email: data.email,
      role: data.role as UserRole,
      status: "invited",
      created_at: new Date().toISOString(),
    };
    setUsers((prev) => [newUser, ...prev]);
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Users & Roles</h1>
          <p className="text-default-500">Manage your team members and their access permissions.</p>
        </div>
        <Button
          color="primary"
          startContent={<UserPlus className="h-4 w-4" />}
          onPress={() => setIsModalOpen(true)}
        >
          Invite User
        </Button>
      </div>

      <div className="flex items-center gap-3">
        <Input
          placeholder="Search users..."
          startContent={<Search className="h-4 w-4 text-default-400" />}
          value={search}
          onValueChange={setSearch}
          variant="bordered"
          className="max-w-xs"
        />
        <span className="text-sm text-default-400">
          {filtered.length} user{filtered.length !== 1 ? "s" : ""}
        </span>
      </div>

      <div className="rounded-xl border border-divider bg-card">
        <UserList users={filtered} />
      </div>

      <CreateUserModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreate}
      />
    </div>
  );
}
