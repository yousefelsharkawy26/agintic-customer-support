import { NextRequest, NextResponse } from "next/server";
import { tenantService } from "@/lib/services/tenants";
import { ApiError } from "@/lib/api-client";

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const type = searchParams.get("type");

    if (type === "config") {
      const data = await tenantService.getConfig();
      return NextResponse.json(data);
    } else if (type === "quota") {
      const data = await tenantService.getQuota();
      return NextResponse.json(data);
    }

    return NextResponse.json(
      { error: "bad_request", message: "Invalid settings type" },
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

export async function PUT(request: NextRequest) {
  try {
    const body = await request.json();
    const data = await tenantService.updateConfig(body);
    return NextResponse.json(data);
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
