export const dynamic = "force-dynamic";
import { NextResponse } from "next/server";
export async function POST(req: Request) {
  const r = NextResponse.redirect(new URL("/", req.url));
  r.cookies.delete("access_token");
  r.cookies.delete("oidc_state");
  r.cookies.delete("pkce_verifier");
  return r;
}
