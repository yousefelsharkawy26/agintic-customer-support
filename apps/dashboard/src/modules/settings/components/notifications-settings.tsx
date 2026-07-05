"use client";

import { Card, CardBody, CardHeader, Divider, Switch, Button } from "@heroui/react";
import { Save } from "lucide-react";

export function NotificationsSettings() {
  return (
    <Card shadow="sm">
      <CardHeader className="px-6 pt-5 pb-4">
        <h2 className="text-base font-semibold">Notifications</h2>
      </CardHeader>
      <Divider />
      <CardBody className="gap-6 p-6">
        <div className="flex flex-col gap-6 max-w-2xl">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-sm">Human Escalations</p>
              <p className="text-xs text-default-500">
                Receive an email when a bot cannot answer a question and escalates to a human.
              </p>
            </div>
            <Switch defaultSelected color="primary" />
          </div>
          <Divider />
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-sm">System Outages</p>
              <p className="text-xs text-default-500">
                Receive alerts when vector DB or LLM APIs experience downtime.
              </p>
            </div>
            <Switch defaultSelected color="primary" />
          </div>
          <Divider />
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-sm">Weekly Report</p>
              <p className="text-xs text-default-500">
                Receive a weekly summary of agent resolution rates and analytics.
              </p>
            </div>
            <Switch color="primary" />
          </div>
        </div>

        <div className="flex mt-6 max-w-2xl justify-end">
          <Button color="primary" startContent={<Save className="h-4 w-4" />}>
            Save Preferences
          </Button>
        </div>
      </CardBody>
    </Card>
  );
}
