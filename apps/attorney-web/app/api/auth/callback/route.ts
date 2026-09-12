export const dynamic = "force-dynamic";
import { NextRequest, NextResponse } from "next/server";
export async function GET(req: NextRequest) {
  if (
    req.nextUrl.searchParams.get("state") !==
    req.cookies.get("oidc_state")?.value
  )
    return new NextResponse("Invalid state", { status: 400 });
  const code = req.nextUrl.searchParams.get("code")!;
  const verifier = req.cookies.get("pkce_verifier")?.value;
  if (!verifier)
    return new NextResponse("Missing PKCE verifier", { status: 400 });
  const b = new URLSearchParams({
    grant_type: "authorization_code",
    code,
    redirect_uri: `${process.env.APP_BASE_URL || req.nextUrl.origin}/api/auth/callback`,
    client_id: process.env.OIDC_CLIENT_ID!,
    client_secret: process.env.OIDC_CLIENT_SECRET!,
    code_verifier: verifier,
  });
  const t = await fetch(
    `${process.env.OIDC_TOKEN_URL || process.env.OIDC_ISSUER_URL}/protocol/openid-connect/token`,
    { method: "POST", body: b },
  );
  if (!t.ok) return new NextResponse("Login failed", { status: 502 });
  const j = await t.json();
  const r = NextResponse.redirect(
    new URL("/", process.env.APP_BASE_URL || req.nextUrl.origin),
  );
  r.cookies.set("access_token", j.access_token, {
    httpOnly: true,
    sameSite: "lax",
    maxAge: j.expires_in,
  });
  return r;
}
