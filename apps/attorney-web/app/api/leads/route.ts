export const dynamic = "force-dynamic";

import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  const token = req.cookies.get("access_token")?.value;
  if (!token) return new NextResponse("Unauthorized", { status: 401 });

  const upstream = await fetch(`${process.env.ATTORNEY_API_URL}/v1/leads`, {
    headers: { Authorization: `Bearer ${token}` },
    cache: "no-store",
  });

  return new NextResponse(await upstream.text(), {
    status: upstream.status,
    headers: {
      "Content-Type": "application/json",
      "Cache-Control": "no-store, max-age=0, must-revalidate",
    },
  });
}
