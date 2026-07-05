import { NextRequest, NextResponse } from "next/server";
import { promptsService } from "@/lib/services/prompts";
import { ApiError } from "@/lib/api-client";

export async function POST(request: NextRequest, { params }: { params: { name: string } }) {
  try {
    const { searchParams } = new URL(request.url);
    const version = parseInt(searchParams.get("version") || "0", 10);

    if (!version) {
      return NextResponse.json(
        { error: "bad_request", message: "Version is required" },
        { status: 400 }
      );
    }

    const data = await promptsService.rollbackPrompt(params.name, version);
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
