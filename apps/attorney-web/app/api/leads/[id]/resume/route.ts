export const dynamic = "force-dynamic";
import { NextRequest, NextResponse } from "next/server";
export async function GET(
  req: NextRequest,
  { params }: { params: { id: string } },
) {
  const token = req.cookies.get("access_token")?.value;
  if (!token) return new NextResponse("Unauthorized", { status: 401 });
  const result = await fetch(
    `${process.env.ATTORNEY_API_URL}/v1/leads/${params.id}/resume`,
    { headers: { Authorization: `Bearer ${token}` } },
  );
  return new NextResponse(await result.arrayBuffer(), {
    status: result.status,
    headers: {
      "Content-Type":
        result.headers.get("content-type") || "application/octet-stream",
      "Content-Disposition":
        result.headers.get("content-disposition") || "attachment",
    },
  });
}
