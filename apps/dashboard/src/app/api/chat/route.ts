import { NextRequest, NextResponse } from "next/server";
import { chatService } from "@/lib/services/chat";
import { ApiError } from "@/lib/api-client";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    if (body.stream !== false) {
      // Proxy streaming response
      const response = await chatService.sendMessageStream(body);
      return new NextResponse(response.body, {
        headers: {
          "Content-Type": "text/event-stream",
          "Cache-Control": "no-cache",
          Connection: "keep-alive",
        },
      });
    }

    const data = await chatService.sendMessage(body);
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
