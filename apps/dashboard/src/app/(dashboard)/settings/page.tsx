"use client";

import { useState } from "react";
import { Tabs, Tab } from "@heroui/react";
import { Settings as SettingsIcon, Bell, Palette } from "lucide-react";
import { GeneralSettings } from "@/modules/settings/components/general-settings";
import { AppearanceSettings } from "@/modules/settings/components/appearance-settings";
import { NotificationsSettings } from "@/modules/settings/components/notifications-settings";

export default function SettingsPage() {
  const [selectedTab, setSelectedTab] = useState("general");

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Workspace Settings</h1>
          <p className="text-default-500">
            Configure your organization details, appearance, and alerts.
          </p>
        </div>
      </div>

      <div className="flex flex-col gap-6">
        <Tabs
          selectedKey={selectedTab}
          onSelectionChange={(k) => setSelectedTab(k as string)}
          variant="underlined"
          color="primary"
          classNames={{
            tabList: "gap-6 w-full relative rounded-none p-0 border-b border-divider",
            cursor: "w-full",
            tab: "max-w-fit px-0 h-12",
            tabContent: "group-data-[selected=true]:font-semibold",
          }}
        >
          <Tab
            key="general"
            title={
              <div className="flex items-center gap-2">
                <SettingsIcon className="h-4 w-4" />
                <span>General</span>
              </div>
            }
          />
          <Tab
            key="appearance"
            title={
              <div className="flex items-center gap-2">
                <Palette className="h-4 w-4" />
                <span>Appearance</span>
              </div>
            }
          />
          <Tab
            key="notifications"
            title={
              <div className="flex items-center gap-2">
                <Bell className="h-4 w-4" />
                <span>Notifications</span>
              </div>
            }
          />
        </Tabs>

        <div className="max-w-4xl pt-4">
          {selectedTab === "general" && <GeneralSettings />}
          {selectedTab === "appearance" && <AppearanceSettings />}
          {selectedTab === "notifications" && <NotificationsSettings />}
        </div>
      </div>
    </div>
  );
}
