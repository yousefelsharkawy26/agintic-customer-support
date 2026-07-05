"use client";

import { use } from "react";
import Link from "next/link";
import {
  Button,
  Card,
  CardBody,
  CardHeader,
  Divider,
  Input,
  Select,
  SelectItem,
  User as UserComponent,
  Chip,
} from "@heroui/react";
import { ArrowLeft, Save, Activity } from "lucide-react";
import { MOCK_USERS } from "@/modules/users/api/mock-data";

export default function UserDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const user = MOCK_USERS.find((u) => u.id === id);

  if (!user) {
    return (
      <div className="flex min-h-[400px] flex-col items-center justify-center gap-4">
        <p className="text-default-500">User not found.</p>
        <Button as={Link} href="/users" variant="flat">
          Back to Users
        </Button>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-4">
        <Button as={Link} href="/users" isIconOnly variant="flat" aria-label="Back to users">
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div className="flex flex-1 items-center gap-4">
          <UserComponent
            name={user.name}
            description={user.email}
            avatarProps={{ name: user.name.charAt(0), size: "md" }}
          />
          <Chip
            size="sm"
            variant="flat"
            color={
              user.status === "active"
                ? "success"
                : user.status === "suspended"
                  ? "danger"
                  : "warning"
            }
          >
            {user.status}
          </Chip>
        </div>
        <Button color="primary" startContent={<Save className="h-4 w-4" />}>
          Save Changes
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="flex flex-col gap-4 lg:col-span-2">
          <Card shadow="sm">
            <CardHeader className="px-6 pt-5 pb-4">
              <h2 className="text-base font-semibold">Account Details</h2>
            </CardHeader>
            <Divider />
            <CardBody className="gap-6 p-6">
              <div className="grid grid-cols-2 gap-4">
                <Input label="Full Name" defaultValue={user.name} variant="bordered" />
                <Input
                  label="Email Address"
                  defaultValue={user.email}
                  variant="bordered"
                  isReadOnly
                />
              </div>
              <Select
                label="Role"
                variant="bordered"
                defaultSelectedKeys={[user.role]}
                description="This determines the user's access level."
              >
                <SelectItem key="admin" value="admin">
                  Administrator
                </SelectItem>
                <SelectItem key="manager" value="manager">
                  Manager
                </SelectItem>
                <SelectItem key="support_agent" value="support_agent">
                  Support Agent
                </SelectItem>
                <SelectItem key="viewer" value="viewer">
                  Viewer
                </SelectItem>
              </Select>
            </CardBody>
          </Card>

          <Card shadow="sm">
            <CardHeader className="px-6 pt-5 pb-4 flex justify-between items-center">
              <h2 className="text-base font-semibold">Recent Activity</h2>
              <Button size="sm" variant="light" startContent={<Activity className="h-4 w-4" />}>
                View Logs
              </Button>
            </CardHeader>
            <Divider />
            <CardBody className="p-0">
              <div className="flex flex-col divide-y divide-divider">
                <div className="p-4 flex items-center justify-between text-sm">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-default-100 rounded-lg">
                      <Activity className="h-4 w-4" />
                    </div>
                    <span>Logged in via SSO</span>
                  </div>
                  <span className="text-default-400">2 hours ago</span>
                </div>
                <div className="p-4 flex items-center justify-between text-sm">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-default-100 rounded-lg">
                      <Activity className="h-4 w-4" />
                    </div>
                    <span>Resolved Conversation #1042</span>
                  </div>
                  <span className="text-default-400">1 day ago</span>
                </div>
              </div>
            </CardBody>
          </Card>
        </div>

        <div className="flex flex-col gap-4">
          <Card shadow="sm">
            <CardHeader className="px-5 pt-5 pb-2">
              <h2 className="text-base font-semibold">Information</h2>
            </CardHeader>
            <Divider />
            <CardBody className="p-5 flex flex-col gap-4 text-sm">
              <div className="flex items-center justify-between">
                <span className="text-default-500">Joined</span>
                <span>{new Date(user.created_at).toLocaleDateString()}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-default-500">Last Login</span>
                <span>
                  {user.last_login_at ? new Date(user.last_login_at).toLocaleDateString() : "Never"}
                </span>
              </div>
            </CardBody>
          </Card>

          <Card shadow="sm" className="bg-danger-50 dark:bg-danger-50/5 border-danger/20">
            <CardHeader className="px-5 pt-5 pb-2">
              <h2 className="text-base font-semibold text-danger">Danger Zone</h2>
            </CardHeader>
            <Divider />
            <CardBody className="p-5 flex flex-col gap-3">
              <Button color="danger" variant="flat" className="w-full justify-start">
                Reset Password
              </Button>
              <Button color="danger" variant="flat" className="w-full justify-start">
                {user.status === "suspended" ? "Unsuspend User" : "Suspend Account"}
              </Button>
            </CardBody>
          </Card>
        </div>
      </div>
    </div>
  );
}
