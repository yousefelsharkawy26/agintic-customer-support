import { NextRequest, NextResponse } from "next/server";
import { promptsService } from "@/lib/services/prompts";
import { ApiError } from "@/lib/api-client";

export async function GET(request: NextRequest, { params }: { params: { name: string } }) {
  try {
    const data = await promptsService.getPrompt(params.name);
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
