"use client";

import { useState } from "react";
import { Button } from "@heroui/react";
import { Plus } from "lucide-react";
import { ApiKeyList } from "@/modules/api-keys/components/api-key-list";
import { CreateApiKeyModal } from "@/modules/api-keys/components/create-api-key-modal";
import { MOCK_API_KEYS } from "@/modules/api-keys/api/mock-data";
import type { ApiKey } from "@/modules/api-keys/types/api-key";

export default function ApiKeysPage() {
  const [apiKeys, setApiKeys] = useState<ApiKey[]>(MOCK_API_KEYS);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handleCreate = (data: { name: string }) => {
    const newKey: ApiKey = {
      id: `key_${Date.now()}`,
      name: data.name,
      key_hint: "sk_live_••••••••••••" + Math.random().toString(16).slice(-4),
      status: "active",
      created_at: new Date().toISOString(),
    };
    setApiKeys((prev) => [newKey, ...prev]);
  };

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">API Keys</h1>
          <p className="text-default-500">
            Manage your secret keys for accessing the workspace API externally.
          </p>
        </div>
        <Button
          color="primary"
          startContent={<Plus className="h-4 w-4" />}
          onPress={() => setIsModalOpen(true)}
        >
          Create new secret key
        </Button>
      </div>

      <div className="rounded-xl border border-divider bg-card">
        <ApiKeyList apiKeys={apiKeys} />
      </div>

      <div className="rounded-lg bg-warning-50 border border-warning/20 p-4 max-w-4xl mt-4">
        <h3 className="font-semibold text-warning-700 text-sm">Security Warning</h3>
        <p className="text-sm text-warning-700/80 mt-1">
          Do not share your API keys in publicly accessible areas such as GitHub, client-side code,
          and so forth. If you suspect a key has been compromised, revoke it immediately.
        </p>
      </div>

      <CreateApiKeyModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreate}
      />
    </div>
  );
}
