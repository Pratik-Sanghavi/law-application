export const dynamic = "force-dynamic";
import { NextRequest, NextResponse } from "next/server";
export function GET(req: NextRequest) {
  const state = crypto.randomUUID();
  const u = new URL(
    `${process.env.OIDC_ISSUER_URL}/protocol/openid-connect/auth`,
  );
  u.searchParams.set("client_id", process.env.OIDC_CLIENT_ID!);
  u.searchParams.set("redirect_uri", `${process.env.APP_BASE_URL || req.nextUrl.origin}/api/auth/callback`);
  u.searchParams.set("response_type", "code");
  u.searchParams.set("scope", "openid profile email");
  u.searchParams.set("state", state);
  const r = NextResponse.redirect(u);
  r.cookies.set("oidc_state", state, { httpOnly: true, sameSite: "lax" });
  return r;
}
