import { NextRequest, NextResponse } from "next/server";
import { ragService } from "@/lib/services/rag";
import { ApiError } from "@/lib/api-client";

export async function DELETE(request: NextRequest, { params }: { params: { id: string } }) {
  try {
    const data = await ragService.deleteDocument(params.id);
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
