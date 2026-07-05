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
} from "@heroui/react";
import { Info, AlertTriangle, XCircle, AlertOctagon, Terminal } from "lucide-react";
import type { SystemLog } from "../types/log";

const getLevelChip = (level: SystemLog["level"]) => {
  switch (level) {
    case "info":
      return (
        <Chip size="sm" color="default" variant="flat" startContent={<Info className="h-3 w-3" />}>
          INFO
        </Chip>
      );
    case "warning":
      return (
        <Chip
          size="sm"
          color="warning"
          variant="flat"
          startContent={<AlertTriangle className="h-3 w-3" />}
        >
          WARN
        </Chip>
      );
    case "error":
      return (
        <Chip
          size="sm"
          color="danger"
          variant="flat"
          startContent={<XCircle className="h-3 w-3" />}
        >
          ERROR
        </Chip>
      );
    case "critical":
      return (
        <Chip
          size="sm"
          color="danger"
          variant="solid"
          startContent={<AlertOctagon className="h-3 w-3" />}
        >
          CRITICAL
        </Chip>
      );
  }
};

const getSourceDisplay = (source: SystemLog["source"]) => {
  return (
    <div className="flex items-center gap-1.5 text-xs font-mono text-default-500">
      <Terminal className="h-3 w-3" />
      {source}
    </div>
  );
};

export function LogTable({ logs }: { logs: SystemLog[] }) {
  if (logs.length === 0) {
    return (
      <div className="flex h-40 flex-col items-center justify-center gap-2 rounded-lg border border-dashed border-default-200">
        <p className="text-default-500">No logs found for the selected filter.</p>
      </div>
    );
  }

  return (
    <Table
      aria-label="System Logs"
      isHeaderSticky
      classNames={{ base: "max-h-[600px] overflow-scroll" }}
    >
      <TableHeader>
        <TableColumn>TIMESTAMP</TableColumn>
        <TableColumn>LEVEL</TableColumn>
        <TableColumn>SOURCE</TableColumn>
        <TableColumn>MESSAGE</TableColumn>
        <TableColumn>LATENCY</TableColumn>
        <TableColumn aria-label="Actions">ACTIONS</TableColumn>
      </TableHeader>
      <TableBody>
        {logs.map((log) => (
          <TableRow key={log.id}>
            <TableCell>
              <span className="text-xs text-default-500 whitespace-nowrap">
                {new Date(log.timestamp).toLocaleTimeString([], {
                  hour12: false,
                  hour: "2-digit",
                  minute: "2-digit",
                  second: "2-digit",
                })}
              </span>
            </TableCell>
            <TableCell>{getLevelChip(log.level)}</TableCell>
            <TableCell>{getSourceDisplay(log.source)}</TableCell>
            <TableCell>
              <span className="text-sm font-medium">{log.message}</span>
            </TableCell>
            <TableCell>
              {log.latency_ms ? (
                <span className="text-xs text-default-500">{log.latency_ms}ms</span>
              ) : (
                <span className="text-xs text-default-300">-</span>
              )}
            </TableCell>
            <TableCell>
              <Button size="sm" variant="light" color="primary">
                Details
              </Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
