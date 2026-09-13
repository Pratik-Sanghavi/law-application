export const dynamic = "force-dynamic";

import { NextResponse } from "next/server";

export async function POST(req: Request) {
  const publicBaseUrl = process.env.APP_BASE_URL ?? new URL(req.url).origin;
  const response = NextResponse.redirect(new URL("/", publicBaseUrl));
  response.cookies.delete("access_token");
  response.cookies.delete("oidc_state");
  response.cookies.delete("pkce_verifier");
  return response;
}
