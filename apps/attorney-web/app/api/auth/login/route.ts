export const dynamic = "force-dynamic";

import { NextRequest, NextResponse } from "next/server";

export async function GET(req: NextRequest) {
  const state = crypto.randomUUID();
  const verifier = `${crypto.randomUUID()}${crypto.randomUUID()}`;
  const digest = await crypto.subtle.digest(
    "SHA-256",
    new TextEncoder().encode(verifier),
  );
  const challenge = Buffer.from(digest).toString("base64url");
  const baseUrl = process.env.APP_BASE_URL || req.nextUrl.origin;
  const url = new URL(
    `${process.env.OIDC_ISSUER_URL}/protocol/openid-connect/auth`,
  );
  url.searchParams.set("client_id", process.env.OIDC_CLIENT_ID!);
  url.searchParams.set("redirect_uri", `${baseUrl}/api/auth/callback`);
  url.searchParams.set("response_type", "code");
  url.searchParams.set("scope", "openid profile email");
  url.searchParams.set("state", state);
  url.searchParams.set("code_challenge", challenge);
  url.searchParams.set("code_challenge_method", "S256");
  const response = NextResponse.redirect(url);
  response.cookies.set("oidc_state", state, {
    httpOnly: true,
    sameSite: "lax",
    secure: false,
    maxAge: 600,
  });
  response.cookies.set("pkce_verifier", verifier, {
    httpOnly: true,
    sameSite: "lax",
    secure: false,
    maxAge: 600,
  });
  return response;
}
