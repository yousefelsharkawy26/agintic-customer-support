"use client";

import { useState, useEffect } from "react";
import { Button, Input, Select, SelectItem } from "@heroui/react";
import { Search, Download, RefreshCw } from "lucide-react";
import { LogTable } from "@/modules/monitoring/components/log-table";
import { SystemStatusOverview } from "@/modules/monitoring/components/system-status";
import { MOCK_SYSTEM_STATUS } from "@/modules/monitoring/api/mock-data";
import type { SystemLog } from "@/modules/monitoring/types/log";

export default function MonitoringPage() {
  const [search, setSearch] = useState("");
  const [levelFilter, setLevelFilter] = useState("all");
  const [logs, setLogs] = useState<SystemLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchLogs = () => {
    setIsLoading(true);
    fetch("/api/monitoring?type=events")
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setLogs(data);
        }
      })
      .finally(() => setIsLoading(false));
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const filteredLogs = logs.filter((log) => {
    const matchesSearch =
      log.message.toLowerCase().includes(search.toLowerCase()) ||
      log.source.toLowerCase().includes(search.toLowerCase());
    const matchesLevel = levelFilter === "all" || log.level === levelFilter;
    return matchesSearch && matchesLevel;
  });

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Monitoring & Logs</h1>
          <p className="text-default-500">
            Real-time observability into your AI agents and system health.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="flat" startContent={<Download className="h-4 w-4" />}>
            Export
          </Button>
          <Button
            color="primary"
            startContent={<RefreshCw className="h-4 w-4" />}
            onPress={fetchLogs}
            isLoading={isLoading}
          >
            Refresh
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 flex flex-col gap-4">
          <div className="flex items-center gap-3">
            <Input
              placeholder="Search logs..."
              startContent={<Search className="h-4 w-4 text-default-400" />}
              value={search}
              onValueChange={setSearch}
              variant="bordered"
              className="max-w-md"
            />
            <Select
              variant="bordered"
              className="max-w-[150px]"
              selectedKeys={[levelFilter]}
              onSelectionChange={(k) => setLevelFilter(Array.from(k)[0] as string)}
            >
              <SelectItem key="all" value="all">
                All Levels
              </SelectItem>
              <SelectItem key="info" value="info">
                Info
              </SelectItem>
              <SelectItem key="warning" value="warning">
                Warning
              </SelectItem>
              <SelectItem key="error" value="error">
                Error
              </SelectItem>
              <SelectItem key="critical" value="critical">
                Critical
              </SelectItem>
            </Select>
          </div>

          <div className="rounded-xl border border-divider bg-card">
            <LogTable logs={filteredLogs} />
          </div>
        </div>

        <div className="flex flex-col gap-4">
          <SystemStatusOverview statuses={MOCK_SYSTEM_STATUS} />
        </div>
      </div>
    </div>
  );
}
