"use client";

import { useState, useEffect } from "react";
import { Card, CardBody, CardHeader, Divider, Input, Button } from "@heroui/react";
import { Save } from "lucide-react";

type Config = Record<string, string> | null;

export function GeneralSettings() {
  const [config, setConfig] = useState<Config>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    fetch("/api/settings?type=config")
      .then((res) => res.json())
      .then((data) => {
        if (!data.error) {
          setConfig(data as Config);
        }
      })
      .finally(() => setIsLoading(false));
  }, []);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      await fetch("/api/settings?type=config", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      });
    } catch (e) {
      console.error(e);
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return <div className="p-8 text-center text-default-500">Loading settings...</div>;
  }

  return (
    <div className="flex flex-col gap-6">
      <Card shadow="sm">
        <CardHeader className="px-6 pt-5 pb-4">
          <h2 className="text-base font-semibold">Workspace Information</h2>
        </CardHeader>
        <Divider />
        <CardBody className="gap-6 p-6">
          <div className="flex flex-col gap-4 max-w-lg">
            <Input
              label="Workspace Name"
              value={config?.company_name ?? "IntegraServeAI"}
              onValueChange={(value) => setConfig({ ...(config ?? {}), company_name: value })}
              variant="bordered"
              description="This is your organization's public name."
            />
            <Input
              label="Support Email"
              value={config?.support_email ?? "support@integraserve.ai"}
              onValueChange={(value) => setConfig({ ...(config ?? {}), support_email: value })}
              variant="bordered"
              description="The default email address for customer communications."
            />
            <Input
              label="Website URL"
              value={config?.website_url ?? "https://integraserve.ai"}
              onValueChange={(value) => setConfig({ ...(config ?? {}), website_url: value })}
              variant="bordered"
            />
          </div>
          <div className="flex justify-end mt-2 max-w-lg">
            <Button
              color="primary"
              startContent={<Save className="h-4 w-4" />}
              isLoading={isSaving}
              onPress={handleSave}
            >
              Save Changes
            </Button>
          </div>
        </CardBody>
      </Card>

      <Card shadow="sm" className="border-danger/20 bg-danger-50 dark:bg-danger-50/5">
        <CardHeader className="px-6 pt-5 pb-4">
          <h2 className="text-base font-semibold text-danger">Danger Zone</h2>
        </CardHeader>
        <Divider />
        <CardBody className="p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-sm">Delete Workspace</p>
              <p className="text-xs text-default-500 mt-1">
                Permanently delete this workspace, all agents, and customer data. This action cannot
                be undone.
              </p>
            </div>
            <Button color="danger" variant="flat">
              Delete Workspace
            </Button>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
