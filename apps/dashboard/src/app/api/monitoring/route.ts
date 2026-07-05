import { NextRequest, NextResponse } from "next/server";
import { monitoringService } from "@/lib/services/monitoring";
import { ApiError } from "@/lib/api-client";

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const type = searchParams.get("type");

    if (type === "alerts") {
      const data = await monitoringService.getAlertRules();
      return NextResponse.json(data);
    } else if (type === "events") {
      const limit = parseInt(searchParams.get("limit") || "50", 10);
      const data = await monitoringService.getAlertEvents(limit);
      return NextResponse.json(data);
    }

    return NextResponse.json(
      { error: "bad_request", message: "Invalid monitoring type" },
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
