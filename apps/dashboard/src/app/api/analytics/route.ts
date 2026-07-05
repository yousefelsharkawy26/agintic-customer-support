import { NextRequest, NextResponse } from "next/server";
import { monitoringService } from "@/lib/services/monitoring";
import { ApiError } from "@/lib/api-client";

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const type = searchParams.get("type");

    if (type === "summary") {
      const data = await monitoringService.getCostSummary();
      return NextResponse.json(data);
    } else if (type === "costs") {
      const startDate = searchParams.get("start_date") || undefined;
      const endDate = searchParams.get("end_date") || undefined;
      const data = await monitoringService.getCosts(startDate, endDate);
      return NextResponse.json(data);
    }

    return NextResponse.json(
      { error: "bad_request", message: "Invalid analytics type" },
      { status: 400 }
    );
  } catch (error) {
    if (error instanceof ApiError) {
      return NextResponse.json(
        { error: error.code, message: error.message },
        { status: error.status }
      );
    }
    return NextResponse.json(
      { error: "internal_error", message: "Internal Server Error" },
      { status: 500 }
    );
  }
}
