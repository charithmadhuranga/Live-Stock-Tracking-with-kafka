import { NextResponse } from "next/server";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function GET(
  request: Request,
  { params }: { params: Promise<{ beltId: string }> }
) {
  try {
    const { beltId } = await params;
    const { searchParams } = new URL(request.url);
    const hours = searchParams.get("hours") || "24";
    const res = await fetch(`${API_URL}/api/telemetry/${beltId}?hours=${hours}`);
    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch telemetry" }, { status: 500 });
  }
}