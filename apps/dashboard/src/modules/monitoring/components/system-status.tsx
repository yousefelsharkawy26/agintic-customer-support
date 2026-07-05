"use client";

import { Card, CardBody, CardHeader, Divider } from "@heroui/react";
import { CheckCircle2, AlertTriangle, XCircle, Activity } from "lucide-react";
import type { SystemStatus } from "../types/log";

export function SystemStatusOverview({ statuses }: { statuses: SystemStatus[] }) {
  const getStatusIcon = (status: SystemStatus["status"]) => {
    switch (status) {
      case "operational":
        return <CheckCircle2 className="h-5 w-5 text-success" />;
      case "degraded":
        return <AlertTriangle className="h-5 w-5 text-warning" />;
      case "down":
        return <XCircle className="h-5 w-5 text-danger" />;
    }
  };

  const getStatusText = (status: SystemStatus["status"]) => {
    switch (status) {
      case "operational":
        return <span className="text-success font-medium">Operational</span>;
      case "degraded":
        return <span className="text-warning font-medium">Degraded Performance</span>;
      case "down":
        return <span className="text-danger font-medium">Major Outage</span>;
    }
  };

  return (
    <Card shadow="sm">
      <CardHeader className="px-6 pt-5 pb-4 flex justify-between items-center">
        <h2 className="text-base font-semibold">System Status</h2>
        <Activity className="h-4 w-4 text-default-400" />
      </CardHeader>
      <Divider />
      <CardBody className="p-0">
        <div className="flex flex-col divide-y divide-divider">
          {statuses.map((sys, idx) => (
            <div key={idx} className="p-4 flex items-center justify-between">
              <div>
                <p className="font-medium text-sm">{sys.service}</p>
                <p className="text-xs text-default-500 mt-1">Uptime: {sys.uptime}</p>
              </div>
              <div className="flex items-center gap-2">
                {getStatusIcon(sys.status)}
                {getStatusText(sys.status)}
              </div>
            </div>
          ))}
        </div>
      </CardBody>
    </Card>
  );
}
