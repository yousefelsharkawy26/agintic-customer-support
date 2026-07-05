"use client";

import { Card, CardBody, CardHeader, Divider, RadioGroup, Radio, Button } from "@heroui/react";
import { Save } from "lucide-react";

export function AppearanceSettings() {
  return (
    <Card shadow="sm">
      <CardHeader className="px-6 pt-5 pb-4">
        <h2 className="text-base font-semibold">Appearance</h2>
      </CardHeader>
      <Divider />
      <CardBody className="gap-6 p-6">
        <div className="flex flex-col gap-6 max-w-lg">
          <RadioGroup
            label="Dashboard Theme"
            defaultValue="system"
            description="Select how the dashboard should look for you."
          >
            <Radio value="light">Light</Radio>
            <Radio value="dark">Dark</Radio>
            <Radio value="system">System Default</Radio>
          </RadioGroup>

          <Divider />

          <RadioGroup
            label="Chat Widget Placement"
            defaultValue="bottom_right"
            description="Where the chat widget appears on your customer-facing website."
          >
            <Radio value="bottom_right">Bottom Right</Radio>
            <Radio value="bottom_left">Bottom Left</Radio>
          </RadioGroup>
        </div>

        <div className="flex justify-end mt-4 max-w-lg">
          <Button color="primary" startContent={<Save className="h-4 w-4" />}>
            Save Appearance
          </Button>
        </div>
      </CardBody>
    </Card>
  );
}
