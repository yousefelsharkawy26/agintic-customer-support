import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({ error: "route_placeholder_under_test" }, { status: 500 });
}
