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
import { Download, CheckCircle2, Clock, AlertCircle } from "lucide-react";
import type { Invoice } from "../types/billing";

export function InvoiceTable({ invoices }: { invoices: Invoice[] }) {
  const getStatusChip = (status: Invoice["status"]) => {
    switch (status) {
      case "paid":
        return (
          <Chip
            size="sm"
            color="success"
            variant="flat"
            startContent={<CheckCircle2 className="h-3 w-3" />}
          >
            Paid
          </Chip>
        );
      case "pending":
        return (
          <Chip
            size="sm"
            color="warning"
            variant="flat"
            startContent={<Clock className="h-3 w-3" />}
          >
            Pending
          </Chip>
        );
      case "failed":
        return (
          <Chip
            size="sm"
            color="danger"
            variant="flat"
            startContent={<AlertCircle className="h-3 w-3" />}
          >
            Failed
          </Chip>
        );
    }
  };

  return (
    <Table aria-label="Invoice History">
      <TableHeader>
        <TableColumn>INVOICE ID</TableColumn>
        <TableColumn>DATE</TableColumn>
        <TableColumn>AMOUNT</TableColumn>
        <TableColumn>STATUS</TableColumn>
        <TableColumn aria-label="Download" align="end">
          RECEIPT
        </TableColumn>
      </TableHeader>
      <TableBody>
        {invoices.map((invoice) => (
          <TableRow key={invoice.id}>
            <TableCell>
              <span className="font-mono text-xs">{invoice.id}</span>
            </TableCell>
            <TableCell>
              <span className="text-sm text-default-500">
                {new Date(invoice.date).toLocaleDateString()}
              </span>
            </TableCell>
            <TableCell>
              <span className="font-medium">${invoice.amount.toFixed(2)}</span>
            </TableCell>
            <TableCell>{getStatusChip(invoice.status)}</TableCell>
            <TableCell>
              <div className="flex justify-end">
                <Button size="sm" variant="light" isIconOnly aria-label="Download receipt">
                  <Download className="h-4 w-4 text-default-500" />
                </Button>
              </div>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
}
